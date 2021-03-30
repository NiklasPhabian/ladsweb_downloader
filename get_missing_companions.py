#!/usr/bin/python3

import requests
import time
import glob
import os
import ladsweb_file
import fnmatch
import xml
import xml.etree.ElementTree as ET
import argparse


def companion_missing(granule_name, companion_names, granule_pattern, companion_pattern):
    name_trunk = granule_name.split('.')[0:-2]
    pattern = '.'.join(name_trunk).replace(granule_pattern, companion_pattern) + '*'
    companion_name = fnmatch.filter(companion_names, pattern)
    if len(companion_name) == 0:
        return True


def get_lonely_granules(granule_folder, companion_folder, granule_pattern, companion_pattern):
    granule_names = sorted(glob.glob(os.path.expanduser(granule_folder) + granule_pattern + '*'))
    companion_names = sorted(glob.glob(os.path.expanduser(companion_folder) + companion_pattern + '*'))
    missing = []
    for granule_name in granule_names:
        if companion_missing(granule_name, companion_names, granule_pattern, companion_pattern):
            granule_name = granule_name.split('/')[-1]            
            missing.append(granule_name)
            print('missing companion for: ' + granule_name)
    return missing


def parse_granule_name(granule_name):
    parts = granule_name.split('.')
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


def get_companion_id(companion_pattern, collection, year, day, hour):
    # Help: https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/lws-classic/api.php
    host = 'https://modwebsrv.modaps.eosdis.nasa.gov'
    api = '/axis2/services/MODAPSservices/searchForFilesByName?'    
    if companion_pattern in ['VJ103DNB', 'VNP03DNB']:
        stub = '.A'
    query = 'collection={collection}&pattern={companion_pattern}{stub}{year}{day}.{hour}*'
    query = query.format(collection=collection, companion_pattern=companion_pattern, stub=stub, year=year, day=day, hour=hour)    
    url = host+api+query
    print(url)
    ret = download(url)
    file_id = xml2file_id(ret)
    return file_id
   
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Finds and retrieves missing geolocation companion files')
    parser.add_argument('--granule_folder', type=str, help='Granule folder (e.g. location of VNP02*)', required=True)
    parser.add_argument('--companion_folder', type=str, help='Companion folder (e.g. location of VNP03*). Default: granule_folder')
    
    parser.add_argument('--granule_pattern', type=str, help='Pattern of the granule name (e.g. VNP02DNB)', required=True)
    parser.add_argument('--companion_pattern', type=str, help='Pattern of the companion name (e.g VNP03DNB)', required=True)
    
    parser.add_argument('--download', help='toggle if missing companions should be downloaded', action='store_true')
    parser.add_argument('--collection', type=str, help='collection of the companion file')
    
    args = parser.parse_args()
   
    if args.companion_folder is None:
        args.companion_folder = args.granule_folder 
    
    if args.download and not args.collection:
        print('Need to specify companion collection if attempting to download \n')
        print(parser.print_help())
        quit()
            
        
    lonely_granules = get_lonely_granules(granule_folder=args.granule_folder, companion_folder=args.companion_folder, 
                                          granule_pattern=args.granule_pattern, companion_pattern=args.companion_pattern)
    
    print('{n} missing companions'.format(n=len(lonely_granules)))
    if args.download:
        for lonely_granule in lonely_granules:
            print('Getting companion for {}'.format(lonely_granule))
            year, day, hour = parse_granule_name(lonely_granule)
            file_id = get_companion_id(args.companion_pattern, args.collection, year, day, hour)
            lw_file = ladsweb_file.LadswebFile(file_id=file_id)
            lw_file.get_url()
            lw_file.get_file_name()
            lw_file.get_properties()
            lw_file.verified_download(args.companion_folder)
        
        
