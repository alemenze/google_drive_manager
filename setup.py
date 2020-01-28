import os

create_dir=['./Data_storage',
            './Data_storage/FASTQs',
            './Data_storage/Raw_bcl',
            './download',
            './download/FASTQs',
            './download/Raw_bcl',
            './bcl_folders',
            './bcl_folders/up',
            './bcl_folders/down']

for folder in create_dir:
    try:
        os.mkdir(folder)
    except Exception as e:
        print(e)
