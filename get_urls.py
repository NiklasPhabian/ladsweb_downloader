import requests
import datetime
import requests
import argparse
import json
from eta import ETA
from bbox import bbox

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
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads file list from Ladsweb')
    parser.add_argument('--product', metavar='product', nargs='?', type=str, 
                        help='ladsweb product (e.g. VNP02DNB, VNP03DNB, CLDMSK_L2_VIIRS_SNPP)')
    parser.add_argument('--region', metavar='region', nargs='?', type=str, help='region', choices=bbox.keys())
    parser.add_argument('--col', metavar='collection', nargs='?', type=str, help='ladsweb collection', default='5110')
    parser.add_argument('--start', metavar='start', nargs='?', type=str, help='start date', default='2012-01-01')
    parser.add_argument('--stop', metavar='stop', nargs='?', type=str, help='stop date', default='2019-06-01')
    args = parser.parse_args()    
    
    print(args)
    get_urls_long(product=args.product, collection=args.collection, start=args.start, stop=args.stop, bbox=bbox[args.region])
    #get_urls_long(product='VNP02DNB', collection='5110', start=start, stop=stop, bbox=bbox)
    #get_urls_long(product='VNP03DNB', collection='5110', start=start, stop=stop, bbox=bbox)
    #get_urls_long(product='CLDMSK_L2_VIIRS_SNPP', collection='5110', start=start, stop=stop, bbox=bbox)
