# Source-to-public migration map

| Production source | Public repository |
|---|---|
| `main_powiat_text_grab.py` | `app/main.py` |
| `grab_powiat-headless.py` | `scrapers/article_scraper.py` |
| `grab_powiat-headless-II_czesc.py` | `scrapers/article_scraper_continuation.py` |
| `grab_powiat-single.py` | `scrapers/single_article_scraper.py` |
| `folder_files_preparation.py` | `spreadsheets/create_issue_folder.py` |
| `fill_in_rozpiska.py` | `spreadsheets/fill_schedules.py` |
| `fill_in_rozpiska-II.py` | `spreadsheets/fill_schedules_continuation.py` |
| `fill_in_rozpiska-single.py` | `spreadsheets/fill_schedule_single.py` |
| `copy_photos_from_ftp_folder.py` | `images/collect_source_photos.py` |
| `copy-photos-for-sharp_screen.py` | `images/prepare_photos_for_processing.py` |
| `copy-photos-from-sharp_screen.py` | `images/restore_processed_photos.py` |
| `rename_photos_gui.py` | `images/rename_photos.py` |
| `rtf-check.py` | `documents/rtf_check.py` |
| external `odt_to_rtf_gui.py` | `documents/odt_to_rtf.py` (portable wrapper) |

## Deliberately excluded

The public package does not include production credentials, cookie files,
Chrome profiles, private editorial data, local images, spreadsheet templates,
unrelated scripts from the large working directory, or historical duplicate
versions of the same tool.
