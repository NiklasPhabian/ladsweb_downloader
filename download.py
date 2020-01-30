#!/usr/bin/python3

import argparse
import configparser
import os
from ladsweb_file import LadswebFile
from eta import ETA


def download(folder, file_list):
    files = open(file_list).readlines()
    eta = ETA(n_tot=len(files))
    for row in files[::-1]:
        ladsweb_file = LadswebFile(file_id=row.split(',')[0], url=row.split(',')[1])
        ladsweb_file.get_file_name()
        eta.display(step='Downloading {name}'.format(name=ladsweb_file.file_name))
        ladsweb_file.get_properties()
        ladsweb_file.verified_download(folder)
        del files[-1]
        open(file_list, 'w').writelines(files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Downloads files from file list')
    parser.add_argument('--file_list', metavar='file_list', nargs='?', type=str, help='CSV to read urls/fileIDs from')
    parser.add_argument('--folder', metavar='folder', nargs='?', type=str, help='Destination folder', default='.')
    args = parser.parse_args()

    if args.file_list is None or args.folder is None:
        print('Wrong usage')
        print(parser.print_help())
        quit()

    folder = os.path.expanduser(args.folder + '/')
    download(folder, args.file_list)

