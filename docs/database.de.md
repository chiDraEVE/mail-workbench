# Datenbank einrichten

**Sprachen:** [English](database.md) · Deutsch · [Deutsche README](../README.de.md)

Mail Workbench verwendet MySQL und die Tabellen aus
[`../database/schema.sql`](../database/schema.sql). Benötigt werden Python
3.10 oder neuer, ein mit MySQL 8.0 kompatibler Server und die Abhängigkeiten
aus [`../requirements.txt`](../requirements.txt).

## Zugangsdaten konfigurieren

`.env.example` im Projektverzeichnis nach `.env` kopieren und folgende Werte
setzen:

| Variable | Erforderlich | Standardwert | Zweck |
|---|---|---|---|
| `DB_NAME` | Ja | — | Name der vorhandenen Datenbank |
| `DB_USER` | Ja | — | MySQL-Benutzer |
| `DB_PASSWORD` | Ja | — | Passwort des Benutzers |
| `DB_HOST` | Nein | `localhost` | Host des MySQL-Servers |
| `DB_PORT` | Nein | `3306` | Port des MySQL-Servers |

Bereits exportierte Umgebungsvariablen haben Vorrang vor Werten in `.env`.
Behandle `.env` vertraulich; Git ignoriert die Datei.

## Datenbank erstellen und Schema einspielen

Eine leere Datenbank und einen Benutzer mit Zugriff darauf anlegen. Danach
den Anweisungen unter [Erste Schritte](../README.de.md#erste-schritte) folgen,
um das Schema einzuspielen. Shell-Befehle im Projekt vom Projektverzeichnis
ausführen; der MySQL-Client fragt nach dem Passwort. Das Schema legt Tabellen
in der ausgewählten Datenbank an, aber nicht die Datenbank selbst. Ein zweiter
Aufruf schlägt fehl, wenn die Tabellen bereits existieren.

## Aus Python verbinden

```python
from python.database import connect

connection = connect()
try:
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1")
        print(cursor.fetchone())
    finally:
        cursor.close()
finally:
    connection.close()
```

`connect()` löst einen `RuntimeError` mit den Namen fehlender Pflichtwerte aus.
Zugangsdaten werden weder protokolliert noch in Fehlermeldungen ausgegeben.
Schließe Cursor und Verbindungen nach der Verwendung.

## Lokale Job-Übersicht

Die `index.php` im Projektverzeichnis verwendet dieselben Einstellungen
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` und `DB_PASSWORD`. Von Apache
gesetzte Umgebungsvariablen haben Vorrang. PHP kann `.env` nur als Ersatz
verwenden, wenn der Webserver-Benutzer die Datei lesen darf. Die Übersicht
zeigt Jobs und ihre Ursprungslinks, bietet Sortierung sowie Plattform- und
Zeitfilter und ermöglicht manuelle Korrekturen an Titel, Unternehmen, Ort und
Arbeitsmodell. Diese Änderungen aktualisieren die vorhandenen Zeilen in
`jobs` und `companies`.

Anzeigenspezifische URLs, Plattformen und externe IDs liegen in
`job_publications`. Die externe ID wird beim Verarbeiten einer E-Mail aus einem
bekannten URL-Parameter (bei Indeed zum Beispiel `jk`) oder, falls keiner
vorhanden ist, aus dem letzten URL-Pfadbestandteil abgeleitet.

`database/drop-schema.sql` löscht alle Projekttabellen und deren Inhalte. Das
Skript ist destruktiv; verwende es nur, wenn du geprüft hast, dass die
ausgewählte Datenbank die richtige Entwicklungsdatenbank ist.

Wenn du nur die Daten löschen und das Schema behalten möchtest, verwende
[`../database/clear-data.sql`](../database/clear-data.sql). Das Skript zeigt
zuerst die ausgewählte Datenbank an und löscht anschließend alle E-Mail-, Job-
und Firmendaten. Prüfe den Datenbanknamen vor dem Ausführen. Danach ist kein
erneutes Einspielen von `schema.sql` nötig.
