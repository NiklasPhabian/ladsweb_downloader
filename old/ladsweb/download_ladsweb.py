#!/usr/bin/python3  
import json
import urllib.request
import requests
import time
import sys
import xml.etree.ElementTree as ET


def search_files(product, collection, start, stop, north, south, west, east, dnb='DNB'):
    api = 'https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles?'
    query = 'product={product}&collection={collection}&'\
            'start={start}&stop={stop}'\
            '&north={north}&south={south}&west={west}&east={east}&coordsOrTiles=coords&'\
            'dayNightBoth={dnb}'
    query = query.format(product=product, collection=collection, 
                         start=start, stop=stop, 
                         north=north, south=south, west=west, east=east, 
                         dnb=dnb)    
    ret = requests.get(api+query)
    root = ET.fromstring(ret.text)
    file_ids = []
    for child in root:
        file_ids.append(child.text)
    return file_ids


def get_file_urls(file_ids):
    file_ids_string = ','.join(file_ids)
    print(file_ids_string)
    api = 'https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/getFileUrls?'
    query = 'fileIds={file_ids}'.format(file_ids=file_ids_string)                
    ret = requests.get(api+query)    
    root = ET.fromstring(ret.text)    
    urls = []
    for child in root:        
        urls.append(child.text)
    return urls

    
def download_hdf(urls, out_folder):           
    filename = out_folder + url.split('/')[-1]        
    success = False
    while not success:
        try:
            urllib.request.urlretrieve(url, filename=filename)
            success = True
        except urllib.error.HTTPError:
            print('failed, trying again')
            time.sleep(2)


def read_cmdline():
    try: 
        product = sys.argv[1]  
        collection = sys.argv[2]  
        start = sys.argv[3]  
        stop = sys.argv[4]  
        north = sys.argv[5]  
        south = sys.argv[6]  
        west = sys.argv[7]  
        east = sys.argv[8]      
        params = {'product': product, 'collection': collection, 'start': start, 'stop': stop, 'north': north, 'south': south, 'west': west, 'east': east}
        out_folder = sys.argv[9]               
    except IndexError: 
        print('not all inputs specified.')
        print('specifiy them as: download_ladsweb.py product collection start stop north south west east out_folder')
        print('e.g. ./download_ladsweb.py MYD09 6 2019-01-01 2019-01-02 40 30 -80 -70 .')
        sys.exit()
    return params, out_folder
    
              
if __name__ == '__main__':         
    #file_ids = search_files(product='MYD09', collection=str('6'), start='2019-01-01', stop='2019-01-02', north=40, south=30, west=-80, east=-70) 
    params, out_folder = read_cmdline()
    file_ids = search_files(**params)    
    urls = get_file_urls(file_ids)
    for url in urls:
        print(url)
        download_hdf(url, out_folder)
    
    
    
