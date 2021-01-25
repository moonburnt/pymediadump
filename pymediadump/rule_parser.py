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

# Attempt to move everything related to fetching content from rule files to separate script

import logging
from os import listdir
from os.path import isfile, join
from re import match
import configparser

log = logging.getLogger(__name__)

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

def verify_rules(files):
    '''Receives list(paths to rule files), returns list(content of valid rule files)'''
    known_rules = []
    for item in files:
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
        log.debug(f"Checking rule {item}")
        supported_urls = item['Main']['URLs']
        for url in supported_urls:
            url = '(|http://|https://)'+url #avoiding necessity to provide protocol info in rule's URL
            log.debug(f"Comparing {link} with {url}")
            try:
                if match(url, link):
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

def rule_parser(configfile):
    '''Receives str(path to rule.ini file), returns dictionary with known data entries from it'''
    log.debug(f"Attempting to parse {configfile}")
    cp = configparser.ConfigParser()
    cp.read(configfile)

    log.debug(f"Processing the Main category")
    main = {}
    main['Name'] = cp['Main']['Name']
    main['Description'] = cp['Main']['Description']
    main['URLs'] = cp['Main']['URLs'].split(" | ")
    log.debug(f"Content of Main is {main}")

    log.debug(f"Processing the Rules category")
    rules = {}
    rules['Find'] = cp['Rules']['Find'].split(" | ")
    try:
        rules['Exclude'] = cp['Rules']['Exclude'].split(" | ")
    except:
        rules['Exclude'] = None #setting unmatching rules to "None" during parse process to avoid dealing with it later
    try:
        rules['Clear'] = cp['Rules']['Clear'].split(" | ")
    except:
        rules['Clear'] = None
    try:
        rules['Replace'] = cp['Rules']['Replace'].split(" | ")
    except:
        rules['Replace'] = None
    log.debug(f"Content of Rules is {rules}")

    log.debug(f"Turning complete data into dictionary")
    data = {}
    data['Main'] = main
    data['Rules'] = rules
    log.debug(f"Complete dictionary of known data of {configfile} is the following: {data}")

    return data
