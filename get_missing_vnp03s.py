#!/usr/bin/python3

import pandas
import requests
import time
import glob
import os
import ladsweb_file
import fnmatch
import xml
import xml.etree.ElementTree as ET


def companion_missing(vnp02_name, vnp03_names):
    name_trunk = vnp02_name.split('.')[0:-2]
    pattern = '.'.join(name_trunk).replace('VNP02DNB', 'VNP03DNB') + '*'
    vnp03_name = fnmatch.filter(vnp03_names, pattern)
    if len(vnp03_name) == 0:
        return True


def get_lonely_vnp02s(folder):
    vnp02_names = sorted(glob.glob(os.path.expanduser(folder) + 'VNP02DNB*'))
    vnp03_names = sorted(glob.glob(os.path.expanduser(folder) + 'VNP03DNB*'))
    missing = []
    for vnp02_name in vnp02_names:
        if companion_missing(vnp02_name, vnp03_names):
            vnp02_name = vnp02_name.split('/')[-1]            
            missing.append(vnp02_name)
            print('missing companion for: ' + vnp02_name)
    return missing


def find_in_json(json, pattern):
    for row in json:        
        if search_pattern in row['name']:
            return row['name']
    return None


def parse_vnp02_name(vnp02_name):
    parts = vnp02_name.split('.')
    year = parts[1][1:5]
    day = parts[1][5:9]
    hour = parts[2]
    return year, day, hour


def download(url):
    ret = requests.get(url)
    while not ret.status_code == 200:
        print('{code} - failed to get {url} download. Retrying'.format(url=url, code=ret.status_code))
        time.sleep(1)                            
        ret = requests.get(url)            
    return ret
    
    
def xml2file_id(ret):         
    try:
        root = ET.fromstring(ret.text)                
        file_id = root[0].text
    except xml.etree.ElementTree.ParseError:
        print('cannot parse properties') 
    return file_id


def get_vnp03_id(year, day, hour):
    host = 'https://modwebsrv.modaps.eosdis.nasa.gov'
    api = '/axis2/services/MODAPSservices/searchForFilesByName?'    
    query = 'collection=5110&pattern=VNP03DNB.A{year}{day}.{hour}*'
    query = query.format(year=year, day=day, hour=hour)
    url = host+api+query
    ret = download(url)
    file_id = xml2file_id(ret)
    return file_id
   
    
if __name__ == '__main__':
    folder = '/home/griessbaum/night_lights/schiss_download/carribean/vnp02/'
    lonely_vnp02s = get_lonely_vnp02s(folder)
    print('{n} missing companions'.format(n=len(lonely_vnp02s)))
    for vnp02_name in lonely_vnp02s:
        print('Getting companion for {}'.format(vnp02_name))
        year, day, hour = parse_vnp02_name(vnp02_name)
        file_id = get_vnp03_id(year, day, hour)
        lw_file = ladsweb_file.LadswebFile(file_id=file_id)
        lw_file.get_url()
        lw_file.get_file_name()
        lw_file.get_properties()
        lw_file.verified_download(folder)
        
        
