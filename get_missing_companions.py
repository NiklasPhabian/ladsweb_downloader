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


def get_granule_paths(granule_folder, granule_pattern, filter_term=None):
    granule_paths = sorted(glob.glob(os.path.expanduser(granule_folder) + '/' + granule_pattern + '*'))
    if filter_term:
        granule_paths = list(filter(lambda name: filter_term not in name, granule_paths))
    return granule_paths
        
        
def get_companion_paths(companion_folder, companion_pattern):
    companion_paths = sorted(glob.glob(os.path.expanduser(companion_folder) + '/' + companion_pattern + '*'))
    return companion_paths


def paths2stumps(paths):
    stumps = []
    for path in paths:
        name = path.split('/')[-1]     
        name_parts = name.split('.')
        date = name_parts[1]
        time = name_parts[2]    
        stump = date + '.' + time
        stumps.append(stump)
    return stumps


def get_lonely_granules(granule_paths, companion_paths):
    granule_stumps = paths2stumps(granule_paths)
    companion_stumps = paths2stumps(companion_paths)
    missing_stumps = list(set(granule_stumps) - set(companion_stumps))
    return missing_stumps
                          

def download(url):
    ret = requests.get(url)
    while not ret.status_code == 200:
        print('{code} - failed to get {url}. Retrying'.format(url=url, code=ret.status_code))
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


def make_search_url(companion_pattern, collection, stump):
    # Help: https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/lws-classic/api.php
    host = 'https://modwebsrv.modaps.eosdis.nasa.gov'
    api = '/axis2/services/MODAPSservices/searchForFilesByName?'            
    query = 'collection={collection}&pattern={companion_pattern}.{stump}*'
    query = query.format(collection=collection, companion_pattern=companion_pattern, stump=stump)    
    url = host+api+query
    return url
   
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Finds and retrieves missing geolocation companion files')
    parser.add_argument('--granule_folder', type=str, help='Granule folder (e.g. location of VNP02*)', required=True)    
    parser.add_argument('--granule_pattern', type=str, help='Pattern of the granule name (e.g. VNP02DNB)', required=True)
    parser.add_argument('--filter_term', type=str, help='Exclude granules containing this filter term', required=False, default=None)
    
    parser.add_argument('--companion_folder', type=str, help='Companion folder (e.g. location of VNP03*). Default: granule_folder')
    parser.add_argument('--companion_pattern', type=str, help='Pattern of the companion name (e.g VNP03DNB)', required=True)
    
    parser.add_argument('--download', help='toggle if missing companions should be downloaded', action='store_true')
    parser.add_argument('--collection', type=str, help='collection of the companion file')
    
    #parser.add_argument('--both_ways', help='toggle if companions with missing granules should be found', action='store_true')
    
    args = parser.parse_args()
   
    if args.companion_folder is None:
        args.companion_folder = args.granule_folder 
    
    if args.download and not args.collection:
        print('Need to specify companion collection if attempting to download \n')
        print(parser.print_help())
        quit()
        
    granule_paths = get_granule_paths(granule_folder=args.granule_folder, 
                                      granule_pattern=args.granule_pattern, 
                                      filter_term=args.filter_term)
            
    companion_paths = get_companion_paths(companion_folder=args.companion_folder,
                                          companion_pattern=args.companion_pattern)
    
    
    stumps = get_lonely_granules(granule_paths, companion_paths)
    
    print('{n} missing companions'.format(n=len(stumps)))
    if args.download:        
        for stump in stumps:            
            print('#######################')
            granule_name = glob.glob(args.granule_folder + '/' +args.granule_pattern + '.' + stump + '*')[0]
            print('Getting companion for {}'.format(granule_name))
            url = make_search_url(args.companion_pattern, args.collection, stump)
            print('searching {}'.format(url))            
            ret = download(url)
            file_id = xml2file_id(ret)
            if file_id == 'No results':
                print('ERROR: did not find file id. Exiting')
                break
            print('found file id {}'.format(file_id))
            lw_file = ladsweb_file.LadswebFile(file_id=file_id)
            lw_file.get_url()
            print('Found companion at: {}'.format(lw_file.url))
            lw_file.get_file_name()
            lw_file.get_properties()
            lw_file.verified_download(args.companion_folder)
                
