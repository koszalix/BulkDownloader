#!/bin/python3
import argparse
from urllib import request
from urllib.error import URLError


class Parser:

    def __init__(self):
        self.url = ""
        self.start_idx = 0
        self.stop_idx = 0
        self.cache_file = ''
        self.extension = '.pdf'

        parser = argparse.ArgumentParser()

        parser.add_argument('--url', help="url to download, with file name without extension and number")
        parser.add_argument('--start', help="start index", required=False)
        parser.add_argument('--stop', help="stop index", required=False)
        parser.add_argument('--cache', help='download cache file')
        args = parser.parse_args()

        self.url = args.url
        self.start_idx = args.start
        self.stop_idx = args.stop
        self.cache_file = args.cache


class Cache:

    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.saved_idx = []
        self.to_save = []

    def read_from_dsk(self):
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


class Downloader:

    def __init__(self, prs: Parser, chc: Cache):
        self.parser = prs
        self.cache = chc

    def run(self):
        for file_id in range(int(self.parser.start_idx), int(self.parser.stop_idx)+1):
            if not self.cache.is_idx_in_cache(file_id):
                url = self.parser.url + str(file_id) + self.parser.extension
                print('Downloading:', url)
                try:
                    request.urlretrieve(url=url, filename=str(file_id)+self.parser.extension)
                    self.cache.append_to_cache(idx=file_id)
                    print("Success")
                except URLError:
                    print("Failed")


class App:

    def __init__(self):
        self.parser = Parser()
        self.cache = Cache(self.parser.cache_file)
        self.cache.read_from_dsk()
        self.downloader = Downloader(prs=self.parser, chc=self.cache)

    def run(self):
        self.downloader.run()


# TODO: Interact with kill signal, cache size

if __name__ == '__main__':
    App = App()
    App.run()