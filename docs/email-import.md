# E-Mail-Import

**Sprachen:** [English](email-import.en.md) · Deutsch · [Deutsche README](../README.de.md)

## Thunderbird-Quelle

Der Import nutzt `MAIL_SOURCE_TYPE=mbox` und `MAIL_SOURCE_PATH` aus `.env`.
Thunderbird speichert POP-Konten und „Lokale Ordner“ üblicherweise unter
`<Profil>/Mail/`, synchronisierte IMAP-Ordner unter `<Profil>/ImapMail/`.
Relevant sind die MBOX-Dateien mit dem jeweiligen Ordnernamen, oft ohne
Dateiendung. `.msf` enthält Indexdaten und wird ignoriert; `.sbd` ist ein
Verzeichnis für Unterordner und wird nicht selbst als Mailbox gelesen. Ein
IMAP-Ordner ist lokal importierbar, wenn Thunderbird ihn synchronisiert hat.
Siehe auch die [Mozilla-Hilfe zu lokalen Mail-Verzeichnissen](https://support.mozilla.org/en-US/kb/dangerous-directories-Thunderbird-account-settings).

Für eine stabile Momentaufnahme Thunderbird während eines Imports schließen
oder eine Profilkopie als Quelle verwenden. Der Adapter öffnet die MBOX nur
lesend; Mailbox-Dateien und E-Mails werden nicht verändert.

## Verarbeitung und Filter

`ImportSource` ist die gemeinsame Schnittstelle für Quellen. Der
`ThunderbirdMboxSource` liefert rohe Nachrichtenbytes; Parser, Absenderfilter,
Deduplizierung und Repository verwenden danach ausschließlich das gemeinsame
`EmailRecord`-Modell. Ein zukünftiger IMAP-Adapter kann dieselbe Schnittstelle
implementieren.

Nur exakte E-Mail-Absender aus der verpflichtenden `JOB_SENDER_ALLOWLIST`
werden importiert. Der Abgleich ignoriert Groß-/Kleinschreibung; Anzeigename
und Formatierung des `From`-Headers spielen keine Rolle. Die persönliche Liste
liegt in der lokalen `.env`-Datei, die Git ignoriert. Sie ist weder im Code
hinterlegt noch in der Datenbank gespeichert. Trage dort nur bestätigte
Job-Absender ein, da allgemeine Plattform- oder Recruiter-Absender auch
Bewerbungsupdates und andere Nachrichten umfassen können. Nicht gelistete
Nachrichten werden gezählt und übersprungen, aber nicht in der Datenbank
gespeichert.

Der tatsächliche Absender aus dem `From`-Header wird in
`email_messages.sender` gespeichert. Davon getrennt bezeichnet
`email_imports.source_type` den Importweg (derzeit `thunderbird_mbox`) und
`source_id` die Mailbox. Die Plattform einer später extrahierten Stellenanzeige
ist wiederum eine eigene Angabe in `job_publications.platform`. Eine Zuordnung
zu einem Extractor erfolgt anhand der Absenderdomain. Die persönliche
`JOB_SENDER_ALLOWLIST` bleibt davon getrennt in `.env`.

## Stellenanzeigen extrahieren

Nach dem E-Mail-Import verarbeitet der CLI-Lauf neue Nachrichten mit einem
passenden portal-spezifischen Extractor. Die erste Version unterstützt
Arbeitsagentur, Indeed, LinkedIn, XING, Stepstone, Instaffo, Stellenanzeigen.de
und Workwise. Sie speichert erkannte Stellen als `jobs` und `job_publications`
und verknüpft sie über `email_observations` mit der Ursprungs-E-Mail. Titel und
Link sind die Mindestfelder. Der Indeed-Extractor übernimmt zusätzlich Firma,
Ort und Beschreibung; weitere Metadaten können pro Portal ergänzt werden.

`email_processing.processing_status` wechselt danach auf `processed`, `no_jobs`,
`unsupported` oder `error`. Exakt gleiche Stellen-URLs werden wiederverwendet;
eine Normalisierung unterschiedlicher Tracking-Links ist noch nicht Teil
dieser Phase.

Extrahiert werden Message-ID, From, To/Cc/Bcc, Subject, der RFC-5322-Date-Wert
als UTC `DATETIME`, Text und HTML. Bei Multipart-Mails bleiben Text und HTML
separat erhalten; Attachments werden nicht gespeichert. Fehlt Message-ID,
Datum oder ein anderer Header, bleibt die Nachricht importierbar, sofern der
Absender zugelassen ist. Parserdefekte werden am Importdatensatz dokumentiert.
Eine Nachricht ohne ermittelbaren Absender wird übersprungen.

## Idempotenz und Zustände

Message-ID ist der primäre Deduplizierungsschlüssel; SHA-256 des normalisierten
RFC-Nachrichteninhalts ist der zusätzliche eindeutige Schlüssel. Der Hash
ermöglicht Deduplizierung auch bei fehlender Message-ID. `email_imports` hält
Quellbezug, Importstatus und Fehler fest. `email_processing` speichert separat
den Verarbeitungsstatus. Es gibt in dieser Phase keine Archivierungs- oder
Löschlogik und keine Postfachaktionen.

## Schema aktualisieren

Für eine neue Datenbank ausschließlich die aktuelle `database/schema.sql`
ausführen. Sie bildet den vollständigen aktuellen Tabellenstand ab.

Nur wenn eine bestehende Datenbank noch die frühere E-Mail-Tabellenstruktur
hat, stattdessen die Migration `002_email_import.sql` einmalig gemäß den
[Befehlen in der README](../README.md#e-mail-import) anwenden. Die Migration
bleibt als Upgrade-Pfad erhalten; sie wird nicht zusätzlich auf eine neue
Datenbank angewendet. Ein separates Ursprungsschema ist nicht nötig, weil die
Migrationsdateien die Änderungen für bestehende Installationen dokumentieren.

## Import ausführen

In `.env` setzen:

```dotenv
MAIL_SOURCE_TYPE=mbox
MAIL_SOURCE_PATH=/path/to/Thunderbird/Profile/ImapMail/account/INBOX
JOB_SENDER_ALLOWLIST=job-alerts@example.invalid,another-alert@example.invalid
```

`JOB_SENDER_ALLOWLIST` ist erforderlich und enthält eine kommaseparierte Liste
exakter Absenderadressen. Ohne gültige Liste bricht der Import mit einer
verständlichen Fehlermeldung ab.
Nach Datenbankeinrichtung und Installation der Abhängigkeiten den Import mit dem
Befehl im Abschnitt [E-Mail-Import der README](../README.md#e-mail-import)
starten. Shell-Befehle im Projekt sind dort gesammelt und vom Repository-Root
aus ausführbar.

Die Ausgabe enthält nur Zähler (gescannt, gefiltert, importiert, Duplikate,
Fehler/Warnungen). Jeder Datensatz wird einzeln committed, sodass ein späterer
Lauf bereits erfolgreich importierte Nachrichten überspringt.
