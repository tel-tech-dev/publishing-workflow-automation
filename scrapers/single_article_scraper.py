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

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from PIL import ImageGrab, Image

# other necessary ones
import urllib.request
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import time
import re
import datetime
from requests_html import HTMLSession
import requests
from tqdm import tqdm
import re

import os
import pyautogui
import shutil
import sys
#import aspose.words as aw

def makemydir(whatever):
  try:
    os.makedirs(whatever)
  except OSError:
    pass
  # let exception propagate if we just can't
  # cd into the specified directory
  os.chdir(whatever)

def convert_month(date_string):
    if "kwietnia" in date_string:
        new_string = date_string.replace(" kwietnia ", ".4.")
    elif "maja" in date_string:
        new_string = date_string.replace(" maja ", ".5.")
    elif "czerwca" in date_string:
        new_string = date_string.replace(" czerwca ", ".6.")
    elif "lipca" in date_string:
        new_string = date_string.replace(" lipca ", ".7.")
    elif "sierpnia" in date_string:
        new_string = date_string.replace(" sierpnia ", ".8.")
    elif "września" in date_string:
        new_string = date_string.replace(" września ", ".9.")
    elif "października" in date_string:
        new_string = date_string.replace(" października ", ".10.")
    elif "listopada" in date_string:
        new_string = date_string.replace(" listopada ", ".11.")
    elif "grudnia" in date_string:
        new_string = date_string.replace(" grudnia ", ".12.")
    elif "stycznia" in date_string:
        new_string = date_string.replace(" stycznia ", ".1.")
    elif "lutego" in date_string:
        new_string = date_string.replace(" lutego ", ".2.")
    elif "marca" in date_string:
        new_string = date_string.replace(" marca ", ".3.")
    return new_string



# ----------------------------------------------------------------------
# FILTR REKLAM GOOGLE v1.2
# ----------------------------------------------------------------------
ARTICLE_XPATH = "//*[@id='portal_1']/div[2]/div/div/div/section[1]/article"

GOOGLE_AD_BLOCK_URLS = [
    "*://*.googlesyndication.com/*",
    "*://*.doubleclick.net/*",
    "*://*.googleadservices.com/*",
    "*://*.adservice.google.com/*",
    "*://*.google.com/pagead/*",
    "*://*.google.pl/pagead/*",
]

def block_google_ads(browser):
    """Blokuje najczęstsze requesty Google Ads przed wejściem na artykuły."""
    try:
        browser.execute_cdp_cmd("Network.enable", {})
        browser.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {"urls": GOOGLE_AD_BLOCK_URLS}
        )
        print("Google Ads: blokowanie requestów aktywne.")
    except Exception as exc:
        # Drugi poziom ochrony - usuwanie reklam z DOM - nadal będzie działał.
        print("Google Ads: nie udało się włączyć blokowania CDP:", exc)

