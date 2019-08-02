import os
import csv
import subprocess
import xml.etree.ElementTree as ET
import xml
import urllib
import wget
import requests
import time
from multiprocessing.pool import Pool


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
        api = 'https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/getFileProperties?'
        query = 'fileIds={file_id}'.format(file_id=self.file_id)
        try:
            ret = requests.get(api+query)
            root = ET.fromstring(ret.text)
        except xml.etree.ElementTree.ParseError:
            print('cannot parse properties')
            print(ret.status_code)
            print(ret.text)
        for child in root[0]:
            key = child.tag.split('}')[1]
            value = child.text            
            self.properties[key] = value     
            
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
        r = requests.get(self.url, headers=headers, stream=True) 
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
            
    def download_requests(self):
        ret = requests.get(self.url)
        with open(self.file_path, 'wb') as out_file:
            out_file.write(ret.content)
            
    def download_wget(self):        
        wget.download(self.url, self.file_path)
        
    def download(self, folder):
        self.file_path = folder + '/' + self.file_name        
        try:
            self.download_requests()        
        except Exception as e:
            print(e)
            print('download failed, trying again')
            time.sleep(2)
            self.download(folder)
<<<<<<< HEAD
   
=======
                    
    def delete(self):
        os.remove(self.file_path)
    
>>>>>>> 0ce71531d0caf64eefeef39758485a6335110e0d
    def verified_download(self, folder):
        self.file_path = folder + '/' + self.file_name
        if not self.already_downloaded(folder):
            self.download(folder)
        while not self.checksum_is_correct():
            print('Checksums dont match. Retrying Download')
            time.sleep(1)
<<<<<<< HEAD
            self.delete(folder)            
            self.verified_download(folder)

    def delete(self, folder):
        os.remove(folder + self.file_name)
        
    def checksum_is_correct(self, folder):
        self.calc_checksum(folder)
=======
            self.delete()            
            self.download(folder)
            
    def checksum_is_correct(self):
        self.calc_checksum()
>>>>>>> 0ce71531d0caf64eefeef39758485a6335110e0d
        checksum_local = self.checksum
        checksum_remote = int(self.properties['checksum'])        
        return checksum_local==checksum_remote
        
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
    lw_file = LaadswebFile(file_id=2777472980)
    lw_file.get_properties()            
    lw_file.get_file_name()
    lw_file.verify_checksum(folder='')    
    lw_file.download('')
