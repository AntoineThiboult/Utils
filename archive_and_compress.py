# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 12:00:18 2023
@author: Antoine Thiboult

Script to archive and compress repositories.
Perform a source-destination comparison to perform operation only on new files.
Can filter specific folders by specifying the matching file. See pathlib.Path.glob doc for more details
Destination can be overwritten if overwrite is set to True
To ommit compression (perform a simple copy) add the name of the file in the copy_only list
"""

import tarfile
import shutil
from pathlib import Path

main_directory ='E:/Ro2_micromet_raw_data/Data'
tar_directory = 'E:/Ro2_micromet_raw_data/Tar_for_Beluga'
matching_files = '*'
overwrite = False
copy_only = ['date_verification.xlsx']


def make_tarfile(source_folder, output_filename):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_folder, arcname='')

# Manage path
main_directory = Path(main_directory)
tar_directory = Path(tar_directory)
list_field_collection = main_directory.glob(matching_files)

for i_field_collection in list_field_collection:

    # If current file/folder in copy_only, simply copy
    if i_field_collection.name == copy_only:
        shutil.copyfile(i_field_collection, Path.joinpath(tar_directory, i_field_collection.name) )
        continue

    # Create the corresponding folder in the parent destination directory
    if not Path.joinpath(tar_directory, i_field_collection.stem).is_dir():
        Path.mkdir( Path.joinpath(tar_directory, i_field_collection.stem))

    for station in i_field_collection.glob('*'):
        archive_name = Path.joinpath(tar_directory, i_field_collection.stem, station.stem).with_suffix('.tar.gz')

        if not archive_name.is_file():
            print(f'Start compressing "{station}"')
            make_tarfile(station, archive_name)
            print(f'"{station}" has been archived and compressed in "{archive_name}"')
            continue

        if overwrite == True:
            print(f'Start compressing "{station}"')
            make_tarfile(station, archive_name)
            print(f'"{station}" has been archived and compressed in "{archive_name}"')