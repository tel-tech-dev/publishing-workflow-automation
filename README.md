# Publishing Workflow Automation

A Python desktop toolkit built around a real local-publishing workflow. The
application combines a PySide2 control panel with independent workers for
collecting article content, preparing issue folders and Excel planning
sheets, organizing publication images, and processing ODT/RTF documents.

## What the project automates

- **Article collection** – batch, continuation and single-article scraping
  using Selenium / BeautifulSoup.
- **Regional workflow** – one workflow for several editorial sections and
  municipalities.
- **Excel planning sheets** – issue-folder preparation and population of
  section-specific spreadsheets.
- **Image workflow** – collect source images from archive subdirectories,
  stage selected images for processing, restore processed output and rename
  images from spreadsheet data.
- **ODT / RTF processing** – batch ODT-to-RTF conversion through OpenOffice
  plus RTF validation/text extraction.
- **Process orchestration** – the desktop GUI starts workers as independent
  Python processes and displays stdout/stderr.

## Structure

```text
app/             desktop control panel
common/          shared configuration
scrapers/        article collection workers
spreadsheets/    issue / Excel automation
images/          image collection and preparation
documents/       ODT / RTF utilities
docs/            architecture and migration notes
```

## Technology

Python, PySide2, Selenium, BeautifulSoup, openpyxl, pandas, Pillow,
requests, pyautogui and striprtf. OpenOffice is used as an external
dependency for ODT-to-RTF conversion.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.json config.json
python app\main.py
```

Edit `config.json` and point it to your own workspace, issue output,
template, image archive, ChromeDriver and OpenOffice locations.

## Public-repository note

This is a cleaned and reorganized portfolio version of a production-use
personal automation toolkit. Local publishing data, spreadsheet templates,
images, cookies, browser profiles, credentials and machine-specific paths
are intentionally excluded from version control.

The production launcher referenced an external `odt_to_rtf_gui.py` that was
not present in the supplied source archive. `documents/odt_to_rtf.py` is a
clean portable OpenOffice conversion layer; publication-specific template or
style mapping from that external converter is not claimed to be reproduced.

Some worker modules intentionally retain the source workflow's staging-file
format to document the real migration path from production scripts to a
maintainable package.

## Author

Adam Jagodzinski / TEL-TECH
