# Publishing Workflow Automation

A Python desktop application that coordinates a multi-step local publishing workflow: article collection, spreadsheet preparation, image handling, and document conversion.

This repository is a cleaned and portable public version of a real internal workflow tool. Machine-specific paths, credentials, private data, and environment-specific settings have been removed or moved to configuration.

## What the project does

The application acts as a desktop control panel for several independent Python modules used during preparation of a local publication.

Main workflow areas include:

- collecting article content in batch or one article at a time,
- processing content for multiple regional sections,
- creating issue folders and preparing spreadsheet-based schedules,
- filling schedules with article data,
- collecting and organizing source images,
- preparing images for further processing,
- restoring processed images to the publication workflow,
- converting ODT documents to RTF,
- validating and extracting content from RTF files,
- launching individual workflow modules from a PySide2 desktop interface.

## Architecture

The project is split into small modules grouped by responsibility:

```text
publishing-workflow-automation/
├── app/
│   └── main.py
├── common/
│   ├── __init__.py
│   └── config.py
├── scrapers/
│   ├── article_scraper.py
│   ├── article_scraper_continuation.py
│   └── single_article_scraper.py
├── spreadsheets/
│   ├── create_issue_folder.py
│   ├── fill_schedule_single.py
│   ├── fill_schedules.py
│   └── fill_schedules_continuation.py
├── images/
│   ├── collect_source_photos.py
│   ├── prepare_photos_for_processing.py
│   ├── rename_photos.py
│   └── restore_processed_photos.py
├── documents/
│   ├── odt_to_rtf.py
│   └── rtf_check.py
├── tests/
│   └── test_config_example.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── MIGRATION.md
│   └── SECURITY.md
├── config.example.json
├── requirements.txt
└── README.md
```

The GUI launcher starts individual modules as separate processes. This keeps the workflow modular and allows individual tools to be executed or developed independently.

## Technology

- Python
- PySide2
- subprocess / QProcess based module orchestration
- file and directory processing
- web-content processing
- spreadsheet workflow automation
- OpenOffice-based ODT to RTF conversion
- JSON configuration
- Git / GitHub

## Configuration

The original application contained workstation-specific paths. The public version uses configuration instead.

Copy:

```text
config.example.json
```

to:

```text
config.json
```

and adjust the paths for your environment.

`config.json` is intentionally excluded from Git so local configuration is not committed.

## Installation

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Copy and edit the configuration file:

```powershell
Copy-Item config.example.json config.json
```

Run the application:

```powershell
python app/main.py
```

Some document-conversion functionality requires a local OpenOffice installation.

## Security

The public repository does not contain production credentials, API keys, passwords, private publishing data, or workstation-specific user paths.

See:

```text
docs/SECURITY.md
```

for additional notes.

## Background

The project evolved from a collection of separate Python utilities used to automate repetitive editorial and publishing operations. The current structure consolidates those tools into a clearer modular application with shared configuration and documentation.

The goal of this public version is to demonstrate practical Python automation, process orchestration, file processing, workflow design, and maintenance of a multi-module desktop application.

## Development

Example Git workflow used for this repository:

```powershell
git switch -c feature-name
git add .
git commit -m "Describe the change"
git switch main
git merge feature-name
git push
```

## License

This repository is provided as a portfolio and demonstration project. Third-party content, private publication data, credentials, and proprietary templates are not included.
