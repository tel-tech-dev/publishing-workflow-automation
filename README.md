# Publishing Workflow Automation

A Windows desktop automation toolkit written in Python for supporting a local publishing workflow.

The project combines a PySide2 control panel with separate processing modules for collecting article content, preparing issue folders, generating and updating Excel planning sheets, organizing images, and converting editorial documents from ODT to RTF.

## Main capabilities

- **Content collection** – batch and single-article scraping workflows using Selenium and BeautifulSoup.
- **Regional workflow** – processing content for multiple local sections / municipalities from one desktop interface.
- **Spreadsheet automation** – creation and population of Excel planning sheets used to organize issue content.
- **Image workflow** – collecting, selecting, copying and preparing images from source folders for publication.
- **Document processing** – ODT-to-RTF conversion, RTF validation and text extraction.
- **Process orchestration** – a PySide2 GUI starts individual Python workers as independent processes and reports their status.

## Project structure

```text
publishing-workflow-automation/
├── app/             # desktop GUI and orchestration
├── scrapers/        # article/content collection
├── spreadsheets/    # Excel planning-sheet automation
├── images/          # image collection and preparation
├── documents/       # ODT/RTF processing
├── docs/            # architecture and workflow notes
├── config.example.json
├── requirements.txt
└── .gitignore
```

## Technology

Python, PySide2, Selenium, BeautifulSoup, pandas, openpyxl, Pillow, requests and striprtf.

The ODT/RTF workflow also integrates with a locally installed OpenOffice installation on Windows.

## Status

This repository is a cleaned and reorganized version of a production-use personal automation toolkit. The original scripts evolved over time around a real editorial workflow; the public repository is being refactored to remove machine-specific paths and separate configuration from application logic.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `config.example.json` to `config.json` and adjust paths for the local machine.
4. Install OpenOffice if ODT-to-RTF conversion is required.
5. Configure a compatible Chrome / ChromeDriver setup for Selenium-based collection modules.

## Privacy and repository hygiene

Local publishing data, generated documents, images, browser profiles, cookies and machine-specific configuration are intentionally excluded from version control.

## Author

Adam Jagodzinski / TEL-TECH
