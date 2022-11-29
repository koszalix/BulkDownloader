#!/bin/python3
import argparse
import urllib.parse
from urllib import request
from urllib.error import URLError

from datetime import datetime
import time
import requests
import os.path
import os
from html.parser import HTMLParser


class Parser:

    def __init__(self):
        self.url = ""
        self.cache_file = ''
        self.extension = '.pdf'
        self.sleep_after = -1
        self.sleep_time = 0
        self.output_directory = '.'

        parser = argparse.ArgumentParser()

        parser.add_argument('--url', help="url to download")
        parser.add_argument('--cache', help='download cache file')
        parser.add_argument('--output-directory', help="", required=False, default='')

        parser.add_argument('--sleep-after', help='sleep for some time after N downloads', required=False, type=int,
                            default=-1)
        parser.add_argument('--sleep-time', help="sleep time", required=False, default=-1, type=int)

        args = parser.parse_args()

        self.url = args.url
        self.cache_file = args.cache
        self.sleep_time = args.sleep_time
        self.sleep_after = args.sleep_after
        self.output_directory = args.output_directory


class Cache:

    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.saved_idx = []
        self.to_save = []

    def read_from_dsk(self):
        if not os.path.isfile(self.cache_file):
            with open(self.cache_file, 'x') as f:
                print("created cache file")

        with open(self.cache_file, 'r') as f:
            self.saved_idx = f.readlines()

        self.saved_idx = [n.replace('\n', '') for n in self.saved_idx]

    def save_to_dsk(self):
        with open(self.cache_file, 'a') as f:
            f.writelines(self.to_save)

    def append_to_cache(self, idx):
        self.to_save.append(str(idx) + '\n')
        if len(self.to_save) >= 10:
            self.save_to_dsk()

    def is_idx_in_cache(self, idx) -> bool:
        idx = str(idx)
        if idx in self.saved_idx or idx in self.to_save:
            return True
        return False


class LinkScaner:
    class SubParser(HTMLParser):
        def __init__(self, urls: list):
            super().__init__()
            self.data_href = False
            self.data_urls = urls

        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                self.data_href = True

        def handle_endtag(self, tag):
            if tag == 'a':
                self.data_href = False

        def handle_data(self, data):
            if self.data_href:
                self.data_urls.append(data)

    def __init__(self, url, extension):

        self.url = url
        self.file_urls = []
        self.extension = extension

        self.validate_last_slash()



    def validate_last_slash(self):
        if self.url[len(self.url)-1] != '/':
            self.url = self.url + '/'

    def find_urls(self, url) -> list:
        urls = []
        sub_parser = self.SubParser(urls)
        xhtml = requests.get(url)
        if xhtml.status_code != 200:
            return []

        lines = xhtml.text
        sub_parser.feed(lines)

        absolute_url = [url + str(urllib.parse.quote(sub_url)) for sub_url in urls]

        for to_rem in ['Name', 'Size', 'Description', 'Parent%20Directory', 'Last%20Modified']:
            if to_rem in absolute_url:
                absolute_url.remove(to_rem)

        return absolute_url

    def url_is_file(self, url) -> bool:
        know_extension = ['.gif', '.svg', '.png', '.jpg', '.tiff', '.tif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt',
                          '.mp4', '.avi', '.ppt', '.bin', '.pptx', '.odp', '.rar', '.Bin', '.zif', '.zip', '.dtapart','.wav', '.raw', '.log', '.7z', '.bmp', '.jpeg', '.rtf', '.db', '.part', '.djvu', '.exe', '.msi', '.asc']
        for ext in know_extension:
            if url[-len(ext):] == ext:
                return True
            if url[-len(ext):] == ext.upper():
                return True
        return False

    def find_files(self):
        self._start_time = datetime.now()
        to_scan = [self.url]

        for url in to_scan:
            urls = self.find_urls(url)

            for xurl in urls:

                if not self.url_is_file(xurl):
                    to_scan.append(xurl)
                else:
                    self.file_urls.append(xurl)
            to_scan.remove(url)

        print('Scanning finished in', datetime.now() - self._start_time)


class Downloader:
    def __init__(self, prs: Parser, chc: Cache, lks: LinkScaner):
        self.parser = prs
        self.cache = chc
        self.links = lks

    def get_file_name(self, url) -> str:
        cut = urllib.parse.unquote(url[len(self.parser.url):])
        return cut

    def get_directory_from_path(self, file):
        return file[0:[idx for idx, char in enumerate(file) if char == '/'][len([idx for idx, char in enumerate(file) if char == '/'])-1]]

    def prepare_path(self, path):
        if self.parser.output_directory[:-1] != '/':
            return self.parser.output_directory + path
        else:
            return self.parser.output_directory[:-1] + path

    def create_directory(self,directory):
        try:
            os.mkdir(directory)
        except FileNotFoundError:
            pass

    def run(self):
        for file in self.links.file_urls:
            fl = self.prepare_path(self.get_file_name(file))
            self.create_directory(self.get_directory_from_path(fl))
            # Download file

# godzina mija za godziną
# jesteś całkiem fajną świnią

class App:
    def __init__(self):
        self.parser = Parser()
        self.cache = Cache(self.parser.cache_file)
        self.link_scaner = LinkScaner(self.parser.url, self.parser.extension)
        self.link_scaner.find_files()
        self.downloader = Downloader(self.parser, self.cache, self.link_scaner)

        self.downloader.run()


if __name__ == '__main__':
    App = App()