def remove_ads_from_article(browser):
    """
    Usuwa elementy reklamowe bezpośrednio z DOM artykułu.
    Dzięki temu późniejsze article.text zachowuje dokładnie ten sam sposób
    dzielenia tekstu na linie, którego używały stare, działające skrypty.
    """
    article = WebDriverWait(browser, 15).until(
        EC.presence_of_element_located((By.XPATH, ARTICLE_XPATH))
    )

    browser.execute_script(r"""
        const article = arguments[0];

        const selectors = [
            "iframe",
            "ins.adsbygoogle",
            ".adsbygoogle",
            ".adsbygoogle-noablate",
            ".google-auto-placed",
            "[class*='google-auto-placed']",
            "[class*='adsbygoogle']",
            "[id^='aswift_']",
            "[id*='aswift_']",
            "[name^='aswift_']",
            "[name*='aswift_']",
            "[id^='google_ads_']",
            "[id*='google_ads_']",
            "[name^='google_ads_']",
            "[name*='google_ads_']",
            "[id*='google_ads_iframe']",
            "[name*='google_ads_iframe']",
            "[data-ad-client]",
            "[data-ad-slot]",
            "[data-ad-format]",
            "[data-ad-status]",
            "[data-google-query-id]",
            "[data-anchor-status]",
            "#google_vignette",
            "[id^='google_vignette']",
            "[class*='google-vignette']",
            "[src*='googlesyndication.com']",
            "[src*='doubleclick.net']",
            "[src*='googleadservices.com']",
            "script[src*='googlesyndication']",
            "script[src*='doubleclick']",
            "script[src*='googleadservices']"
        ];

        article.querySelectorAll(selectors.join(",")).forEach(el => el.remove());

        // Dodatkowy bezpiecznik dla wrapperów reklam automatycznych Google.
        article.querySelectorAll("div, section, aside, ins").forEach(el => {
            const id = (el.id || "").toLowerCase();
            const cls = (typeof el.className === "string" ? el.className : "").toLowerCase();

            const looksLikeGoogleAd =
                id.startsWith("aswift_") ||
                id.includes("aswift_") ||
                id.startsWith("google_ads_") ||
                id.includes("google_ads_iframe") ||
                id.includes("google_vignette") ||
                cls.includes("google-auto-placed") ||
                cls.includes("adsbygoogle") ||
                cls.includes("google-vignette");

            if (looksLikeGoogleAd) {
                el.remove();
            }
        });
    """, article)

    return article

def get_clean_article_text(browser):
    """
    Najpierw usuwa reklamy z DOM, potem pobiera tekst PRZEZ SELENIUM .text.
    To zachowuje oryginalny układ linii (data / tytuł / fot. / treść).
    """
    article = remove_ads_from_article(browser)
    return article.text.strip()

