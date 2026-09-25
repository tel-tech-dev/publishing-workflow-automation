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
import re
import os
import shutil
import sys

def makemydir(whatever):
  try:
    os.makedirs(whatever)
  except OSError:
    pass
  # let exception propagate if we just can't
  # cd into the specified directory
  os.chdir(whatever)

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

dest_table = []
source_table = []

file1 = open(WORKSPACE_PREFIX + "converted_file.txt",mode='r',encoding="utf-8")
Lines = file1.readlines()

count = 0
for line in Lines:
    count += 1
    if (count % 2) > 0:
        line = line.strip()
        source_table.append(line)
    else:
        line = line.strip()
        dest_table.append(line)

count=0
for count in range(0,len(source_table)):
    source = source_table[count]
    dest = dest_table[count]
    shutil.copy(source, dest)
    count = count + 1

directory = WORKSPACE_PREFIX.rstrip("/")
for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        os.remove(os.path.join(directory, filename))

directory = WORKSPACE_PREFIX.rstrip("/")
for filename in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, filename)):
        os.remove(os.path.join(directory, filename))
