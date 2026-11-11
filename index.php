<?php
declare(strict_types=1);

/**
 * Small local entry point for Mail Workbench.
 *
 * Apache/PHP environment variables take precedence. The project .env file is
 * used as a fallback when it is readable by the PHP process.
 */
$localSettings = [];
$envFile = __DIR__ . '/.env';

if (is_readable($envFile)) {
    $parsedSettings = @parse_ini_file($envFile, false, INI_SCANNER_RAW);
    if (is_array($parsedSettings)) {
        $localSettings = $parsedSettings;
    }
}

$setting = static function (string $name, ?string $default = null) use ($localSettings): ?string {
    $environmentValue = getenv($name);
    if ($environmentValue !== false) {
        return $environmentValue;
    }

    $localValue = $localSettings[$name] ?? $default;
    return is_string($localValue) ? $localValue : $default;
};

$databaseHost = $setting('DB_HOST', 'localhost');
$databasePort = $setting('DB_PORT', '3306');
$databaseName = $setting('DB_NAME');
$databaseUser = $setting('DB_USER');
$databasePassword = $setting('DB_PASSWORD');

$missingSettings = [];
foreach (['DB_NAME' => $databaseName, 'DB_USER' => $databaseUser, 'DB_PASSWORD' => $databasePassword] as $name => $value) {
    if ($value === null || trim($value) === '') {
        $missingSettings[] = $name;
    }
}

$databaseConnected = false;
$pageError = null;
$jobs = [];
$publicationsByJob = [];
$totalJobs = 0;
$pageNumber = filter_input(INPUT_GET, 'page', FILTER_VALIDATE_INT);
$pageNumber = max(1, $pageNumber === false || $pageNumber === null ? 1 : $pageNumber);
$platform = $_GET['platform'] ?? '';
$platform = is_string($platform) ? $platform : '';
$period = $_GET['period'] ?? 'all';
$period = is_string($period) && in_array($period, ['all', '1', '3', '6'], true) ? $period : 'all';
$sort = $_GET['sort'] ?? 'recent';
$sort = is_string($sort) ? $sort : 'recent';
$sortOrders = [
    'recent' => 'MAX(p.last_seen_at) DESC, j.id DESC',
    'oldest' => 'MAX(p.last_seen_at) ASC, j.id ASC',
    'title' => 'j.title ASC, j.id DESC',
    'company' => 'COALESCE(c.name, \'\') ASC, j.title ASC, j.id DESC',
];
if (!array_key_exists($sort, $sortOrders)) {
    $sort = 'recent';
}
$pageSize = 50;
$pageCount = 1;