def safe_split_title(tytul):
    """
    Dzieli tytuł na nadtytuł i tytuł właściwy przy pierwszym '. '.
    Jeżeli separatora nie ma, nie wywala IndexError - zwraca tytuł
    w obu polach, zgodnie z dotychczasowym zachowaniem wersji II.
    """
    parts = tytul.split(". ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]

    print("UWAGA: tytuł bez separatora '. ': " + repr(tytul))
    return tytul, tytul

def grabPostText (browser,profil,filename):
    time.sleep(1)
    gm=[]
    tekst = get_clean_article_text(browser)
    soup = bs(browser.page_source, "lxml")
    for img in soup.find_all("img", alt=re.compile("fot")):
        foto_link = img.get("src")
        foto_link = "http://www.powiat24.pl/"+foto_link
    #tekst = browser.find_element(By.XPATH, "//*[@id='portal_1']/div[2]/div/div/div/section[1]/article/header/div").text
    #tekst = browser.find_all("div", {"data-ad-comet-preview":"message"})
    sep = "Oceń artykuł:"
    if int(profil)==0:
        gm="SPORT"
    if int(profil)==1:
        gm="POWIAT"
    if int(profil)==2:
        gm="NAKLO"
    if int(profil)==3:
        gm="SZUBIN"
    if int(profil)==4:
        gm="KCYNIA"
    if int(profil)==5:
        gm="MROCZA"
    if int(profil)==6:
        gm="SADKI"
    if int(profil)==7:
        gm="ROLNICZE"
    if int(profil)==8:
        gm="POLICJA"
    separator = "------------------------------\n"+gm+"\n------------------------------\n"
    tekst = tekst.split(sep, 1)[0]
    f = open(WORKSPACE_PREFIX + "myfile5_single.txt",mode='a', encoding="utf-8")
    f.write(separator)
    f.write(tekst)
    f.write("\n"+filename+"\n")
    f.close()
    #osCommandString = "notepad.exe tekst_ze_strony.txt"
    #os.system(osCommandString)
    return foto_link

def grabPostTextFile (browser,profil,nr_gazety,filenumber):
    time.sleep(0.5)
    gm=[]
    tekst = get_clean_article_text(browser)
    #tekst = browser.find_element(By.XPATH, "//*[@id='portal_1']/div[2]/div/div/div/section[1]/article/header/div").text
    #tekst = browser.find_all("div", {"data-ad-comet-preview":"message"})
    sep = "Oceń artykuł:"
    tekst = tekst.split(sep, 1)[0] # ucięcie koncowki
    linie = tekst.split("\n")
    if "WIADOMOŚCI Z REGIONU" in linie:
        linie.remove("WIADOMOŚCI Z REGIONU")
    # łączymy z powrotem w tekst
    tekst = "\n".join(linie)
    data = tekst.split("\n",1)[0]
    #print("data: ", data)
    foto = tekst.split("\n",3)[2] # foto
    tytul = tekst.split("\n",2)[1] # tytul
    tytul = tytul.replace("\"", "")
    tytul = tytul.replace("?", ".")
    tytul = re.sub("[\"!?%()<>]","",tytul)
    #print("0:",tytul) # podwojny tytul
    tytul1, tytul2 = safe_split_title(tytul)
    tytul1 = tytul1.replace("\"", "")
    tytul1 = tytul1.replace("?", ".")
    tytul1 = re.sub("[\"!?%()<>]","",tytul1)
    #print("1:",tytul1) # pierwsza czesc tytulu
    tytul2 = tytul2.replace("\"", "")
    tytul2 = tytul2.replace("?", "")
    tytul2 = re.sub("[\"!?%()<>]","",tytul2)
    #print("2:",tytul2) # druga czesc tytulu
    tekst = tekst.split("\n",3)[3] # tekst ponizej foto
    #print("tekst:",tekst)
    if int(profil)==0:
        gm="_SpA_IJ_"
        tab_spa.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_spa.append(tytul)
        tab_dat_spa.append(data)
        tab_dlug_spa.append(len(tekst))
    if int(profil)==1:
        gm="_PowA_IJ_"
        tab_pow.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_pow.append(tytul)
        tab_dat_pow.append(data)
        tab_dlug_pow.append(len(tekst))
    if int(profil)==2:
        gm="_Nk_IJ_"
        tab_nk.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_nk.append(tytul)
        tab_dat_nk.append(data)
        tab_dlug_nk.append(len(tekst))
    if int(profil)==3:
        gm="_Szb_IJ_"
        tab_szb.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_szb.append(tytul)
        tab_dat_szb.append(data)
        tab_dlug_szb.append(len(tekst))
    if int(profil)==4:
        gm="_Kc_IJ_"
        tab_kc.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_kc.append(tytul)
        tab_dat_kc.append(data)
        tab_dlug_kc.append(len(tekst))
    if int(profil)==5:
        gm="_Mr_IJ_"
        tab_mr.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_mr.append(tytul)
        tab_dat_mr.append(data)
        tab_dlug_mr.append(len(tekst))
    if int(profil)==6:
        gm="_Sd_IJ_"
        tab_sd.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_sd.append(tytul)
        tab_dat_sd.append(data)
        tab_dlug_sd.append(len(tekst))
    if int(profil)==7:
        gm="_RolA_IJ_"
        tab_rol.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_rol.append(tytul)
        tab_dat_rol.append(data)
        tab_dlug_rol.append(len(tekst))
    if int(profil)==8:
        gm="_PolA_IJ_"
        tab_pol.append(nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1)
        tab_tyt_pol.append(tytul)
        tab_dat_pol.append(data)
        tab_dlug_pol.append(len(tekst))
    filename = nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1
    #usnięcie pierwszej linii
    f = open(WORKSPACE_PREFIX + ""+nr_gazety+"/"+nr_gazety+gm+"0"+str(filenumber)+"_"+tytul1+".odt",mode='a', encoding="utf-8")
    f.write(tytul1+"\n")
    f.write(tytul2+"\n")
    f.write(tekst)
    f.write(foto)
    f.close()
    return filename+"\nfotka "+nr_gazety+gm+"0"+str(filenumber)+"_",data,tytul

def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress.iterable:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


#----------------------------
#main program
#----------------------------
# set options as you wish
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.page_load_strategy = 'eager'
options.add_argument("--disable-infobars")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
service = ChromeService(executable_path=CHROMEDRIVER_PATH)
options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 1}
)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")

