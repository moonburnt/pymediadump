## pymediadump - simple tool to download various media files from sites
## Copyright (c) 2021 moonburnt
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see https://www.gnu.org/licenses/gpl-3.0.txt

import requests
import logging
from re import findall
import argparse
from os import makedirs
from sys import exit
import configparser

DEFAULT_DOWNLOAD_DIRECTORY="./Downloads"

# Custom logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
log.addHandler(handler)

def get_page_source(link):
    '''Receives str(webpage url), returns raw content of said page'''
    log.debug(f"Fetching page content from {link}")
    page = requests.get(link, timeout = 100)
    page.raise_for_status()

    return page.text

def download_file(link):
    '''Receives str(link to download file), saves file to DOWNLOAD_DIRECTORY'''
    log.debug(f"Fetching file from {link}")
    data = requests.get(link, timeout = 100)
    data.raise_for_status()

    log.debug(f"Trying to determine filename")
    fn = link.rsplit('/', 1) #this aint perfect, coz link may contain some garbage such as id after file name
    filename = str(fn[1])
    save_path = DOWNLOAD_DIRECTORY+"/"+filename

    log.debug(f"Attempting to save file as {save_path}")
    with open(save_path, 'wb') as f:
        f.write(data.content)
    log.info(f"Successfully saved {filename} as {save_path}")

def get_download_links(page, search_rule):
    '''Receives str(webpage's html content) and str(search rule), returns link to download file'''
    log.debug(f"Searching for expression in html source")
    raw_links = findall(search_rule, page) #this will create list with all matching links

    log.debug(f"Found matching download links: {raw_links}, attempting to cleanup")
    clean_links = []
    for item in raw_links:
        log.debug(f"Cleaning up {item}")
        cl = item.rsplit("?", 1) #avoiding the issue described in comment of download_file()
        cl = str(cl[0])

        cl = cl.replace("\\", "") #avoiding backslashes in url - requests cant into them
        clean_links.append(cl)

    log.debug(f"Clean links are: {clean_links}")

    return clean_links

# argparse shenanigans
ap = argparse.ArgumentParser()
ap.add_argument("url", help="URL of webpage, from which you want to download your media", type=str)
ap.add_argument("-d", "--directory", help="Custom path to downloads directory", type=str)
ap.add_argument("-r", "--rules", help="Path to rules.ini that will be used to determine files to download", type=str)
args = ap.parse_args()

if args.rules:
    log.debug(f"Attempting to get download rules from {args.rules} file")
    try:
        cp = configparser.ConfigParser()
        cp.read(args.rules)
        RULESET_DESCRIPTION = cp['Main']['Description']
        RULESET_FIND = cp['Rules']['Find']
    except Exception as e:
        log.error(f"Some unfortunate error has happend: {e}")
        print(f"Couldnt get rules from provided file. Are you sure its path is correct and format match supported scheme?")
        exit(1)
else:
    print(f"Rules.ini isnt provided. Please specify path to correct file with -r flag and try again")
    exit(1)

if args.directory:
    log.debug(f"Custom downloads directory will be: {args.directory}")
    DOWNLOAD_DIRECTORY = args.directory
else:
    log.debug(f"Custom downloads directory isnt set, will use default: {DEFAULT_DOWNLOAD_DIRECTORY}")
    DOWNLOAD_DIRECTORY = DEFAULT_DOWNLOAD_DIRECTORY

try:
    makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)
except Exception as e:
    log.error(f"An error has happend while trying to create downloads directory: {e}")
    print(f"Couldnt set downloads directory. Either provided path is incorrect or you have no rights to write into {DOWNLOAD_DIRECTORY}")
    exit(1)
print(f"Downloads directory has been set to {DOWNLOAD_DIRECTORY}")

DOWNLOAD_URL = args.url

print(f"Attempting to download media from {DOWNLOAD_URL}")
try:
    page_html = get_page_source(DOWNLOAD_URL)
except Exception as e:
    log.error(f"Some unfortunate error has happend: {e}")
    print(f"Couldnt fetch provided url. Are you sure your link is correct and you have internet connection?")
    exit(1)

try:
    links = get_download_links(page_html, RULESET_FIND)
except Exception as e:
    log.error(f"Some unfortunate error has happend: {e}")
    print("Couldnt find download link :( Are you sure this link should contain supported file type?")
    exit(1)

for link in links:
    try:
        print(f"Downloading the file from {link} - depending on size, it may require some time")
        download_file(link)
    except Exception as e:
        log.error(f"Some unfortunate error has happend: {e}")
        print("Couldnt download the files :( Please double-check your internet connection and try again")
        continue #used to sys.exit(1), but it would be bad to break everything if just one file fails. May do something about that later

print("Done")
exit(0)
