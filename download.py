import requests
import datetime
import os
import bbox_africa as bbox
import json
from ladsweb_file import LadswebFile
from eta import ETA

def get_urls_long(product, collection, start, stop, bbox):
    # The api times out for ranges of more than a couple of months worth of tiles
    # Therefore we make iterative calls to the api
    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    stop = datetime.datetime.strptime(stop, '%Y-%m-%d').date()
    iterator = start    
    step = datetime.timedelta(days=100)
    while iterator + step < stop:
        get_urls(product=product, collection=collection, start=iterator, stop=iterator+step, bbox=bbox)
        iterator = iterator + step
    get_urls(product=product, collection=collection, start=iterator, stop=iterator+step, bbox=bbox)    


def get_urls(product, collection, start, stop, bbox):
    host = 'https://ladsweb.modaps.eosdis.nasa.gov'
    api = '/api/v1/files/'
    query = 'product={product}&collection={collection}&'\
            'dateRanges={start}..{stop}&'\
            'areaOfInterest=x{west}y{north},x{east}y{south}&'\
            'nightCoverage=true'
    query = query.format(product=product, collection=collection,
                         start=start, stop=stop,
                         north=bbox.north, south=bbox.south, west=bbox.west, east=bbox.east)
    print(host+api+query)
    ret = requests.get(host+api+query, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=600)    
    file_ids = ret.json().keys()
    for file_id in file_ids:
        url = host + ret.json()[file_id]['fileURL']
        with open('files.txt', 'a') as files_log:
            files_log.write(file_id + ',' + url + ',\n')
   
    
def download(folder):
    files = open('files.txt').readlines()
    eta = ETA(n_tot=len(files))
    for row in files[::-1]:        
        ladsweb_file = LadswebFile(file_id=row.split(',')[0], url=row.split(',')[1])                
        ladsweb_file.get_file_name()        
        eta.display(step='Downloading {name}'.format(name=ladsweb_file.file_name))
        ladsweb_file.get_properties()
        ladsweb_file.verified_download(folder)
        del files[-1]
        open('files.txt', 'w').writelines(files)
    
    
if __name__ == '__main__':
    folder = os.path.expanduser('download/viiirs/vnp02')
    start ='2012-01-01'
    stop = '2019-06-01'        
    get_urls_long(product='VNP02DNB', collection='5110', start=start, stop=stop, bbox=bbox)
    #get_urls_long(product='VNP03DNB', collection='5110', start=start, stop=stop, bbox=bbox)
    #get_urls_long(product='CLDMSK_L2_VIIRS_SNPP', collection='5110', start=start, stop=stop, bbox=bbox)
    #download(folder)

    
    

