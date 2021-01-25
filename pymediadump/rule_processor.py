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

# Attempt to move everything related to processing content with rules to separate file

import logging
from re import findall, match

log = logging.getLogger(__name__)

def find_data(page, find_rule):
    '''Receives str(webpage's html content) and str(find rule(content of rulefile's "find" key)), returns list(matching webpage parts)'''
    log.debug(f"Applying {find_rule} find rule to the provided html")
    matching_data = findall(find_rule, page) #this will create list with all matching entires

    log.debug(f"Found the following data that match {find_rule}: {matching_data}")

    return matching_data

def exclude_data(data, exclusion_rule):
    '''Receives list(data to process) and str(rule to apply). Remove all entries from list, that match rule's regular expression'''

    log.debug(f"Applying {exclusion_rule} exclusion rule to {data} entries")
    fine_data = []
    for item in data:
        if match(exclusion_rule, item):
            log.debug(f"{item} matches exclusion rule {exclusion_rule}, ignoring")
        else:
            log.debug(f"{item} is fine, adding to list")
            fine_data.append(item)

    log.debug(f"Data without unwanted content is the following: {fine_data}")

    return fine_data

def clear_data(data, clearing_rule):
    '''Receives list(data to process) and str(rule to use to clear it up). Remove parts that match rule from each list's entry, then returns list(cleared data)'''

    log.debug(f"Applying {clearing_rule} clear rule to {data} entries")
    clean_data = []
    for item in data:
        log.debug(f"Cleaning up {item}")

        cl = item.replace(clearing_rule, "")
        clean_data.append(cl)

    log.debug(f"Data with cleared up content is the following: {clean_data}")

    return clean_data

def replace_data(data, replacing_rule):
    '''Receives list(data to process) and str(rule to use to replace stuff). Replace parts that match rule from each list's entry accordingly, then returns list(fixed data)'''

    log.debug(f"Processing replacing rule {replacing_rule}")
    find, replace = replacing_rule.split(" >> ")

    log.debug(f"Trying to process data, replacing {find} with {replace}")

    replaced_data = []
    for item in data:
        log.debug(f"Replacing stuff in {item}")

        rd = item.replace(find, replace)
        replaced_data.append(rd)

    log.debug(f"Data with replaced content is the following: {replaced_data}")

    return replaced_data

def rule_processor(html_source, rule):
    '''Receives str(html source of web page) and dic(entire content of rule file to apply to it). Applies all matching filters and return list of ready-to-download entries'''

    log.debug(f"Trying to process data, based on rule {rule}")

    data = []
    for find_rule in rule['Rules']['Find']:
        log.debug(f"Trying to find data, based on {find_rule}")
        try:
            data = find_data(html_source, find_rule)
            log.debug(f"Found following data: {data}")
        except Exception as e:
            log.error(f"Some unfortunate error has happend: {e}")
            log.debug(f"No data matching find rule {rule} has been found, skipping")
            continue

    if not data:
        log.warning("No valid data has been found!")
        return

    if rule['Rules']['Exclude']:
        for exclude_rule in rule['Rules']['Exclude']:
            log.debug(f"Trying to exclude data, based on {exclude_rule}")
            try:
                ex = exclude_data(data, exclude_rule)
            except Exception as e:
                log.error(f"Some unfortunate error has happend: {e}")
                log.debug(f"Couldnt apply exclusion rule {rule}, skipping")
                continue
            else:
                data = ex

    if rule['Rules']['Clear']:
        for clear_rule in rule['Rules']['Clear']:
            log.debug(f"Trying to clear data, based on {clear_rule}")
            try:
                cd = clear_data(data, clear_rule)
            except Exception as e:
                log.error(f"Some unfortunate error has happend: {e}")
                log.debug(f"Couldnt apply clear rule {rule}, skipping")
                continue
            else:
                data = cd

    if rule['Rules']['Replace']:
        for replace_rule in rule['Rules']['Replace']:
            log.debug(f"Trying to replace data, based on {replace_rule}")
            try:
                rd = replace_data(data, replace_rule)
            except Exception as e:
                log.error(f"Some unfortunate error has happend: {e}")
                log.debug(f"Couldnt apply replace rule {rule}, skipping")
                continue
            else:
                data = rd

    log.debug(f"Gathered following data: {data}")
    return data