#numer = input("Podaj numer gazety: ")
numer = str(sys.argv[1])
browser = webdriver.Chrome(service=service, options=options)
block_google_ads(browser)
makemydir(WORKSPACE_PREFIX + ""+numer)
makemydir(WORKSPACE_PREFIX + ""+numer+"/final")
makemydir(WORKSPACE_PREFIX + ""+numer+"/foto")
makemydir(WORKSPACE_PREFIX + ""+numer+"/przerobione")
makemydir(WORKSPACE_PREFIX + ""+numer+"/selected_fotos")

l_spa = 0
tab_spa = []
tab_tyt_spa = []
tab_dat_spa = []
tab_dlug_spa = []
l_nk = 0
tab_nk = []
tab_tyt_nk = []
tab_dat_nk = []
tab_dlug_nk = []
l_pow = 0
tab_pow = []
tab_tyt_pow = []
tab_dat_pow = []
tab_dlug_pow = []
l_szb = 0
tab_szb = []
tab_tyt_szb = []
tab_dat_szb = []
tab_dlug_szb = []
l_kc = 0
tab_kc = []
tab_tyt_kc = []
tab_dat_kc = []
tab_dlug_kc = []
l_mr = 0
tab_mr = []
tab_tyt_mr = []
tab_dat_mr = []
tab_dlug_mr = []
l_sd = 0
tab_sd = []
tab_tyt_sd = []
tab_dat_sd = []
tab_dlug_sd = []
l_rol = 0
tab_rol = []
tab_tyt_rol = []
tab_dat_rol = []
tab_dlug_rol = []
l_pol = 0
tab_pol = []
tab_tyt_pol = []
tab_dat_pol = []
tab_dlug_pol = []
licznik = 0
count = 0

nbr = str(sys.argv[2])
sin = str(sys.argv[3])
art_link = str(sys.argv[4])

# Strips the newline character
gmina=sin

browser.get(art_link)
if int(sin)==0:
    licznik = int(nbr)+1
    print(art_link)
    print("SPORT\n")
if int(sin)==1:
    licznik = int(nbr)+1
    print(art_link)
    print("POWIAT\n")
if int(sin)==2:
    licznik = int(nbr)+1
    print(art_link)
    print("NAKLO\n")
if int(sin)==3:
    licznik = int(nbr)+1
    print(art_link)
    print("SZUBIN\n")
if int(sin)==4:
    licznik = int(nbr)+1
    print(art_link)
    print("KCYNIA\n")
if int(sin)==5:
    licznik = int(nbr)+1
    print(art_link)
    print("MROCZA\n")
if int(sin)==6:
    licznik = int(nbr)+1
    print(art_link)
    print("SADKI\n")
if int(sin)==7:
    licznik = int(nbr)+1
    print(art_link)
    print("ROLNICZE\n")
if int(sin)==8:
    licznik = int(nbr)+1
    print(art_link)
    print("POLICJA\n")
#nazwa_pliku = grabPostTextFile(browser,gmina,numer,licznik)

dzm = ""
tyt = ""
source_folder = ""
nazwa_pliku, dzm, tyt = grabPostTextFile(browser,gmina,numer,licznik)
dzm = convert_month(dzm)
print(dzm)
print(tyt)

download(grabPostText (browser,gmina,nazwa_pliku),WORKSPACE_PREFIX + ""+numer+"/foto")

