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
from os import makedirs, listdir
from os.path import isfile, join
from sys import exit
import configparser
import pymediadump
from time import sleep
from re import match

DEFAULT_DOWNLOAD_DIRECTORY="./Downloads"
RULES_DIRECTORY = "./rules"
pmd = pymediadump.PyMediaDump()

# Custom logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
log.addHandler(handler)

def get_files(dirname):
    '''Receives str(path to directory with files), returns list(files in directory)'''
    log.debug(f"Attempting to parse directory {dirname}")
    directory_content = listdir(dirname)
    log.debug(f"Uncategorized content inside is: {directory_content}")

    files = []
    #for now we wont care about subdirectories and just skip them altogether
    for item in directory_content:
        log.debug(f"Processing {item}")
        itempath = join(dirname, item)
        if isfile(itempath):
            log.debug(f"{itempath} leads to file, adding to list")
            files.append(itempath)
        else:
            log.debug(f"{itempath} doesnt lead to file, ignoring")
            continue

    log.debug(f"Got following files in total: {files}")
    return files

def rule_parser(configfile):
    '''Receives str(path to rule.ini file), returns dictionary with known data entries from it'''
    log.debug(f"Attempting to parse {configfile}")
    cp = configparser.ConfigParser()
    cp.read(configfile)

    log.debug(f"Processing the Main category")
    main = {}
    main['Name'] = cp['Main']['Name']
    main['Description'] = cp['Main']['Description']
    main['URLs'] = cp['Main']['URLs']
    log.debug(f"Content of Main is {main}")

    log.debug(f"Processing the Rules category")
    rules = {}
    rules['Find'] = cp['Rules']['Find']
    try:
        rules['Exclude'] = cp['Rules']['Exclude']
    except:
        pass
    log.debug(f"Content of Rules is {rules}")

    log.debug(f"Turning complete data into dictionary")
    data = {}
    data['Main'] = main
    data['Rules'] = rules
    log.debug(f"Complete dictionary of known data of {configfile} is the following: {data}")

    return data

def get_rules(files):
    '''Receives list(paths to rule files), returns list(content of valid rule files)'''
    known_rules = []
    for item in known_rule_files:
        try:
            rule_content = rule_parser(item)
            known_rules.append(rule_content)
        except Exception as e:
            log.error(f"An error has happend while trying to process {item} rule: {e}")
            log.warning(f"Couldnt parse {item}, skipping")
            continue
    log.debug(f"Found following rules: {known_rules}")
    return known_rules

def get_matching_rules(link, rules):
    '''Receives str(url of webpage you are trying to parse) and list(content of rule files). Returns list(matching rule files)'''
    log.debug(f"Trying to find rules that can be applied to {link}")
    matching_rules = []

    for item in rules:
        log.debug(f"Checking {item}")
        supported_urls = item['Main']['URLs']
        try:
            if match(supported_urls, DOWNLOAD_URL):
                log.debug(f"{item} matches url {link}. Adding to list")
                matching_rules.append(item)
            else:
                print(f"{item} doesnt match, skipping")
                continue
        except Exception as e:
            log.error(f"An error has happend while trying to process {item} rule: {e}")
            log.warning(f"Couldnt parse {item}, skipping")
            continue

    log.debug(f"The following rules has matched {link} url: {matching_rules}")
    return matching_rules

# argparse shenanigans
ap = argparse.ArgumentParser()
ap.add_argument("url", help="URL of webpage, from which you want to download your media", type=str)
ap.add_argument("-d", "--directory", help="Custom path to downloads directory", type=str)
ap.add_argument("--dryrun", help="Dont download anything - just print what will be downloaded", action="store_true")
args = ap.parse_args()

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

print(f"Attempting to get list of available download rules")
known_rule_files = get_files(RULES_DIRECTORY)
valid_rules = get_rules(known_rule_files)
matching_rules = get_matching_rules(DOWNLOAD_URL, valid_rules)
if len(matching_rules) == 0:
    #for now we exit, later will need rework for multiple urls
    print(f"No matching rules has been found for url {DOWNLOAD_URL}. Abort")
    exit(1)

print(f"Attempting to download media from {DOWNLOAD_URL}")
try:
    page_html, page_referer = pmd.get_page_source(DOWNLOAD_URL)
except Exception as e:
    log.error(f"Some unfortunate error has happend: {e}")
    print(f"Couldnt fetch provided url. Are you sure your link is correct and you have internet connection?")
    exit(1)

download_links = []
for item in matching_rules:
    log.debug(f"Trying to find links, based on rule {item}")

    find_rule = item['Rules']['Find']
    log.debug(f"Found search rule: {find_rule}")
    try:
        exclude_rule = item['Rules']['Exclude']
        log.debug(f"Found exclude rule: {exclude_rule}")
    except:
        exclude_rule = None
        log.debug(f"No exclusion rule has been found")

    try:
        links = pmd.get_download_links(page_html, find_rule)
        log.debug(f"Found following download links: {links}")
        #download_links += links
    except Exception as e:
        log.error(f"Some unfortunate error has happend: {e}")
        log.debug(f"No links matching rule {item} has been found, skipping")
        continue

    #If Im right, this will execute as "else" without specifically saying it
    if exclude_rule:
        log.debug(f"Trying to exclude links, based on {exclude_rule}")
        for link in links:
            try:
                if match(exclude_rule, link):
                    log.debug(f"{link} matches exclusion rule {exclude_rule}, removing")
                    links.remove(link)
                else:
                    log.debug(f"{link} is fine, skipping")
                    continue
            except Exception as e:
                log.error(f"Some unfortunate error has happend: {e}")
                log.debug(f"No links matching exclude rule {item} has been found, skipping")

    log.debug(f"Adding following links to downloads list: {links}")
    download_links += links

for link in download_links:
    try:
        print(f"Downloading the file from {link} - depending on size, it may require some time")
        if not args.dryrun:
            sleep(3) #waiting a bit to avoid getting banned for spamming requests. I should probably turn this number into launch argument
            pmd.download_file(link, DOWNLOAD_DIRECTORY, referer=page_referer)
    except Exception as e:
        log.error(f"Some unfortunate error has happend: {e}")
        print("Couldnt download the files :( Please double-check your internet connection and try again")
        continue #used to be sys.exit(1), but it would be bad to break everything if just one file fails. May do something about that later

print("Done")
exit(0)
