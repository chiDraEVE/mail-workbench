# Mail Workbench

<a id="top"></a>

**Sprachen:** [English](README.md) · Deutsch

## Inhalt

- [Motivation](#motivation)
- [Ziele](#ziele)
- [Geplante Architektur](#geplante-architektur)
- [Entwicklungsplan](#entwicklungsplan)
- [Entwicklungsgrundsätze](#entwicklungsgrundsätze)
- [Erste Schritte](#erste-schritte)
- [Tests](#tests)
- [E-Mail-Import](#e-mail-import)
- [Trello-Integration](#trello-integration)
- [Status](#status)
- [Lizenz](#lizenz)

**Dokumentation:** [Datenbank einrichten](docs/database.de.md) · [Database setup (EN)](docs/database.md) · [Tests](docs/testing.de.md) · [Testing (EN)](docs/testing.md) · [E-Mail-Import](docs/email-import.md) · [Email import (EN)](docs/email-import.en.md) · [Trello-Integration](docs/trello-integration.de.md) · [Trello integration (EN)](docs/trello-integration.md)

Ein lokales, modular aufgebautes Automatisierungsprojekt zur Verarbeitung von E-Mails und zum Extrahieren nützlicher Informationen aus verschiedenen Quellen.

## Motivation

Mein Posteingang enthält immer mehr automatisch erzeugte E-Mails, die manuell geprüft werden müssen. Jobbenachrichtigungen sind ein Beispiel dafür.

Die manuelle Verarbeitung umfasst mehrere wiederkehrende Aufgaben:

- Stellenanzeigen und ihre URLs extrahieren
- Doppelte Anzeigen auf verschiedenen Plattformen erkennen
- Erneut veröffentlichte oder möglicherweise veraltete Anzeigen erkennen
- Prüfen, ob eine Anzeige noch verfügbar ist
- Relevante Informationen strukturiert erfassen
- Anzeigen für die manuelle Prüfung und weitere Verarbeitung aufbereiten

Mail Workbench soll diese wiederkehrenden Aufgaben automatisieren und wichtige Entscheidungen weiterhin dem Menschen überlassen.

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Ziele

Das Projekt soll Folgendes ermöglichen:

- **E-Mail-Verarbeitung:** Lokal verfügbare E-Mail-Daten lesen und analysieren.
- **Strukturierte Speicherung:** Extrahierte Informationen in einer relationalen Datenbank speichern.
- **Duplikaterkennung:** Identische oder ähnliche Anzeigen aus verschiedenen Quellen erkennen.
- **Verfügbarkeitsprüfung:** Informationen dazu sammeln, ob eine Stellenanzeige noch erreichbar ist.
- **Berichte:** Übersichtliche Berichte mit Links zu den Originalanzeigen erzeugen.
- **Modularität:** Verschiedene E-Mail-Verarbeitungsabläufe in getrennten Modulen unterstützen.

Der Schwerpunkt liegt zunächst auf Stellenanzeigen. Später könnten weitere Module Sicherheitsberichte von NinjaFirewall und DMARC-Aggregatberichte verarbeiten.

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Geplante Architektur

Die erste Architektur basiert auf diesen Komponenten:

| Komponente | Technologie |
|---|---|
| E-Mail-Verarbeitung | Python |
| Datenbank | MySQL |
| Berichte | PHP / HTML |
| Versionsverwaltung | Git |
| Entwicklungsumgebung | Ubuntu 24.04 / IntelliJ IDEA |

Die aktuelle lokale PHP-Seite zeigt gespeicherte Jobs an und ermöglicht manuelle Korrekturen. Die Verarbeitungslogik bleibt unabhängig von der Darstellung.

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Entwicklungsplan

### Phase 1 – Projektgrundlage

- [x] Projektstruktur anlegen
- [x] Git-Repository initialisieren
- [x] Lokale Entwicklungsumgebung einrichten
- [x] MySQL-Datenbank in IntelliJ IDEA verbinden
- [x] Projektdokumentation und Konventionen festlegen
- [x] Erstes Datenbankschema erstellen
- [x] Python-Umgebung und Abhängigkeiten einrichten

### Phase 2 – E-Mail-Import

- [x] Lokales E-Mail-Speicherformat untersuchen
- [x] Schreibgeschützten Thunderbird-MBOX-Import implementieren
- [x] Nachrichten-Metadaten sowie Text- und HTML-Inhalte extrahieren
- [x] Importierte Nachrichten mit Duplikaterkennung und getrennten Statusangaben speichern
- [x] Stellenanzeigen und ihre URLs aus unterstützten E-Mail-Vorlagen extrahieren

### Phase 3 – Analyse von Stellenanzeigen

- [x] URLs normalisieren
- [x] Dieselbe Stellenveröffentlichung über ihre normalisierte URL wiedererkennen
- [x] Anzeigen mit übereinstimmender Stellenbezeichnung und Company zusammenführen
- [x] Erste und letzte Beobachtung einer Stellenveröffentlichung erfassen

### Phase 4 – Berichte

- [x] Eine Datenbank-Übersicht mit einem Eintrag pro Job und klickbaren Anzeigen-Links erzeugen
- [x] Betreff und Datum der zugehörigen E-Mails als Kontext anzeigen
- [x] Sortierung sowie Plattform- und Zeitfilter für die manuelle Prüfung ergänzen
- [x] Stellenbezeichnung, Unternehmen, Ort und Arbeitsmodell manuell bearbeiten können

### Phase 5 – Trello-Integration und optionale Anreicherung

- [x] Listen und Karten des konfigurierten Trello-Boards in der Übersicht anzeigen
- [x] API-Key, Token und Board-ID aus lokaler `.env` lesen und Listen-IDs dynamisch abrufen
- [ ] Manuell ausgewählte Anzeigen an Trello-Boards übergeben
- [ ] Optional Stellenbeschreibungen von Plattformseiten abrufen und plattformübergreifend vergleichen
- [ ] Optional Verfügbarkeit von Anzeigen prüfen

### Zukünftige Ideen

- Weboberfläche
- Integration in bestehende Bewerbungsabläufe
- Verarbeitung von NinjaFirewall-Berichten
- Verarbeitung von DMARC-Aggregatberichten
- Optionale KI-gestützte Analyse

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Trello-Integration

In Phase 5 sollen in der Übersicht ausgewählte Stellenanzeigen an Trello
übergeben werden. Die Anleitung beschreibt die API-Zugangsdaten, ihre
Erstellung, die relevanten Endpunkte und die geplante lokale Konfiguration:
[Trello-Integration](docs/trello-integration.de.md). Die [englische Fassung](docs/trello-integration.md)
ist ebenfalls verfügbar.

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Entwicklungsgrundsätze

Dieses Projekt dient auch als praktische Lernmöglichkeit. Die Implementierung soll daher verständlich, testbar und wartbar bleiben.

Für die Entwicklung gelten folgende Grundsätze:

- In kleinen, schrittweisen Änderungen arbeiten.
- Module möglichst lose koppeln.
- Wichtige Funktionen automatisiert testen.
- Architekturentscheidungen und relevante Implementierungsdetails dokumentieren.
- Unnötige Abhängigkeiten und Komplexität vermeiden.
- Vertrauliche Daten und Zugangsdaten aus der Versionsverwaltung heraushalten.
- Original-E-Mails beim Import niemals verändern oder löschen.
- Die abschließende Bewertung von Stellen und Bewerbungsentscheidungen dem Menschen überlassen.

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Erste Schritte

Das Projekt enthält einen schreibgeschützten Thunderbird-MBOX-Importer und eine MySQL-Datenbankschicht. Benötigt werden Python 3.10 oder neuer sowie ein erreichbarer, mit MySQL 8.0 kompatibler Server. Wenn du das Schema im Terminal einspielen möchtest, installiere außerdem den MySQL-Kommandozeilenclient.

1. Virtuelle Umgebung erstellen und aktivieren, dann Abhängigkeiten installieren:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   Führe Python-Befehle mit aktivierter virtueller Umgebung aus. So verwendet das Projekt das in `requirements.txt` unterstützte Paket `mysql-connector-python` statt eines älteren, systemweit installierten MySQL-Connectors. Dieser kann mit `AttributeError: module 'ssl' has no attribute 'wrap_socket'` scheitern.

2. Eine lokale Datenbank und einen Benutzer mit Zugriff darauf anlegen, zum Beispiel in einer administrativen MySQL-Sitzung:

   ```sql
   CREATE DATABASE `mail-workbench` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'mail-workbench'@'localhost' IDENTIFIED BY 'choose-a-local-password';
   GRANT ALL PRIVILEGES ON `mail-workbench`.* TO 'mail-workbench'@'localhost';
   ```

3. `.env.example` nach `.env` im Projektverzeichnis kopieren und `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` sowie `DB_PASSWORD` für deinen Server setzen. Git ignoriert `.env`; committe niemals echte Zugangsdaten.

4. Das Schema einspielen. Die Datenbank muss bereits existieren:

   ```bash
   mysql --host=localhost --user=mail-workbench --password mail-workbench < database/schema.sql
   ```

   Der Befehl fragt nach dem Passwort. Das Skript legt Tabellen an, aber weder die Datenbank noch den Datenbankbenutzer.

5. Den Verbindungshelfer aus Python verwenden:

   ```python
   from python.database import connect

   connection = connect()
   try:
       with connection.cursor() as cursor:
           cursor.execute("SELECT 1")
           print(cursor.fetchone())
   finally:
       connection.close()
   ```

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Tests

Die Unit-Tests mit dem Standard-Test-Runner ausführen:

```bash
python -m unittest discover -s tests -v
```

Der Integrationstest ist optional und verwendet die in `.env` konfigurierte Datenbank. Schema einspielen und anschließend ausführen:

```bash
RUN_DB_INTEGRATION=1 python -m unittest discover -s tests -v
```

Der Test führt nur eine schreibgeschützte Verbindungsabfrage aus und prüft, ob die erwarteten Tabellen vorhanden sind. Das destruktive Skript `database/drop-schema.sql` wird von Tests nicht verwendet. Führe es nur aus, wenn du Tabellen und Daten bewusst löschen willst.

Weitere Informationen: [Datenbank einrichten](docs/database.de.md) und [Tests](docs/testing.de.md).

<p align="right"><a href="#top">Nach oben ↑</a></p>

## E-Mail-Import

In `.env` `MAIL_SOURCE_TYPE=mbox`, `MAIL_SOURCE_PATH` und die erforderliche `JOB_SENDER_ALLOWLIST` setzen. Damit werden eine Thunderbird-MBOX-Datei und die exakten Absenderadressen festgelegt, deren Nachrichten importiert werden. Die Absenderliste liegt in der lokalen, von Git ignorierten `.env`-Datei und wird nicht in der Datenbank gespeichert.

Für eine neue Datenbank das aktuelle `database/schema.sql` wie unter [Datenbank einrichten](docs/database.de.md) beschrieben einspielen. Hat eine bestehende Datenbank noch die frühere E-Mail-Tabellenstruktur, stattdessen einmalig die Migration aus dem Projektverzeichnis anwenden:

```bash
mysql --host=localhost --user=mail-workbench --password mail-workbench < database/migrations/002_email_import.sql
```

Beide Skripte nicht auf dieselbe Datenbank anwenden. MySQL fragt nach dem Passwort. Danach den Import vom Projektverzeichnis aus starten:

```bash
python -m python.email_import.cli
```

Der Import verändert keine Mailboxdaten und archiviert oder löscht keine Nachrichten. Erkannte Stellenanzeigen werden mit ihrer Ursprungs-E-Mail verknüpft. Weitere Informationen zu Thunderbird, Filterung, Extraktion, Migration und Adaptern stehen in der [Dokumentation zum E-Mail-Import](docs/email-import.md).

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Status

<badge color="warning">Frühe Entwicklung</badge>

Das Projekt befindet sich in einer frühen Entwicklungsphase. Der lokale Thunderbird-Import, die Extraktion von Stellenanzeigen, die URL-Normalisierung, ein einfacher Abgleich gleicher URLs beziehungsweise gleicher Stellenbezeichnungen und Unternehmen, eine PHP-Übersicht mit klickbaren Links, Filtern und manueller Bearbeitung sowie die schreibgeschützte Anzeige der Trello-Listen und -Karten sind umgesetzt. Das Übertragen ausgewählter Jobs an Trello steht noch aus. Die Verknüpfung zu den Ursprungs-E-Mails ist in der Datenbank vorhanden.

Funktionen und Architekturentscheidungen können sich im weiteren Entwicklungsverlauf ändern.

<p align="right"><a href="#top">Nach oben ↑</a></p>

## Lizenz

Noch keine Lizenz festgelegt.

<p align="right"><a href="#top">Nach oben ↑</a></p>
