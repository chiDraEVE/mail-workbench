# Mail Workbench

A local, modular automation project for processing emails and extracting useful information from different sources.

## Motivation

My inbox contains a growing number of automated emails that require manual review. Job alerts from platforms such as LinkedIn, Indeed and the German Federal Employment Agency are a particular example.

Processing these emails manually involves several repetitive tasks:

- Extracting job listings and their URLs
- Identifying duplicate listings across different platforms
- Recognizing reposted or potentially outdated job advertisements
- Checking whether a listing is still available
- Collecting relevant information in a structured format
- Preparing listings for manual review and further processing

The goal of Mail Workbench is to automate the repetitive parts of this workflow while keeping important decisions under manual control.

## Goals

The project is intended to provide:

- **Email processing:** Read and parse locally available email data.
- **Structured storage:** Store extracted information in a relational database.
- **Duplicate detection:** Identify identical or similar listings across different sources.
- **Availability checks:** Collect information about whether a job listing is still accessible.
- **Reports:** Generate clear reports with links to the original listings.
- **Modularity:** Support different email-processing workflows through separate modules.

The initial focus is job advertisement processing. Additional modules may later handle security reports from NinjaFirewall and DMARC aggregate reports.

## Planned Architecture

The initial architecture is based on the following components:

| Component | Technology |
|---|---|
| Email processing | Python |
| Database | MySQL |
| Reporting | HTML |
| Version control | Git |
| Development environment | Ubuntu 24.04 / IntelliJ IDEA |

A web interface may be added later. The processing logic should remain independent of the presentation layer.

## Development Roadmap

### Phase 1 – Project foundation

- [x] Create project structure
- [x] Initialize Git repository
- [x] Configure local development environment
- [x] Connect MySQL database in IntelliJ IDEA
- [ ] Define project documentation and conventions
- [ ] Create initial database schema
- [ ] Set up Python environment and dependencies

### Phase 2 – Email import

- [ ] Inspect and understand the local email storage format
- [ ] Implement read-only email import
- [ ] Extract relevant metadata and URLs
- [ ] Store imported messages and extracted listings

### Phase 3 – Job listing analysis

- [ ] Normalize URLs
- [ ] Detect duplicate listings
- [ ] Compare titles, companies and descriptions
- [ ] Track when listings were first and last observed
- [ ] Collect availability information

### Phase 4 – Reporting

- [ ] Generate HTML reports
- [ ] Provide direct links to original job advertisements
- [ ] Highlight potential duplicates and unavailable listings
- [ ] Support manual classification and review

### Future ideas

- Web-based interface
- Integration with existing job application workflows
- NinjaFirewall report processing
- DMARC aggregate report processing
- Optional AI-assisted analysis

## Development Principles

This project is also a practical learning exercise. The implementation should therefore remain understandable, testable and maintainable.

The following principles guide development:

- Prefer small, incremental implementation steps.
- Keep modules loosely coupled.
- Write automated tests for important functionality.
- Document architectural decisions and relevant implementation details.
- Avoid unnecessary dependencies and complexity.
- Keep sensitive data and credentials outside version control.
- Never modify or delete original emails during import.
- Keep final job evaluation and application decisions under manual control.

## Status

<badge color="warning">Early development</badge>

The project is currently in its initial setup phase. No functional email-processing pipeline has been implemented yet.

Features and architectural decisions may change as development progresses.

## License

License not yet specified.