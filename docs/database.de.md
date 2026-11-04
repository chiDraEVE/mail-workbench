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

`database/drop-schema.sql` löscht alle Projekttabellen und deren Inhalte. Das
Skript ist destruktiv; verwende es nur, wenn du geprüft hast, dass die
ausgewählte Datenbank die richtige Entwicklungsdatenbank ist.
