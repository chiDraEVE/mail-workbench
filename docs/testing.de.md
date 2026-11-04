# Tests

**Sprachen:** [English](testing.md) · Deutsch · [Deutsche README](../README.de.md)

Die Tests verwenden Pythons eingebauten `unittest`-Runner; ein zusätzliches
Testframework ist nicht erforderlich. Installiere die Projektabhängigkeiten
und führe die Unit-Tests mit den Befehlen aus den README-Abschnitten
[Erste Schritte](../README.de.md#erste-schritte) und [Tests](../README.de.md#tests)
aus. Führe Shell-Befehle im Projektverzeichnis und mit aktivierter virtueller
Umgebung aus.

Unit-Tests prüfen die Verbindungskonfiguration, den exakten Absenderabgleich,
die MIME-Extraktion, fehlerhafte Metadaten und den schreibgeschützten
Thunderbird-MBOX-Adapter. Die Beispieldateien in `tests/fixtures/` sind
synthetisch und verwenden reservierte `.invalid`-Adressen; sie enthalten keine
echten Mailboxdaten.

## Integrationstest

Integrationstests werden übersprungen, sofern `RUN_DB_INTEGRATION=1` nicht
gesetzt ist. Sie prüfen das Schema und importieren die anonymisierte
Beispiel-Mailbox in MySQL. Dabei werden Absenderfilter und ein wiederholter
Import geprüft. Der Importtest löscht nur die von ihm angelegten Datensätze.

Für eine neue Datenbank die aktuelle `database/schema.sql` einspielen. Die
Migration `002_email_import.sql` nur für ein Upgrade einer Datenbank mit der
früheren E-Mail-Struktur verwenden; beide Skripte nicht auf dieselbe Datenbank
anwenden. Danach den im [README](../README.de.md#tests) beschriebenen
Integrationstest vom Projektverzeichnis aus starten.

Die konfigurierte Datenbank sollte ausschließlich für Entwicklung oder Tests
verwendet werden. Der Integrationstest führt `database/drop-schema.sql` nie
aus und liest niemals die konfigurierte echte Thunderbird-Mailbox.
