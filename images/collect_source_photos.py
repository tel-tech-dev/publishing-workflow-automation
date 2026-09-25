# Public-repository configuration layer (replaces machine-specific paths).
from pathlib import Path as _ConfigPath
import sys as _config_sys
_PROJECT_ROOT = _ConfigPath(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in _config_sys.path:
    _config_sys.path.insert(0, str(_PROJECT_ROOT))
from common.config import (  # noqa: E402
    WORKSPACE_PREFIX,
    ISSUE_OUTPUT_PREFIX,
    PHOTO_ARCHIVE_PREFIX,
    PHOTO_PROCESSING_PREFIX,
    CHROMEDRIVER_PATH,
    PUBLICATION_YEAR,
)

import datetime
import os
import shutil
import sys

def makemydir(whatever):
    try:
        os.makedirs(whatever, exist_ok=True)
    except OSError:
        pass
    os.chdir(whatever)

def first_existing_path(paths):
    """Zwraca pierwszy istniejący katalog z listy (i niepusty), albo None."""
    for p in paths:
        if os.path.isdir(p):
            try:
                files = [os.path.join(p, name) for name in os.listdir(p)
                         if os.path.isfile(os.path.join(p, name))]
                if files:
                    return p
            except PermissionError:
                pass
    return None

# === WEJŚCIE ===
with open(WORKSPACE_PREFIX + 'foto_file.txt', 'r', encoding='utf-8') as f:
    Lines = f.readlines()

makemydir(fWORKSPACE_PREFIX + "{str(sys.argv[1])}/selected_fotos")

# === ZBIORNIKI NA PODSUMOWANIE ===
missing = []              # lista (data, nazwa, source_pref, source_fallback)
copied_files = 0
copied_sets  = 0          # ile wpisów (folderów docelowych) skopiowano
errors = []               # ewentualne wyjątki podczas kopiowania

count = 0
data = None  # aktualna data z pliku wejściowego

for raw in Lines:
    count += 1
    line = raw.strip()

    # linia nieparzysta = data
    if (count % 2) > 0:
        data = line
        print("data:", data)
        continue

    # linia parzysta = nazwa folderu
    name = line

    # źródła
    source_preferred = fPHOTO_ARCHIVE_PREFIX + "{data}/ftp/{name}/0"
    source_fallback  = fPHOTO_ARCHIVE_PREFIX + "{data}/ftp/{name}"
    source_folder = first_existing_path([source_preferred, source_fallback])

    if not source_folder:
        # NIE drukujemy od razu – zbieramy do podsumowania
        missing.append((data, name, source_preferred, source_fallback))
        continue

    # policz i wybierz miejsce docelowe
    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    file_count = len(files)
    if file_count == 0:
        missing.append((data, name, source_preferred, source_fallback))
        continue

    if file_count > 1:
        destination = fWORKSPACE_PREFIX + "{str(sys.argv[1])}/selected_fotos/{name}/0"
    else:
        destination = fWORKSPACE_PREFIX + "{str(sys.argv[1])}/selected_fotos/{name}"

    makemydir(destination)

    print(f"Źródło: {source_folder}")
    print(f"Cel:    {destination}")
    print(f"Liczba zdjęć: {file_count}")

    copied_sets += 1
    for file_name in files:
        src = os.path.join(source_folder, file_name)
        dst = os.path.join(destination, file_name)
        try:
            shutil.copy2(src, dst)
            copied_files += 1
        except Exception as e:
            errors.append((data, name, file_name, str(e)))

# === PODSUMOWANIE ===
print("\n================ PODSUMOWANIE ================")
print(f"Skopiowane wpisy (foldery): {copied_sets}")
print(f"Skopiowane pliki:           {copied_files}")

if missing:
    print(f"\nBrak zdjęć dla {len(missing)} pozycji:")
    for i, (d, n, pref, fallb) in enumerate(missing, 1):
        print(f"  {i}. {d} / {n}")
        print(f"     ↳ sprawdzono: {pref}")
        print(f"                    {fallb}")

if errors:
    print(f"\nBłędy kopiowania ({len(errors)}):")
    for i, (d, n, fname, msg) in enumerate(errors, 1):
        print(f"  {i}. {d} / {n} / {fname} → {msg}")

print("==============================================")
