#!/usr/bin/python3

import requests
import configparser
import datetime
import requests
import argparse
import time
from eta import ETA


def get_urls_long(product, collection, start, stop, bbox, day, night):
    # The api times out for ranges of more than a couple of months worth of tiles
    # Therefore we make iterative calls to the api
    urls = []
    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    stop = datetime.datetime.strptime(stop, '%Y-%m-%d').date()
    iterator = start    
    step = datetime.timedelta(days=50)
    while iterator + step < stop:
        urls += get_urls(product=product, collection=collection, 
                         start=iterator, stop=iterator+step, bbox=bbox, day=day, night=night)
        iterator += step
    urls += get_urls(product=product, collection=collection, start=iterator, stop=stop, bbox=bbox)    
    return urls


def get_urls(product, collection, start, stop, bbox, day=True, night=False):
    host = 'https://ladsweb.modaps.eosdis.nasa.gov'
    api = '/api/v1/files/'
    query = 'product={product}&collection={collection}&'\
            'dateRanges={start}..{stop}&'\
            'areaOfInterest=x{west}y{north},x{east}y{south}&'\
            'dayCoverage={day}&nightCoverage={night}'
    query = query.format(product=product, collection=collection,
                         start=start, stop=stop,
                         north=bbox['north'], south=bbox['south'], west=bbox['west'], east=bbox['east'],
                         day=str(day).lower(), night=str(night).lower())
    print(host+api+query)

    success = False
    n_tries = 0
    while not success:
        ret = requests.get(host+api+query, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=1200)   
        if ret.status_code!=200 or len(ret.json()) == 0:
            print('empty response; flasely specified arguments? timeout?')
            print('Status Code: {}'.format(ret.status_code))
            print('retrying')
            time.sleep(1)
            n_tries += 1
            if n_try == 3:
                print('tried 3 times; giving up')
                return []            
        else: 
            success = True

    urls = []    
    json_ret = ret.json()
    for file_id in json_ret.keys():
        url = host + json_ret[file_id]['fileURL']
        urls.append((file_id, url))
    return urls
    
    
if __name__ == '__main__':
    bbox = configparser.ConfigParser()
    bbox.read('bbox.config')
    parser = argparse.ArgumentParser(description='Downloads file list from Ladsweb')
    parser.add_argument('--product', metavar='product', nargs='?', type=str, 
                        help='ladsweb product (e.g. VNP02DNB, VNP03DNB, CLDMSK_L2_VIIRS_SNPP, VNP46A1, MOD09)')
    parser.add_argument('--collection', metavar='collection', nargs='?', type=str, 
                        help='ladsweb collection (e.g. 5110, 5000, 6)')
    parser.add_argument('--region', metavar='region', nargs='?', type=str, 
                        help='region as specified in bbox.config', choices=bbox.sections())    
    parser.add_argument('--start', metavar='start', nargs='?', type=str, 
                        help='start date (yyyy-mm-dd)', default='2019-04-01')
    parser.add_argument('--stop', metavar='stop', nargs='?', type=str, 
                        help='stop date (yyyy-mm-dd)', default='2019-09-01')
    parser.add_argument('--day', dest='day', action='store_true')
    parser.add_argument('--night', dest='night', action='store_true')
    parser.set_defaults(day=False)
    parser.set_defaults(night=False)

    args = parser.parse_args()   
    if args.product is None or args.region is None or args.collection is None:
        print('Wrong usage')
        print(parser.print_help())
        quit()
    
    urls = get_urls_long(product=args.product, 
                         collection=args.collection, 
                         start=args.start, stop=args.stop, 
                         bbox=bbox[args.region],
                         day=args.day, night=args.night)

    file_list_name = 'file_lists/{region}_{product}.csv'.format(region=args.region, product=args.product)
    with open(file_list_name, 'a') as files_log:        
        for row in urls:
            files_log.write(row[0] + ',' + row[1] + ',\n')         
