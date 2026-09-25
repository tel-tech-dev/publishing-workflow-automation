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

# napisz program który na podstawie pliku excela wszystkich komórek w kolumnie F znajdzie katalog np. zawartość komórki F1 "/Redakcja24/Wsparcie na inwestycje. Ilu rolników zainteresowanych" wskazuje na katalog
# WORKSPACE_PREFIX + "42\selected_fotos\Wsparcie na inwestycje. Ilu rolników zainteresowanych". w tym katalogu jest jeden plik graficzny jpg i program musi zmienić nazwę tego pliku wpisaną w
# komórkę G1 (dla F1 nazwa jest w G1, dla F2 nazwa w G2 itd).
# program ma posiadac GUI w którym bede wybierał poprzez dialog plik excela do analizy
import os
import re
import sys
import traceback
from tkinter import Tk, Label, Entry, Button, Text, END, DISABLED, NORMAL, filedialog, messagebox, Checkbutton, BooleanVar

try:
    from openpyxl import load_workbook
except ImportError:
    raise SystemExit("Brak pakietu 'openpyxl'. Zainstaluj: pip install openpyxl")

INVALID_WIN_CHARS = r'<>:"/\\|?*'
INVALID_WIN_RE = re.compile(rf"[{re.escape(INVALID_WIN_CHARS)}]")


def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = INVALID_WIN_RE.sub("_", name)
    name = name.rstrip(" .")
    return name


def ensure_jpg_extension(name: str) -> str:
    lower = name.lower()
    if lower.endswith('.jpg') or lower.endswith('.jpeg'):
        return name
    return name + '.jpg'


def split_cell_lines(value) -> list:
    if value is None:
        return []
    s = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return [ln.strip() for ln in s.split("\n") if ln.strip()]


def find_jpgs(directory: str, include_subdirs: bool = False):
    if not os.path.isdir(directory):
        return [], f"Katalog nie istnieje: {directory}"

    jpgs = []
    for f in os.listdir(directory):
        p = os.path.join(directory, f)
        if os.path.isfile(p) and f.lower().endswith((".jpg", ".jpeg")):
            jpgs.append(p)

    jpgs.sort(key=lambda x: os.path.basename(x).lower())
    if not jpgs:
        return [], f"Brak plików JPG w katalogu: {directory}"
    return jpgs, None


def extract_folder_from_cell(cell_value: str, anchor_segment: str) -> str:
    if not cell_value:
        return ""
    import unicodedata
    s = str(cell_value)
    s = s.replace('\\', '/').replace('\xa0', ' ').strip()
    s = unicodedata.normalize("NFC", s)

    token = f"/{anchor_segment}/"
    s_lower = s.lower()
    token_lower = token.lower()
    if token_lower in s_lower:
        idx = s_lower.index(token_lower) + len(token_lower)
        segment = s[idx:]
        return segment.strip("/").strip()
    return s.strip("/").split("/")[-1].strip()


