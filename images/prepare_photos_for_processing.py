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
nr_gazety = str(sys.argv[1])
subfolders = [ f.name for f in os.scandir(WORKSPACE_PREFIX + ""+str(nr_gazety)+"/selected_fotos/") if f.is_dir() ]
destination = PHOTO_PROCESSING_PREFIX + ""
makemydir (WORKSPACE_PREFIX + ""+str(nr_gazety)+"/selected_fotos/converted/")
print(len(subfolders))
converted_file = open(WORKSPACE_PREFIX + "converted_file.txt",mode='a', encoding="utf-8")
count=0
for count in range(0,len(subfolders)):
    source_folder = WORKSPACE_PREFIX + ""+str(nr_gazety)+"/selected_fotos/"+subfolders[count]
    makemydir (WORKSPACE_PREFIX + ""+str(nr_gazety)+"/selected_fotos/converted/"+subfolders[count])
    #dest_table.append(count)
    #dest_table.append(source_folder)
    for file_name in os.listdir(source_folder):
        source = source_folder+"/"+file_name
        dest = destination+"/"+file_name
        shutil.copy(source, dest)
        #source_table.append(PHOTO_PROCESSING_PREFIX + "rozjasnione_wyostrzone/"+file_name)
        converted_file.write(PHOTO_PROCESSING_PREFIX + "rozjasnione_wyostrzone/"+file_name+"\n")
        #dest_table.append(WORKSPACE_PREFIX + ""+str(nr_gazety)+"/selected_fotos/converted/"+subfolders[count]+"/"+file_name)
        converted_file.write(WORKSPACE_PREFIX + ""+str(nr_gazety)+"/selected_fotos/converted/"+subfolders[count]+"/"+file_name+"\n")
    count = count + 1

converted_file.close()
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

print(len(source_table))
print(source_table)
print(len(dest_table))
print(dest_table)
"""
count=0
for count in range(0,len(source_table)-1):
    source = source_table[count]
    dest = dest_table[count]
    shutil.copy(source, dest)
    count = count + 1

file1 = open(WORKSPACE_PREFIX + 'foto_file.txt',mode='r',encoding="utf-8")
Lines = file1.readlines()

makemydir(WORKSPACE_PREFIX + ""+str(sys.argv[1])+"/selected_fotos")

count = 0
for line in Lines:
    count += 1
    #print(line.strip())
    if (count % 2) > 0:
        data=line.strip()
        print("data: ", data)
        continue
    line = line.strip() # usuniecie znaku koncza lini \n
    makemydir(WORKSPACE_PREFIX + ""+str(sys.argv[1])+"/selected_fotos/"+line+"/0")
    destination = WORKSPACE_PREFIX + ""+str(sys.argv[1])+"/selected_fotos/"+line+"/0"
    dir1 = os.path.join(PHOTO_ARCHIVE_PREFIX, str(data), "ftp", str(line), "0")
    source_folder = PHOTO_ARCHIVE_PREFIX + ""+str(data)+"/ftp/"+line+"/0"
    #source_folder = ""

    #shutil.copytree(source_folder, dir1)
    #os.chdir(source_folder)
    print("sourcd: ", source_folder)

    for file_name in os.listdir(source_folder):
        source = source_folder+"/"+file_name
        dest = destination+"/"+file_name
        print(file_name)
        print(source)
        print(dest)
        shutil.copy(source, dest)
"""
