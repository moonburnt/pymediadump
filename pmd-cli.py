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

import logging
import argparse
from os import makedirs
from sys import exit
import configparser
import pymediadump
from time import sleep

DEFAULT_DOWNLOAD_DIRECTORY="./Downloads"
pmd = pymediadump.PyMediaDump()

# Custom logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
log.addHandler(handler)

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
    page_html = pmd.get_page_source(DOWNLOAD_URL)
except Exception as e:
    log.error(f"Some unfortunate error has happend: {e}")
    print(f"Couldnt fetch provided url. Are you sure your link is correct and you have internet connection?")
    exit(1)

try:
    links = pmd.get_download_links(page_html, RULESET_FIND)
except Exception as e:
    log.error(f"Some unfortunate error has happend: {e}")
    print("Couldnt find download link :( Are you sure this link should contain supported file type?")
    exit(1)

sleep(10)

for link in links:
    try:
        print(f"Downloading the file from {link} - depending on size, it may require some time")
        pmd.download_file(link, DOWNLOAD_DIRECTORY)
        sleep(10)
    except Exception as e:
        log.error(f"Some unfortunate error has happend: {e}")
        print("Couldnt download the files :( Please double-check your internet connection and try again")
        continue #used to be sys.exit(1), but it would be bad to break everything if just one file fails. May do something about that later

print("Done")
exit(0)
