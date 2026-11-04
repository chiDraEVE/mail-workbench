# Email import

**Languages:** English · [Deutsch](email-import.md) · [German README](../README.de.md)

## Thunderbird source

The importer reads `MAIL_SOURCE_TYPE=mbox` and `MAIL_SOURCE_PATH` from `.env`.
Thunderbird usually stores POP accounts and Local Folders under
`<profile>/Mail/`, and synchronized IMAP folders under `<profile>/ImapMail/`.
Relevant MBOX files often have the folder name without a file extension. `.msf`
files contain index data and are ignored; `.sbd` directories hold subfolders
and are not mailbox files themselves. An IMAP folder can be imported locally
if Thunderbird has synchronized it.

For a stable snapshot, close Thunderbird during an import or use a copy of the
profile. The adapter opens the MBOX read-only; it does not modify mailbox files
or messages.

## Processing and filtering

`ImportSource` is the common interface for sources. `ThunderbirdMboxSource`
provides raw message bytes; parsing, sender filtering, deduplication, and
storage then use the shared `EmailRecord` model. A future IMAP adapter can
implement the same interface.

Only exact sender addresses in the required `JOB_SENDER_ALLOWLIST` are
imported. Matching is case-insensitive; the display name and formatting of the
`From` header do not matter. Keep this personal list in the local `.env` file,
which Git ignores. It is neither hardcoded nor stored in the database. Add only
confirmed job alert senders, since general platform or recruiter addresses may
also be used for application updates and unrelated messages. Messages from
unlisted senders are counted and skipped without being stored in the database.

The importer extracts Message-ID, From, To/Cc/Bcc, Subject, the RFC 5322 date
as a UTC `DATETIME`, and text and HTML bodies. Text and HTML remain separate
for multipart messages; attachments are not stored. A message can still be
imported when Message-ID, date, or another header is missing, provided its
sender is allowed. Parser failures are recorded on the import record. Messages
without a detectable sender are skipped.

## Idempotency and status

Message-ID is the primary deduplication key; SHA-256 of the normalized RFC
message content is an additional unique key. The hash also enables
deduplication when Message-ID is missing. `email_imports` stores source
references, import status, and errors. `email_processing` separately stores
processing status. This phase has no archive or delete logic and performs no
mailbox actions.

## Updating the schema

For a new database, apply only the current `database/schema.sql`. It defines
the complete current table layout.

Only if an existing database still has the earlier email table structure,
apply migration `002_email_import.sql` once, following the commands in the
[README](../README.md#e-mail-import). Keep the migration as an upgrade path;
do not also apply it to a new database. A separate original schema is not
needed because the migration files document changes for existing installs.

## Running the importer

Set these values in `.env`:

```dotenv
MAIL_SOURCE_TYPE=mbox
MAIL_SOURCE_PATH=/path/to/Thunderbird/Profile/ImapMail/account/INBOX
JOB_SENDER_ALLOWLIST=job-alerts@example.invalid,another-alert@example.invalid
```

`JOB_SENDER_ALLOWLIST` is required and contains a comma-separated list of
exact sender addresses. If the list is missing or empty, the importer exits
with a clear error.

After setting up the database and installing dependencies, run the importer
from the repository root:

```bash
python -m python.email_import.cli
```

The output contains only counts (scanned, filtered, imported, duplicates, and
errors or warnings). Each record is committed individually, so a later run
skips messages that were already imported successfully.
