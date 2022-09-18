import glob
import os

def path2stump(path):
    name = path.split('/')[-1]     
    name_parts = name.split('.')
    date = name_parts[1]
    time = name_parts[2]    
    stump = date + '.' + time
    return stump

def paths2stumps(paths):
    stumps = []
    for path in paths:
        stump=path2stump(path)
        stumps.append(stump)
    return stumps


def get_granule_paths(granule_folder, granule_pattern, filter_term=None):
    granule_paths = sorted(glob.glob(os.path.expanduser(granule_folder) + '/' + granule_pattern + '*'))
    if filter_term:
        granule_paths = list(filter(lambda name: filter_term not in name, granule_paths))
    return granule_paths
        