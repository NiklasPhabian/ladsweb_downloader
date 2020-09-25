import requests

out_folder = ''
host = 'https://ladsweb.modaps.eosdis.nasa.gov/'


def save_file(ret, file_name, folder):
    with open(folder + file_name, 'wb') as f:
        for chunk in ret.iter_content(chunk_size=1024): 
            if chunk: 
                f.write(chunk)


def get_hdf(version, product, year, day, time, creation):
    filename_stump = '{product}.A{year}{day}.{time}.00{version}.{creation}.hdf'
    file_name = filename_stump.format(version=version, product=product, year=year, day=day, time=time, creation=creation)    
    folder_stump = 'archive/allData/{version}/{product}/{year}/{day}/'
    folder = folder_stump.format(version=version, product=product, year=year, day=day)    
    url = host + folder + file_name    
    ret = requests.get(url)
    save_file(ret, file_name, out_folder)
    
    
def get_json(version, product, year, day):
    json_url_stump = host + '{version}/{product}/{year}/{day}/.json'
    json_url = json_url_stump.format(version=version, product=product, year=year, day=day)
    ret = requests.get(json_url)
    json = ret.json()
    return json


def find_creation(json, time):    
    for entry in json['data']:
        filename = entry[0]
        file_time = filename.split('.')[2]        
        if file_time == time:
            creation = filename.split('.')[4]
            return creation
        

def get_file(version, year, day, time, product):
    json = get_json(version, product, year, day)
    creation = find_creation(json, time)
    get_hdf(version, product, year, day, time, creation)

if __name__ == '__main__':      
    get_file(version=6, year=2017, day=058, time=0010, product='MOD09')
    
    
    
  