if ($missingSettings !== []) {
    http_response_code(503);
    $pageError = 'Datenbank-Einstellungen fehlen: ' . implode(', ', $missingSettings) . '.';
} else {
    try {
        $dsn = sprintf(
            'mysql:host=%s;port=%s;dbname=%s;charset=utf8mb4',
            $databaseHost,
            $databasePort,
            $databaseName
        );
        $connection = new PDO($dsn, $databaseUser, $databasePassword, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        $connection->query('SELECT 1');
        $databaseConnected = true;

        if ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'save_job') {
            $jobId = filter_input(INPUT_POST, 'job_id', FILTER_VALIDATE_INT);
            $title = trim((string) ($_POST['title'] ?? ''));
            $companyName = trim((string) ($_POST['company'] ?? ''));
            $location = trim((string) ($_POST['location'] ?? ''));
            $workMode = trim((string) ($_POST['work_mode'] ?? ''));
            if (!$jobId || $title === '') {
                throw new RuntimeException('Titel und gültige Job-ID werden benötigt.');
            }
            $connection->beginTransaction();
            $companyId = null;
            if ($companyName !== '') {
                $normalizedName = function_exists('mb_strtolower')
                    ? mb_strtolower(preg_replace('/\\s+/', ' ', $companyName))
                    : strtolower(preg_replace('/\\s+/', ' ', $companyName));
                $companyLookup = $connection->prepare('SELECT id FROM companies WHERE normalized_name=:name ORDER BY id LIMIT 1');
                $companyLookup->execute([':name' => $normalizedName]);
                $companyId = $companyLookup->fetchColumn();
                if ($companyId === false) {
                    $insertCompany = $connection->prepare('INSERT INTO companies (name, normalized_name) VALUES (:name, :normalized)');
                    $insertCompany->execute([':name' => $companyName, ':normalized' => $normalizedName]);
                    $companyId = (int) $connection->lastInsertId();
                }
            }
            $updateJob = $connection->prepare(
                'UPDATE jobs SET title=:title, employer_company_id=:company, location=:location, work_mode=:mode WHERE id=:id'
            );
            $updateJob->execute([
                ':title' => $title, ':company' => $companyId,
                ':location' => $location !== '' ? $location : null,
                ':mode' => $workMode !== '' ? $workMode : null, ':id' => $jobId,
            ]);
            $connection->commit();
            $query = http_build_query(['sort' => $sort, 'platform' => $platform, 'period' => $period, 'page' => $pageNumber]);
            header('Location: ?' . $query);
            exit;
        }

        $availablePlatforms = $connection->query('SELECT DISTINCT platform FROM job_publications ORDER BY platform')->fetchAll(PDO::FETCH_COLUMN);
        $where = [];
        $filterParameters = [];
        if ($platform !== '') {
            $where[] = 'EXISTS (SELECT 1 FROM job_publications fp WHERE fp.job_id=j.id AND fp.platform=:platform)';
            $filterParameters[':platform'] = $platform;
        }
        if ($period !== 'all') {
            $where[] = 'EXISTS (SELECT 1 FROM job_publications fp JOIN email_observations fo ON fo.publication_id=fp.id JOIN email_messages fm ON fm.id=fo.email_id WHERE fp.job_id=j.id AND fm.received_at >= DATE_SUB(CURRENT_TIMESTAMP, INTERVAL ' . (int) $period . ' MONTH))';
        }
        $whereSql = $where ? ' WHERE ' . implode(' AND ', $where) : '';

        $countStatement = $connection->prepare('SELECT COUNT(*) FROM jobs AS j' . $whereSql);
        $countStatement->execute($filterParameters);
        $totalJobs = (int) $countStatement->fetchColumn();
        $pageCount = max(1, (int) ceil($totalJobs / $pageSize));
        $pageNumber = min($pageNumber, $pageCount);
        $offset = ($pageNumber - 1) * $pageSize;

        $jobsSql = <<<'SQL'
        SELECT j.id, j.title, c.name AS company_name, j.location, j.work_mode,
               MIN(p.first_seen_at) AS first_seen_at,
               MAX(p.last_seen_at) AS last_seen_at,
               COUNT(DISTINCT p.id) AS publication_count
        FROM jobs AS j
        LEFT JOIN companies AS c ON c.id=j.employer_company_id
        LEFT JOIN job_publications AS p ON p.job_id=j.id
        __WHERE__
        GROUP BY j.id, j.title, c.name, j.location, j.work_mode
        ORDER BY __ORDER_BY__
        LIMIT :limit OFFSET :offset
        SQL;
        $jobsSql = str_replace(['__ORDER_BY__', '__WHERE__'], [$sortOrders[$sort], $whereSql], $jobsSql);
        $jobsStatement = $connection->prepare($jobsSql);
        foreach ($filterParameters as $name => $value) {
            $jobsStatement->bindValue($name, $value);
        }
        $jobsStatement->bindValue(':limit', $pageSize, PDO::PARAM_INT);
        $jobsStatement->bindValue(':offset', $offset, PDO::PARAM_INT);
        $jobsStatement->execute();
        $jobs = $jobsStatement->fetchAll();

        if ($jobs !== []) {
            $jobParameters = [];
            $placeholders = [];
            foreach ($jobs as $index => $job) {
                $placeholder = ':job' . $index;
                $placeholders[] = $placeholder;
                $jobParameters[$placeholder] = (int) $job['id'];
            }

            $publicationStatement = $connection->prepare(
                'SELECT p.job_id, p.platform, p.external_id, p.url, p.last_seen_at,
                        (SELECT COUNT(*) FROM email_observations AS o
                         WHERE o.publication_id=p.id) AS email_count,
                        (SELECT m.subject FROM email_observations AS o
                         JOIN email_messages AS m ON m.id=o.email_id
                         WHERE o.publication_id=p.id
                         ORDER BY m.received_at DESC, m.id DESC LIMIT 1) AS latest_email_subject,
                        (SELECT m.received_at FROM email_observations AS o
                         JOIN email_messages AS m ON m.id=o.email_id
                         WHERE o.publication_id=p.id
                         ORDER BY m.received_at DESC, m.id DESC LIMIT 1) AS latest_email_date
                 FROM job_publications AS p
                 WHERE p.job_id IN (' . implode(', ', $placeholders) . ')
                 ORDER BY p.job_id, p.last_seen_at DESC'
            );
            $publicationStatement->execute($jobParameters);
            foreach ($publicationStatement->fetchAll() as $publication) {
                $publicationsByJob[(int) $publication['job_id']][] = $publication;
            }
        }
    } catch (PDOException $exception) {
        http_response_code(503);
        error_log('Mail Workbench database connection failed: ' . $exception->getMessage());
        $pageError = $databaseConnected
            ? 'Die Job-Übersicht konnte nicht geladen werden. Prüfe das PHP- oder Apache-Fehlerprotokoll.'
            : 'Keine Datenbankverbindung. Prüfe das PHP- oder Apache-Fehlerprotokoll.';
        $databaseConnected = false;
    }
}

