import xml.etree.ElementTree as ET

def get_file_ids_long(product, collection, start, stop, north, south, west, east, dnb='N'):
    # The api times out for ranges of more than a couple of months worth of tiles
    # Therefore we make iterative calls to the api
    start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    stop = datetime.datetime.strptime(stop, '%Y-%m-%d').date()
    iterator = start
    file_ids = []
    step = datetime.timedelta(days=100)
    while iterator + step < stop:
        file_ids += get_file_ids(product=product, collection=collection,
                                start=iterator, stop=iterator+step,
                                north=bbox.north, south=bbox.south, west=bbox.west, east=bbox.east)
        iterator = iterator + step
    file_ids += get_file_ids(product=product, collection=collection,
                                start=iterator, stop=stop,
                                north=bbox.north, south=bbox.south, west=bbox.west, east=bbox.east)
    return file_ids


def get_file_ids(product, collection, start, stop, north, south, west, east, dnb='N'):
    api = 'https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles?'
    query = 'product={product}&collection={collection}&'\
            'start={start}&stop={stop}'\
            '&north={north}&south={south}&west={west}&east={east}&coordsOrTiles=coords&'\
            'dayNightBoth={dnb}'
    query = query.format(product=product, collection=collection,
                         start=start, stop=stop,
                         north=north, south=south, west=west, east=east,
                         dnb=dnb)
    print(api+query)
    failed = True
    while failed:
        try:
            ret = requests.get(api+query, timeout=30)
            root = ET.fromstring(ret.text)
            failed = False
        except:
            print('dl failed. trying again')
            time.sleep(1)
    file_ids = []
    for child in root:
        file_ids.append(child.text)
    return file_ids


def files_modwebsrv(product, collection, start, stop, north, south, west, east, dnb='N'):
    file_ids = get_file_ids_long(product=product, collection=collection, start=start, stop=stop,
                                 north=north, south=south, west=west, east=east, dnb=dnb)
    files = []
    eta = ETA(len(file_ids))    
    for file_id in file_ids:        
        eta.display(step='Getting URL for {}'.format(file_id))
        files.append(LadswebFile(file_id=file_id))                
    return files 
