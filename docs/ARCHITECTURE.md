# Architecture overview

The application is organized as a desktop orchestrator plus independent worker scripts.

## 1. Desktop control panel

The PySide2 interface acts as the operator entry point. It starts worker processes and displays their stdout/stderr and execution state.

## 2. Content collection

Selenium / BeautifulSoup workers collect article content in batch or single-item mode. Content is classified into regional / editorial sections and written to intermediate working files used by later stages.

## 3. Issue and spreadsheet preparation

Issue-folder utilities create the working directory for a new publication issue. Spreadsheet workers use pandas / openpyxl to populate planning sheets for individual sections.

## 4. Image preparation

Image utilities copy source images into issue-specific working directories, prepare selected images for external processing and copy processed results back into the publishing workflow.

## 5. Document processing

The document pipeline converts ODT source documents into RTF and validates / extracts RTF text for downstream editorial use. OpenOffice is treated as an external application dependency rather than being bundled with the project.

## Refactoring goals for the public repository

- Replace hard-coded Windows paths with `config.json`.
- Use relative paths between Python modules.
- Keep credentials, cookies, browser profiles and local content out of Git.
- Consolidate historical script versions into one maintained implementation per function.
- Gradually add tests around path handling and data-transformation logic.
