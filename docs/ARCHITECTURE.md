# Architecture

## Desktop orchestrator
`app/main.py` is the operator entry point. It launches independent worker
processes and streams their output into the GUI. This reflects the original
production design while removing absolute `C:\...` script paths.

## Configuration
Machine-specific directories live in `config.json`, which is ignored by Git.
`config.example.json` documents the required keys. `common/config.py` exposes
paths to worker modules.

## Content collection
The three scraper workers are source-derived from the production batch,
continuation and single-article flows. Their existing parsing and staging
formats are retained; hard-coded workstation paths are replaced by config.

## Spreadsheet workflow
The production workflow uses section-specific Excel planning sheets and
intermediate staging files. `create_issue_folder.py` prepares a new issue;
the `fill_*` workers retain the production workbook layout.

## Image workflow
Image workers collect source photos from archive subfolders, stage selected
files for external processing, restore processed output and optionally rename
images from spreadsheet metadata.

## Document workflow
RTF extraction is refactored from the production utility. ODT conversion is
performed by a portable OpenOffice CLI wrapper because the separately stored
original converter was not included in the source archive.
