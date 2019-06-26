import os
import csv
import subprocess
import xml.etree.ElementTree as ET
import urllib
import urllib2
import wget
import requests
import time


class LadswebFile:
    def __init__(self, file_id=None, url=None):
        self.file_id = file_id
        self.file_name = None
        if url is not None:
            self.url = url
        else:
            self.get_url()
        self.get_file_name()        
        self.checksum = None
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
        ret = requests.get(api+query)
        root = ET.fromstring(ret.text)
        for child in root[0]:
            key = child.tag.split('}')[1]
            value = child.text            
            self.properties[key] = value     
     
    def download_urllib1(self, file_path):
        urllib.request.urlretrieve(self.url, filename=file_path)                        
            
    def download_urllib2(self, file_path):
        file_data = urllib2.urlopen(self.url)           
        data = file_data.read()
        with open(file_path, 'wb') as out_file:
            out_file.write(data)
            
    def download_requests(self, file_path):
        ret = request.get(self.url)
        with open(file_path, 'wb') as out_file:
            out_file.write(ret.contents)
            
    def download_wget(self, file_path):        
        wget.download(self.url, file_path)
        
    def download(self, folder):
        file_path = folder + '/' + self.file_name        
        try:
            self.download_wget(file_path)        
        except :
            print('download failed, trying again')
            time.sleep(2)
            self.download(folder)
                    
    def delete(self, folder):
        os.remove(folder + self.file_name)
    
    def verified_download(self, folder):
        if not self.already_downloaded(folder):
            self.download(folder)
        if not self.checksum_is_correct(folder):
            print('Checksums dont match. Retrying Download')
            time.sleep(1)
            self.delete(folder)            
            self.verified_download(folder)
            
    def checksum_is_correct(self, folder):
        self.calc_checksum(folder)
        checksum_local = self.checksum
        checksum_remote = int(self.properties['checksum'])        
        return checksum_local==checksum_remote
        
    def calc_checksum(self, folder):
        ret = subprocess.check_output(['cksum', folder+self.file_name])        
        self.checksum = int(ret.split()[0])
        
    def already_downloaded(self, folder):
        already_downloaded = os.path.isfile(folder + self.file_name)
        if already_downloaded:
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
