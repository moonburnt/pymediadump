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
from urllib.parse import urlparse
from os.path import join

# Custom logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#log.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
log.addHandler(handler)

class PyMediaDump:
    def __init__(self):
        log.debug(f"Initializing network session")
        self.session = requests.Session()

    def get_page_source(self, link):
        '''Receives str(webpage url), returns raw content of said page'''
        log.debug(f"Fetching page content from {link}")
        page = self.session.get(link, timeout = 100)
        page.raise_for_status()

        #this part may be done better, as it will break if you will try to fetch multiple pages before downloading
        url = urlparse(link)
        self.referer = f'{url.scheme}://{url.netloc}/'

        log.debug(f"Saved {self.referer} as referer for future downloads")

        return page.text

    def download_file(self, link, downloads_directory):
        '''Receives str(link to download file) and str(path to download directory), saves file to dir'''
        log.debug(f"Fetching file from {link}")
        if self.referer:
            log.debug(f"Found referer, will use it to download file: {self.referer}")
            data = self.session.get(link, timeout = 100, headers={'referer': self.referer})
        else:
            log.debug("Didnt find referer, will try to download without it")
            data = self.session.get(link, timeout = 100)
        data.raise_for_status()

        log.debug(f"Trying to determine filename")
        fn = link.rsplit('/', 1) #this aint perfect, coz link may contain some garbage such as id after file name
        filename = str(fn[1])
        save_path = join(downloads_directory, filename)

        log.debug(f"Attempting to save file as {save_path}")
        with open(save_path, 'wb') as f:
            f.write(data.content)
        log.info(f"Successfully saved {filename} as {save_path}")

    def get_download_links(self, page, search_rule):
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
