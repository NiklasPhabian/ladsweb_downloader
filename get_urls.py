#!/usr/bin/python3

import requests
import configparser
import datetime
import requests
import argparse
import time
from eta import ETA


def get_urls_long(product, collection, start, stop, bbox, day, night):
    # The api times out for ranges of more than a couple of months worth of files
    # Therefore we make iterative calls to the api
    urls = []
    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    stop = datetime.datetime.strptime(stop, '%Y-%m-%d').date()
    iterator = start
    step = datetime.timedelta(days=30)
    while iterator + step < stop:
        urls += get_urls(product=product, collection=collection,
                         start=iterator, stop=iterator+step, bbox=bbox, day=day, night=night)
        iterator += step
    urls += get_urls(product=product, collection=collection, start=iterator, stop=stop, bbox=bbox, day=day, night=night)
    return urls


def get_urls(product, collection, start, stop, bbox, day=False, night=False):
    host = 'https://ladsweb.modaps.eosdis.nasa.gov'
    api = '/api/v1/files/'
    query = 'product={product}&collection={collection}&'\
            'dateRanges={start}..{stop}&'\
            'areaOfInterest=x{west}y{north},x{east}y{south}&'\
            'dayCoverage={day}&nightCoverage={night}&dnboundCoverage={day}'
    query = query.format(product=product, collection=collection,
                         start=start, stop=stop,
                         north=bbox['north'], south=bbox['south'], west=bbox['west'], east=bbox['east'],
                         day=str(day).lower(), night=str(night).lower())

    print(host+api+query)
    success = False
    n_tries = 0
    while not success:
        ret = requests.get(host+api+query, headers={'X-Requested-With': 'XMLHttpRequest'}, timeout=120)
        if ret.status_code!=200 or len(ret.json()) == 0:
            print('empty response; flasely specified arguments? timeout?')
            print('Status Code: {}'.format(ret.status_code))
            print('retrying')
            time.sleep(10)
            n_tries += 1
            if n_tries == 10:
                print('tried 10 times')
                #return []
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
    parser.add_argument('--product', metavar='product',  type=str,
                        help='ladsweb product (e.g. VNP02DNB, VNP03DNB, CLDMSK_L2_VIIRS_SNPP, VNP46A1, MOD09)')
    parser.add_argument('--collection', metavar='collection', type=str,
                        help='ladsweb collection (e.g. 5110, 5000, 6)')
    parser.add_argument('--region', metavar='region',  type=str,
                        help='region as specified in bbox.config', choices=bbox.sections())
    parser.add_argument('--start', metavar='start',  type=str,
                        help='start date (yyyy-mm-dd)')
    parser.add_argument('--stop', metavar='stop', type=str,
                        help='stop date (yyyy-mm-dd)')
    parser.add_argument('--start_day', type=str,
                        help='specify the start day of the year as mm-dd')
    parser.add_argument('--stop_day', type=str,
                        help='specify the end day of the year as mm-dd')
    parser.add_argument('--start_year', type=int,
                        help='specify start year as yyyy')
    parser.add_argument('--stop_year', type=int,
                        help='specify stop year as yyyy')
    parser.add_argument('--day', dest='day', action='store_true', default=False)
    parser.add_argument('--night', dest='night', action='store_true', default=False)

    args = parser.parse_args()

    if args.product is None or args.region is None or args.collection is None:
        print('Wrong usage')
        print(parser.print_help())
        quit()

    if args.start is not None and args.stop is not None:
        urls = get_urls_long(product=args.product,
                             collection=args.collection,
                             start=args.start, stop=args.stop,
                             bbox=bbox[args.region],
                             day=args.day, night=args.night)
    elif args.start_day is not None and args.stop_day and args.stop_year is not None and args.start_year is not None:
        year = args.start_year
        urls = []
        while year<args.stop_year:
            start = '{year}-{day}'.format(year=year, day=args.start_day)
            stop= '{year}-{day}'.format(year=year, day=args.stop_day)
            year +=1
            urls += get_urls_long(product=args.product,
                                  collection=args.collection,
                                  start=start, stop=stop,
                                  bbox=bbox[args.region],
                                  day=args.day, night=args.night)
    else:
        print('need to specify either start and stop or start_day, stop_day, start_year, stop_year')
        print(parser.print_help())
        quit()

    file_list_name = f'file_lists/{args.region}_{args.product}_{args.start}-{args.stop}.csv'
    with open(file_list_name, 'a') as files_log:
        for row in urls:
            files_log.write(row[0] + ',' + row[1] + ',\n')
