#!/usr/bin/python3

import requests
import datetime
import os
from ftplib import FTP
import configparser
import sys

config = configparser.ConfigParser(allow_no_value=True)
config.optionxform = str        
config.read('download_lpdaac.ini')

def get_inventory(product, version, bbox=None, lat=None, lon=None, julianrange=None, years=None, date=None, only_ftp=False):       
    query = 'product={product}'
    if version:
        query += '&version={version}'
    if lat and lon:
        query += '&lat={lat}&lon={lon}'
    if bbox:
        query += '&bbox={bbox}'
    if date:
        date = date.strftime('%Y-%m-%d')
        query += '&date={date}'
    if years:
        query += '&years={years}'
    if julianrange:
        query += '&julianrange={julianrange}'
    query = query.format(product=product, version=version, lat=lat, lon=lon, bbox=bbox, date=date, years=years, julianrange=julianrange)            
    print(query)
    url = 'https://lpdaacsvc.cr.usgs.gov/services/inventory?{query}&output=json'    
    url = url.format(query=query)     
    ret = requests.get(url)        
    json = ret.json()    
    print(json)
    json.remove('')
    if only_ftp:
        json = [url for url in json if 'ftp://' in url]    
    return json


def bbox(lat_min, lat_max, lon_min, lon_max):
    bbox = '{lon_min},{lat_min},{lon_max},{lat_max}'    
    bbox = bbox.format(lon_min=lon_min, lat_min=lat_min, lon_max=lon_max, lat_max=lat_max)
    return bbox    


def download_list(file_list, out_folder):
    for url in file_list:                 
        print(url)
        download_file(url, out_folder)
        
    
def get_remote_size(ftp, directory, file_name):
    size = ftp.size(directory+file_name)    
    return size
   
    
def get_local_size(file_name, out_folder):
    size = os.stat(out_folder+file_name).st_size
    return size
        
        
def download_file(url, out_folder):    
    if 'ftp://' in url:
        download_ftp(url, out_folder)   
    else:
        download_https(url, out_folder)
            
            
def download_ftp(url, out_folder):    
    host = url.split('//')[1].split('/')[0]    
    file_name = url.split('/')[-1]       
    directory = url.split(host)[-1].split(file_name)[0]       
    
    ftp = FTP(host)
    ftp.login()
    ftp.cwd(directory)        
    
    if file_already_exists(file_name, out_folder):        
        local_size = get_local_size(file_name, out_folder)
        remote_size = get_remote_size(ftp, directory, file_name)        
        if local_size == remote_size: 
            return None    
    
    with open(out_folder + file_name, 'wb') as outfile:
        cmd = 'RETR {file_name}'.format(file_name=file_name)
        ftp.retrbinary(cmd=cmd, callback=outfile.write)
    
                
def download_https(url, out_folder):   
    user = config['global']['user']
    password = config['global']['password'] 
    file_name = url.split('/')[-1]
    if file_already_exists(file_name, out_folder):
        return None    
    ret = requests.get(url, auth=(user, password), cookies={'DATA' :'WaCByZg9BGcAAC1zpHEAAADA'})
    save_file(ret, file_name, out_folder)
        

def file_already_exists(file_name, out_folder):
    if file_name in os.listdir(out_folder):        
        return True
    else:
        return False
        

def save_file(ret, file_name, folder):
    with open(folder + '/' + file_name, 'wb') as f:
        for chunk in ret.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)

def load_config():
    pass

if __name__ == '__main__':
    config_name = config['global']['config']    
    machine = config['global']['machine']
    out_folder = config['out_folder'][machine]    
    version = config[config_name]['version']
    lat_min= config[config_name]['lat_min']
    lat_max= config[config_name]['lat_max']
    lon_min = config[config_name]['lon_min']
    lon_max = config[config_name]['lon_max']
    julianrange = config[config_name]['julianrange']
    years = config[config_name]['years']         
    bbox = bbox(lat_min, lat_max, lon_min, lon_max)        
    product = config[config_name]['product']         
    
    inventory = get_inventory(product=product, version=version, bbox=bbox, julianrange=julianrange, years=years, only_ftp=True)    
    download_list(inventory, out_folder)
    
    product = 'MOD03'
    inventory = get_inventory(product=product, version=version, bbox=bbox, julianrange=julianrange, years=years, only_ftp=True)   
    download_list(inventory, out_folder)
