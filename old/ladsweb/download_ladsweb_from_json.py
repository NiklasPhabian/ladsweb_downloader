#!/usr/bin/python3  
import json
import urllib.request
import time
import sys


host = 'https://ladsweb.modaps.eosdis.nasa.gov'


def load_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    urls = []    
    for granule_id in data:        
        if not granule_id == 'query':
            urls.append(data[granule_id]['url'])
    return urls
    
    
def download(out_folder, urls):
    for rel_url in urls:        
        url = host+rel_url
        print(url)
        filename = out_folder + url.split('/')[-1]        
        success = False
        while not success:
            try:
                urllib.request.urlretrieve(url, filename=filename)
                success = True
            except urllib.error.HTTPError:
                print('failed, trying again')
                time.sleep(2)


def save_file(ret, file_name):
    with open(out_folder + file_name, 'wb') as f:
        for chunk in ret.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)
                    
    
    
if __name__ == '__main__':     
    json_file = sys.argv[1]
    out_folder = sys.argv[2]            
    urls = load_json(json_file)
    print('total {n_hdf} files'.format(n_hdf=len(urls)))
    download(out_folder, urls)
