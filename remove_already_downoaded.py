import glob
import lib
import pandas
import argparse
import os



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Removes already downloaded files from file list')
    parser.add_argument('--file_list', metavar='file_list', nargs='?', type=str, help='CSV to read urls/fileIDs from')
    parser.add_argument('--folder', metavar='folder', nargs='?', type=str, help='Destination folder', default='.')
    parser.add_argument('--overwrite', metavar='folder', nargs='?', type=str, help='Destination folder')
    args = parser.parse_args()

    if args.file_list is None or args.folder is None:
        print('Wrong usage')
        print(parser.print_help())
        quit()
        
    
    folder = os.path.expanduser(args.folder + '/')
    
    remote = pandas.read_csv(args.file_list, names=['id','url','n'])
    remote['remote_stumps'] = remote['url'].map(lib.path2stump)
    
    extension = remote.url.iloc[0].split('.')[-1]
    beginning = remote.url.iloc[0].split('/')[-1].split('.')[0]
    pattern = f'{beginning}*{extension}'
    existing_paths = lib.get_granule_paths(granule_folder=folder, granule_pattern=pattern, filter_term=None)
    existing_stumps = lib.paths2stumps(existing_paths)    
    existing = pandas.DataFrame({'existing_stumps': existing_stumps})
    
    merged = pandas.merge(remote, existing, left_on='remote_stumps', right_on='existing_stumps', how='outer', indicator=True)
    missing = merged[merged['_merge']=='left_only']
    
    out_file = args.file_list.split('.csv')[0]+'_missing.csv'    
    missing[['id', 'url', 'n']].to_csv(out_file, header=False, index=False)
