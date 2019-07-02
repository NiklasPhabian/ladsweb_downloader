import requests
import datetime
import requests
import argparse
from eta import ETA
from bbox import bbox

def get_urls_long(product, collection, start, stop, bbox):
    # The api times out for ranges of more than a couple of months worth of tiles
    # Therefore we make iterative calls to the api
    urls = []
    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    stop = datetime.datetime.strptime(stop, '%Y-%m-%d').date()
    iterator = start    
    step = datetime.timedelta(days=100)
    while iterator + step < stop:
        urls += get_urls(product=product, collection=collection, start=iterator, stop=iterator+step, bbox=bbox)
        iterator = iterator + step
    urls += get_urls(product=product, collection=collection, start=iterator, stop=iterator+step, bbox=bbox)    
    return urls


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
    urls = []    
    json_ret = ret.json()
    for file_id in json_ret.keys():
        url = host + json_ret[file_id]['fileURL']
        urls.append((file_id, url))
    return urls
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads file list from Ladsweb')
    parser.add_argument('--product', metavar='product', nargs='?', type=str, 
                        help='ladsweb product (e.g. VNP02DNB, VNP03DNB, CLDMSK_L2_VIIRS_SNPP)')
    parser.add_argument('--region', metavar='region', nargs='?', type=str, 
                        help='region', choices=bbox.keys())
    parser.add_argument('--collection', metavar='collection', nargs='?', type=str, 
                        help='ladsweb collection', default='5110')
    parser.add_argument('--start', metavar='start', nargs='?', type=str, 
                        help='start date', default='2012-01-01')
    parser.add_argument('--stop', metavar='stop', nargs='?', type=str, 
                        help='stop date', default='2019-06-01')
    args = parser.parse_args()    
    
    
    urls = get_urls_long(product=args.product, 
                         collection=args.collection, 
                         start=args.start, stop=args.stop, 
                         bbox=bbox[args.region])

    file_list_name = '{region}_{product}.csv'.format(region=args.region, product=args.product)
    with open(file_list_name, 'a') as files_log:        
        for row in urls:
            files_log.write(row[0] + ',' + row[1] + ',\n')         