foto_file = open(WORKSPACE_PREFIX + "foto_file.txt",mode='a', encoding="utf-8")
foto_file.write(dzm+"\n")
foto_file.write(tyt)
foto_file.write("\n")
foto_file.close()

with open(WORKSPACE_PREFIX + "myfile5_single.txt",mode='a', encoding="utf-8") as f, open(WORKSPACE_PREFIX + "spa.txt",mode='a', encoding="utf-8") as f_spa, open(WORKSPACE_PREFIX + "pow.txt",mode='a', encoding="utf-8") as f_pow, open(WORKSPACE_PREFIX + "nk.txt",mode='a', encoding="utf-8") as f_nk, open(WORKSPACE_PREFIX + "kc.txt",mode='a', encoding="utf-8") as f_kc, open(WORKSPACE_PREFIX + "szb.txt",mode='a', encoding="utf-8") as f_szb, open(WORKSPACE_PREFIX + "mr.txt",mode='a', encoding="utf-8") as f_mr, open(WORKSPACE_PREFIX + "sd.txt",mode='a', encoding="utf-8") as f_sd, open(WORKSPACE_PREFIX + "rol.txt",mode='a', encoding="utf-8") as f_rol, open(WORKSPACE_PREFIX + "pol.txt",mode='a', encoding="utf-8") as f_pol:
    # SPORT
    f.write("---\nSPORT:\n")
    for elem in tab_spa:
        f.write(elem+".rtf\n")
        f_spa.write(elem+".rtf\n")
    f.write("SPORT TYTUŁY:\n")
    for elem in tab_tyt_spa:
        f.write(elem+"\n")
        f_spa.write(elem+"\n")
    f.write("SPORT DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_spa:
        f.write(str(elem)+"\n")
        f_spa.write(str(elem)+"\n")
    f.write("SPORT FOTO:\n")
    for elem in tab_tyt_spa:
        f.write("/Redakcja24/"+elem+"\n")
        f_spa.write("/Redakcja24/"+elem+"\n")
    # POWIAT
    f.write("---\nPOWIAT\n")
    for elem in tab_pow:
        f.write(elem+".rtf\n")
        f_pow.write(elem+".rtf\n")
    f.write("POWIAT TYTUŁY:\n")
    for elem in tab_tyt_pow:
        f.write(elem+"\n")
        f_pow.write(elem+"\n")
    f.write("POWIAT DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_pow:
        f.write(str(elem)+"\n")
        f_pow.write(str(elem)+"\n")
    f.write("POWIAT FOTO:\n")
    for elem in tab_tyt_pow:
        f.write("/Redakcja24/"+elem+"\n")
        f_pow.write("/Redakcja24/"+elem+"\n")
    # NAKLO
    f.write("---\nNAKLO\n")
    for elem in tab_nk:
        f.write(elem+".rtf\n")
        f_nk.write(elem+".rtf\n")
    f.write("NAKLO TYTUŁY:\n")
    for elem in tab_tyt_nk:
        f.write(elem+"\n")
        f_nk.write(elem+"\n")
    f.write("NAKLO DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_nk:
        f.write(str(elem)+"\n")
        f_nk.write(str(elem)+"\n")
    f.write("NAKLO: FOTO:\n")
    for elem in tab_tyt_nk:
        f.write("/Redakcja24/"+elem+"\n")
        f_nk.write("/Redakcja24/"+elem+"\n")
    # SZUBIN
    f.write("---\nSZUBIN\n")
    for elem in tab_szb:
        f.write(elem+".rtf\n")
        f_szb.write(elem+".rtf\n")
    f.write("SZUBIN TYTUŁY:\n")
    for elem in tab_tyt_szb:
        f.write(elem+"\n")
        f_szb.write(elem+"\n")
    f.write("SZUBIN DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_szb:
        f.write(str(elem)+"\n")
        f_szb.write(str(elem)+"\n")
    f.write("SZUBIN FOTO:\n")
    for elem in tab_tyt_szb:
        f.write("/Redakcja24/"+elem+"\n")
        f_szb.write("/Redakcja24/"+elem+"\n")
    # KCYNIA
    f.write("---\nKCYNIA\n")
    for elem in tab_kc:
        f.write(elem+".rtf\n")
        f_kc.write(elem+".rtf\n")
    f.write("KCYNIA TYTUŁY:\n")
    for elem in tab_tyt_kc:
        f.write(elem+"\n")
        f_kc.write(elem+"\n")
    f.write("KCYNIA DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_kc:
        f.write(str(elem)+"\n")
        f_kc.write(str(elem)+"\n")
    f.write("KCYNIA FOTO:\n")
    for elem in tab_tyt_kc:
        f.write("/Redakcja24/"+elem+"\n")
        f_kc.write("/Redakcja24/"+elem+"\n")
    # MROCZA
    f.write("---\nMROCZA\n")
    for elem in tab_mr:
        f.write(elem+".rtf\n")
        f_mr.write(elem+".rtf\n")
    f.write("MROCZA TYTUŁY:\n")
    for elem in tab_tyt_mr:
        f.write(elem+"\n")
        f_mr.write(elem+"\n")
    f.write("MROCZA DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_mr:
        f.write(str(elem)+"\n")
        f_mr.write(str(elem)+"\n")
    f.write("MROCZA FOTO:\n")
    for elem in tab_tyt_mr:
        f.write("/Redakcja24/"+elem+"\n")
        f_mr.write("/Redakcja24/"+elem+"\n")
    # SADKI
    f.write("---\nSADKI\n")
    for elem in tab_sd:
        f.write(elem+".rtf\n")
        f_sd.write(elem+".rtf\n")
    f.write("SADKI TYTUŁY:\n")
    for elem in tab_tyt_sd:
        f.write(elem+"\n")
        f_sd.write(elem+"\n")
    f.write("SADKI DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_sd:
        f.write(str(elem)+"\n")
        f_sd.write(str(elem)+"\n")
    f.write("SADKI FOTO:\n")
    for elem in tab_tyt_sd:
        f.write("/Redakcja24/"+elem+"\n")
        f_sd.write("/Redakcja24/"+elem+"\n")
    # ROLNICZE
    f.write("---\nROLNICZE\n")
    for elem in tab_rol:
        f.write(elem+".rtf\n")
        f_rol.write(elem+".rtf\n")
    f.write("ROLNICZE TYTUŁY:\n")
    for elem in tab_tyt_rol:
        f.write(elem+"\n")
        f_rol.write(elem+"\n")
    f.write("ROLNICZE DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_rol:
        f.write(str(elem)+"\n")
        f_rol.write(str(elem)+"\n")
    f.write("ROLNICZE FOTO:\n")
    for elem in tab_tyt_rol:
        f.write("/Redakcja24/"+elem+"\n")
        f_rol.write("/Redakcja24/"+elem+"\n")
    # POLICJA
    f.write("---\nPOLICJA\n")
    for elem in tab_pol:
        f.write(elem+".rtf\n")
        f_pol.write(elem+".rtf\n")
    f.write("POLICJA TYTUŁY:\n")
    for elem in tab_tyt_pol:
        f.write(elem+"\n")
        f_pol.write(elem+"\n")
    f.write("POLICJA DLUGOSCI TEKSTOW:\n")
    for elem in tab_dlug_pol:
        f.write(str(elem)+"\n")
        f_pol.write(str(elem)+"\n")
    f.write("POLICJA FOTO:\n")
    for elem in tab_tyt_pol:
        f.write("/Redakcja24/"+elem+"\n")
        f_pol.write("/Redakcja24/"+elem+"\n")
f.close()
f_spa.close()
f_pow.close()
f_nk.close()
f_szb.close()
f_mr.close()
f_kc.close()
f_sd.close()
f_rol.close()
browser.close()
browser.quit()