class App:
    def __init__(self, master: Tk):
        self.master = master
        master.title("Zmiana nazw JPG wg Excela (F->folder, G->nazwy; wiele linii= wiele plików)")
        master.geometry("920x560")

        Label(master, text="Plik Excel:").grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.excel_entry = Entry(master, width=90)
        self.excel_entry.grid(row=0, column=1, padx=6, pady=6, sticky='we')
        Button(master, text="Wybierz...", command=self.choose_excel).grid(row=0, column=2, padx=6, pady=6)

        Label(master, text="Katalog bazowy 'selected_fotos':").grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.base_entry = Entry(master, width=90)
        self.base_entry.grid(row=1, column=1, padx=6, pady=6, sticky='we')
        self.base_entry.insert(0, WORKSPACE_PREFIX + "01/selected_fotos")

        Label(master, text="Segment kotwicy (po nim nazwa z F):").grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.anchor_entry = Entry(master, width=90)
        self.anchor_entry.grid(row=2, column=1, padx=6, pady=6, sticky='we')
        self.anchor_entry.insert(0, "Redakcja24")

        Label(master, text="Arkusz (puste = pierwszy):").grid(row=3, column=0, sticky='e', padx=6, pady=6)
        self.sheet_entry = Entry(master, width=40)
        self.sheet_entry.grid(row=3, column=1, sticky='w', padx=6, pady=6)

        self.overwrite_var = BooleanVar(value=False)
        Checkbutton(master, text="Nadpisuj, jeśli plik docelowy już istnieje", variable=self.overwrite_var).grid(row=4, column=1, sticky='w', padx=6, pady=2)

        self.dryrun_var = BooleanVar(value=False)
        Checkbutton(master, text="Tryb testowy (bez zmian)", variable=self.dryrun_var).grid(row=5, column=1, sticky='w', padx=6, pady=2)

        Button(master, text="Start", command=self.run).grid(row=6, column=1, sticky='w', padx=6, pady=10)

        Label(master, text="Log:").grid(row=7, column=0, sticky='ne', padx=6)
        self.log = Text(master, width=110, height=22)
        self.log.grid(row=7, column=1, columnspan=2, sticky='nsew', padx=6, pady=6)

        master.columnconfigure(1, weight=1)
        master.rowconfigure(7, weight=1)

    def choose_excel(self):
        path = filedialog.askopenfilename(
            title="Wybierz plik Excel",
            filetypes=[("Excel", "*.xlsx;*.xlsm;*.xltx;*.xltm"), ("Wszystkie pliki", "*.*")],
        )
        if path:
            self.excel_entry.delete(0, END)
            self.excel_entry.insert(0, path)

    def log_write(self, text: str):
        self.log.configure(state=NORMAL)
        self.log.insert(END, text + "\n")
        self.log.see(END)
        self.log.configure(state=DISABLED)
        self.master.update_idletasks()

    def run(self):
        excel_path = self.excel_entry.get().strip()
        base_dir = self.base_entry.get().strip()
        anchor = self.anchor_entry.get().strip() or "Redakcja24"
        sheet_name = self.sheet_entry.get().strip() or None

        if not excel_path:
            messagebox.showerror("Błąd", "Wybierz plik Excel.")
            return
        if not os.path.isfile(excel_path):
            messagebox.showerror("Błąd", f"Nie znaleziono pliku: {excel_path}")
            return
        if not base_dir:
            messagebox.showerror("Błąd", "Podaj katalog bazowy.")
            return
        if not os.path.isdir(base_dir):
            messagebox.showerror("Błąd", f"Katalog bazowy nie istnieje: {base_dir}")
            return

        self.log.configure(state=NORMAL)
        self.log.delete(1.0, END)
        self.log.configure(state=DISABLED)

        try:
            wb = load_workbook(excel_path, data_only=True, read_only=True)
            ws = wb[sheet_name] if sheet_name else wb.worksheets[0]
        except Exception as e:
            messagebox.showerror("Błąd Excel", f"Nie można otworzyć arkusza: {e}")
            return

        self.log_write(f"Plik: {excel_path}")
        self.log_write(f"Arkusz: {ws.title}")
        self.log_write(f"Baza katalogów: {base_dir}")
        self.log_write(f"Kotwica: {anchor}")
        self.log_write("--- Start (od wiersza 5) ---")

        processed = 0
        renamed = 0
        errors = 0

        for i, row in enumerate(ws.iter_rows(min_row=5, values_only=True), start=5):
            val_f = row[5] if len(row) >= 6 else None
            val_g = row[6] if len(row) >= 7 else None

            if (val_f is None or str(val_f).strip() == "") and (val_g is None or str(val_g).strip() == ""):
                continue

            processed += 1
            try:
                folder_name = extract_folder_from_cell(str(val_f) if val_f is not None else "", anchor)
                if not folder_name:
                    self.log_write(f"[WARN] Wiersz {i}: pusty F – pomijam")
                    continue
                target_dir = os.path.join(base_dir, folder_name)
                self.log_write(f"[DBG] Wiersz {i}: folder z F -> '{folder_name}' | pełna ścieżka: {target_dir}")

                jpg_paths, err = find_jpgs(target_dir, include_subdirs=False)
                if err:
                    errors += 1
                    self.log_write(f"[ERR] {err}")
                    continue

                if val_g is None or str(val_g).strip() == "":
                    errors += 1
                    self.log_write(f"[ERR] Brak nazwy w kolumnie G dla katalogu: {target_dir}")
                    continue

                name_lines = split_cell_lines(val_g)
                if not name_lines:
                    errors += 1
                    self.log_write(f"[ERR] Kolumna G pusta po oczyszczeniu (wiersz {i})")
                    continue

                target_names = [ensure_jpg_extension(sanitize_filename(n)) for n in name_lines]

                n = min(len(target_names), len(jpg_paths))
                if len(target_names) != len(jpg_paths):
                    self.log_write(f"[WARN] Wiersz {i}: nazw w G = {len(target_names)}, zdjęć = {len(jpg_paths)}. Przetwarzam pary: {n}.")

                for k in range(n):
                    src = jpg_paths[k]
                    new_path = os.path.join(os.path.dirname(src), target_names[k])

                    # Jeśli plik o tej nazwie już istnieje – pomiń zmianę
                    if os.path.exists(new_path):
                        self.log_write(f"[SKIP] Istnieje już plik docelowy: {new_path}")
                        continue

                    self.log_write(f"[INFO] {src} -> {new_path}")
                    if not self.dryrun_var.get():
                        os.replace(src, new_path)
                    renamed += 1

                if len(jpg_paths) > n:
                    self.log_write(f"[INFO] {len(jpg_paths)-n} zdjęć pozostało bez zmiany nazwy (brak linii w G)")
                if len(target_names) > n:
                    self.log_write(f"[INFO] {len(target_names)-n} nazw z G nieużytych (brak zdjęć)")

            except Exception:
                errors += 1
                self.log_write("[EXC] " + traceback.format_exc())

        self.log_write("--- Koniec ---")
        self.log_write(f"Wierszy przetworzonych: {processed}")
        self.log_write(f"Plików przemianowanych: {renamed}")
        self.log_write(f"Błędów: {errors}")
        messagebox.showinfo("Zakończono", f"Przetworzono: {processed}\nZmieniono nazw: {renamed}\nBłędy: {errors}")


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