function escape(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
?>
<!doctype html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mail Workbench</title>
    <style>
        :root { color-scheme: light dark; font-family: system-ui, sans-serif; }
        body { max-width: 70rem; margin: 3rem auto; padding: 0 1.25rem; line-height: 1.55; }
        .status, .job { padding: 1rem; border: 1px solid color-mix(in srgb, currentColor 30%, transparent); border-radius: .5rem; }
        .job { margin: 1rem 0; }
        .job h2 { margin: 0 0 .4rem; font-size: 1.2rem; }
        .job-meta, .publication-meta { color: GrayText; }
        .publication { margin-top: .75rem; }
        .publication-meta { font-size: .9rem; }
        nav, .pagination { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 1.5rem; }
        .sort-form { display: flex; flex-wrap: wrap; align-items: center; gap: .75rem; }
        .edit-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: .65rem; margin-top: 1rem; }
        .edit-form label { display: grid; gap: .2rem; }
        input, select, button { font: inherit; padding: .35rem; }
        .pagination { justify-content: space-between; }
    </style>
</head>
<body>
    <main>
        <h1>Mail Workbench</h1>
        <?php if (!$databaseConnected): ?>
            <p class="status" role="status"><?= escape($pageError ?? 'Datenbankverbindung nicht verfügbar.') ?></p>
        <?php endif; ?>

        <nav aria-label="Projektdokumentation">
            <a href="README.de.md">README (Deutsch)</a>
            <a href="README.md">README (English)</a>
            <a href="docs/database.de.md">Datenbank einrichten</a>
            <a href="docs/database.md">Database setup</a>
        </nav>

        <?php if ($databaseConnected): ?>
            <section aria-labelledby="jobs-heading">
                <h2 id="jobs-heading">Stellenanzeigen</h2>
                <p><?= number_format($totalJobs, 0, ',', '.') ?> Jobs in der Datenbank</p>
                <form class="sort-form" method="get">
                    <label for="platform">Plattform</label>
                    <select id="platform" name="platform">
                        <option value="">Alle Plattformen</option>
                        <?php foreach ($availablePlatforms as $availablePlatform): ?>
                            <option value="<?= escape($availablePlatform) ?>" <?= $platform === $availablePlatform ? 'selected' : '' ?>><?= escape($availablePlatform) ?></option>
                        <?php endforeach; ?>
                    </select>
                    <label for="period">Zeitraum</label>
                    <select id="period" name="period">
                        <option value="all" <?= $period === 'all' ? 'selected' : '' ?>>Gesamter Zeitraum</option>
                        <option value="1" <?= $period === '1' ? 'selected' : '' ?>>Letzter Monat</option>
                        <option value="3" <?= $period === '3' ? 'selected' : '' ?>>Letzte 3 Monate</option>
                        <option value="6" <?= $period === '6' ? 'selected' : '' ?>>Letzte 6 Monate</option>
                    </select>
                    <label for="sort">Sortieren nach</label>
                    <select id="sort" name="sort">
                        <option value="recent" <?= $sort === 'recent' ? 'selected' : '' ?>>Neueste zuerst</option>
                        <option value="oldest" <?= $sort === 'oldest' ? 'selected' : '' ?>>Älteste zuerst</option>
                        <option value="title" <?= $sort === 'title' ? 'selected' : '' ?>>Titel A–Z</option>
                        <option value="company" <?= $sort === 'company' ? 'selected' : '' ?>>Company A–Z</option>
                    </select>
                    <button type="submit">Anwenden</button>
                </form>

                <?php if ($jobs === []): ?>
                    <p>Noch keine Jobs vorhanden.</p>
                <?php else: ?>
                    <?php foreach ($jobs as $job): ?>
                        <article class="job">
                            <h2><?= escape($job['title']) ?></h2>
                            <p class="job-meta">
                                <?= escape($job['company_name'] ?: 'Unternehmen unbekannt') ?>
                                <?php if ($job['location']): ?> · <?= escape($job['location']) ?><?php endif; ?>
                                <?php if ($job['work_mode']): ?> · <?= escape($job['work_mode']) ?><?php endif; ?>
                            </p>

                            <details>
                                <summary>Jobdaten bearbeiten</summary>
                                <form class="edit-form" method="post">
                                    <input type="hidden" name="action" value="save_job">
                                    <input type="hidden" name="job_id" value="<?= (int) $job['id'] ?>">
                                    <label>Titel<input name="title" maxlength="500" required value="<?= escape($job['title']) ?>"></label>
                                    <label>Unternehmen<input name="company" maxlength="255" value="<?= escape($job['company_name'] ?? '') ?>"></label>
                                    <label>Ort<input name="location" maxlength="255" value="<?= escape($job['location'] ?? '') ?>"></label>
                                    <label>Arbeitsmodell<input name="work_mode" maxlength="50" value="<?= escape($job['work_mode'] ?? '') ?>" placeholder="Remote, Hybrid, Vor Ort"></label>
                                    <button type="submit">Speichern</button>
                                </form>
                            </details>
                            <p class="job-meta">
                                Beobachtet: <?= escape($job['first_seen_at'] ?: 'unbekannt') ?>
                                bis <?= escape($job['last_seen_at'] ?: 'unbekannt') ?>
                                · <?= (int) $job['publication_count'] ?>
                                <?= (int) $job['publication_count'] === 1 ? 'Anzeigen-Link' : 'Anzeigen-Links' ?>
                            </p>

                            <?php foreach ($publicationsByJob[(int) $job['id']] ?? [] as $publication): ?>
                                <?php
                                $urlParts = parse_url($publication['url']);
                                $safeUrl = is_array($urlParts)
                                    && in_array(strtolower($urlParts['scheme'] ?? ''), ['http', 'https'], true);
                                $emailCount = (int) $publication['email_count'];
                                ?>
                                <div class="publication">
                                    <?php if ($safeUrl): ?>
                                        <a href="<?= escape($publication['url']) ?>" target="_blank" rel="noopener noreferrer"
                                           aria-label="<?= escape($publication['platform']) ?>: Stellenanzeige öffnen">
                                            <?= escape($publication['platform']) ?> ↗
                                        </a>
                                        <?php if ($publication['external_id']): ?>
                                            <span class="publication-meta">· ID <?= escape($publication['external_id']) ?></span>
                                        <?php endif; ?>
                                    <?php else: ?>
                                        <span><?= escape($publication['platform']) ?> – ungültiger Link</span>
                                    <?php endif; ?>
                                    <div class="publication-meta">
                                        <?php if ($publication['latest_email_date']): ?>
                                            E-Mail vom <?= escape($publication['latest_email_date']) ?>
                                            <?php if ($publication['latest_email_subject']): ?>
                                                · <?= escape($publication['latest_email_subject']) ?>
                                            <?php endif; ?>
                                            <?php if ($emailCount > 1): ?>
                                                · In <?= $emailCount ?> E-Mails erhalten
                                            <?php endif; ?>
                                        <?php else: ?>
                                            Keine verknüpfte E-Mail
                                        <?php endif; ?>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </article>
                    <?php endforeach; ?>

                    <?php if ($pageCount > 1): ?>
                        <nav class="pagination" aria-label="Seitennavigation">
                            <?php if ($pageNumber > 1): ?>
                                <a href="?page=<?= $pageNumber - 1 ?>&amp;sort=<?= escape($sort) ?>&amp;platform=<?= escape($platform) ?>&amp;period=<?= escape($period) ?>">← Vorherige Seite</a>
                            <?php else: ?>
                                <span></span>
                            <?php endif; ?>
                            <span>Seite <?= $pageNumber ?> von <?= $pageCount ?></span>
                            <?php if ($pageNumber < $pageCount): ?>
                                <a href="?page=<?= $pageNumber + 1 ?>&amp;sort=<?= escape($sort) ?>&amp;platform=<?= escape($platform) ?>&amp;period=<?= escape($period) ?>">Nächste Seite →</a>
                            <?php endif; ?>
                        </nav>
                    <?php endif; ?>
                <?php endif; ?>
            </section>
        <?php endif; ?>
    </main>
</body>
</html>
