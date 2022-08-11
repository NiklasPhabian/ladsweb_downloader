import os
import csv
import subprocess
import xml.etree.ElementTree as ET
import xml
import urllib
import wget
import requests
import time
import configparser
from multiprocessing.pool import Pool


class SessionEarthData(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return


config = configparser.ConfigParser()
config.read('user.config')
username= config['user']['user']
password = config['user']['pwd']
session = SessionEarthData(username=username, password=password)


class LadswebFile:
    def __init__(self, file_id=None, url=None):
        self.file_id = file_id
        self.file_name = None
        self.file_path = None
        if url is not None:
            self.url = url
        else:
            self.get_url()
        self.get_file_name()
        self.checksum = None
        self.header = None
        self.properties = {}

    def get_url(self):
        api = 'https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/getFileUrls?'
        query = 'fileIds={file_id}'.format(file_id=self.file_id)
        ret = requests.get(api+query)
        root = ET.fromstring(ret.text)
        self.url = root[0].text

    def get_properties(self):
        ret = self.download_properties()
        try:
            root = ET.fromstring(ret.text)
        except xml.etree.ElementTree.ParseError:
            print('cannot parse properties')
        for child in root[0]:
            key = child.tag.split('}')[1]
            value = child.text
            self.properties[key] = value

    def download_properties(self):
        api = 'https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/getFileProperties?'
        query = 'fileIds={file_id}'.format(file_id=self.file_id)
        ret = requests.get(api+query)
        while not ret.status_code == 200:
            print('{code} - failed to download properties. Retrying'.format(code=ret.status_code))
            time.sleep(5)
            ret = requests.get(api+query)
        return ret

    def get_header(self):
        r = requests.head(self.url)
        self.header = r.headers

    def file_size(self):
        if self.header is None:
            self.get_header()
        return int(self.header['content-length'])

    def download_chunk_urllib(self, ranges):
        req = urllib.request.Request(self.url)
        req.headers['Range'] = 'bytes=%s-%s' % (ranges[0], ranges[1])
        return urllib.request.urlopen(req).read()

    def download_chunk_requests(self, ranges):
        headers = {'Range': 'bytes=%d-%d' % (ranges[0], ranges[1])}
        r = session.get(self.url, headers=headers, stream=True)
        return r.content

    def download_parallel(self, threads=4):
        chunk_size = int(self.file_size() / threads ) + 1
        ranges = []
        for start in range(0, self.file_size(), chunk_size):
            end = start + chunk_size-1
            ranges.append((start, end))
        with Pool(threads) as p:
            chunks = p.map(self.download_chunk_requests, ranges)
        with open(self.file_path, 'wb') as out_file:
            for chunk in chunks:
                out_file.write(chunk)

    def download_urllib(self):
        urllib.request.urlretrieve(self.url, filename=self.file_path)

    def download_wget(self):
        wget.download(self.url, self.file_path)

    def download_requests(self):
        ret = session.get(self.url, timeout=120)
        if not ret.status_code == 200:
            print('Didnt get a 200/OK, but {status_code} instead'.format(status_code=ret.status_code))
            print('URL was {url}'.format(url=self.url))
        elif 'text/html' in ret.headers['Content-Type']:
            print('Got an HTML response. Maybe not logged in?')
            title = ret.text.split('<title>')[1].split('</title>')[0]
            print('Hint: page title says "{title}"'.format(title=title))
        with open(self.file_path, 'wb') as out_file:
            out_file.write(ret.content)

    def download(self, folder):
        self.file_path = folder + '/' + self.file_name
        try:
            self.download_requests()
        except Exception as e:
            print(e)
            print('download failed, trying again')
            time.sleep(2)
            self.download(folder)

    def delete(self):
        os.remove(self.file_path)

    def verified_download(self, folder):
        self.file_path = folder + '/' + self.file_name
        if not self.already_downloaded(folder):
            self.download(folder)
        while not self.checksum_is_correct():
            print('Checksums dont match. Retrying Download')
            time.sleep(5)
            self.delete()
            self.download(folder)

    def checksum_is_correct(self):
        self.calc_checksum()
        checksum_local = self.checksum
        checksum_properties = int(self.properties['checksum'])
        return checksum_local==checksum_properties

    def calc_checksum(self):
        ret = subprocess.check_output(['cksum', self.file_path])
        self.checksum = int(ret.split()[0])

    def already_downloaded(self, folder):
        self.file_path = folder + '/' + self.file_name
        if os.path.isfile(self.file_path):
            print('file already downloaded. Skipping')
            return True
        else:
            return False

    def get_file_name(self):
        self.file_name = self.url.split('/')[-1]

    def __str__(self):
        return self.file_id + ',' + self.url

if __name__ == '__main__':
    ladsweb_file = LadswebFile(file_id=2777472981)
    ladsweb_file.get_file_name()
    ladsweb_file.get_properties()
    ladsweb_file.verified_download('.')
