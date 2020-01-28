import os
import sys
import subprocess

sys.path.append('./bin/')

import md5_check
import bcl_download, bcl_upload

sys.stdout=open('log.txt','w')

#### tar the bcl folders
bcl_dir='./bcl_folders/up'#just dont add the last /
final_tarlist=[]
for dirpath, dirnames, filenames in os.walk(bcl_dir, topdown=True):
    if dirpath.count(os.sep) - bcl_dir.count(os.sep) !=0:
        del dirnames[:]
        del filenames[:]
    for d in dirnames:
        in_path=os.path.join(dirpath, d)
        out_tar=d+'.tar.gz'
        final_tarlist.append(out_tar)

        out_path=os.path.join('./Data_storage/Raw_bcl/',out_tar)

        try:
            subprocess.run('tar -czvf '+out_path+' -C '+in_path, shell=True)
        except Exception as e:
            print(e)

print('Compression completed (if applicable)')

#### upload and download
dir_start='./Data_storage'


try:
    bcl_upload.uploader([dir_start])
except Exception as e:
    print(e)


print('Upload step completed')

downloads=[]
dir_start=dir_start.rstrip('/')
for dirpath, dirnames, filenames in os.walk(dir_start, topdown=True):
    if dirpath.count(os.sep) - dir_start.count(os.sep) != 0:
        del dirnames[:]
        del filenames[:]
    for d in dirnames:
        downloads.append([d, os.path.join(dirpath,d)])
for download in downloads:
    download_dir=download[1].replace('/Data_storage/','/download/')
    try:
        bcl_download.downloader([[download[0],download_dir]])
    except Exception as e:
        print(e)

### Regular folder md5 check (no untar needed)
files_start=[]
for dirpath, dirnames, filenames in os.walk(dir_start):
    for f in filenames:
        files_start.append(os.path.join(dirpath, f))
dir_end='./download'
files_end=[]
for dirpath, dirnames, filenames in os.walk(dir_end):
    for d in dirnames:
        for f in filenames:
            files_end.append(os.path.join(dirpath,f))
for f_in in files_start:
    match_count=[]
    for f_out in files_end:
        if os.path.basename(f_in) == os.path.basename(f_out):
            f_in_md5=md5_check.md5_file(f_in)
            f_out_md5=md5_check.md5_file(f_out)
            if f_in_md5==f_out_md5:
                match_count.append('md5 match for '+os.path.basename(f_in)+' and '+os.path.basename(f_out))
    if len(match_count) >0:
        print('download md5 ok for '+os.path.basename(f_out))
    else:
        print('ERROR! download md5 bad')
#### untar and md5 check for BCL downloads
bcl_out='./download/Raw_bcl'
tar_out='./bcl_folders/down'
sub_tar_out=[]
for dirpath, dirnames, filenames in os.walk(bcl_out, topdown=True):
    for f in filenames:
        
        in_path=os.path.join(dirpath, f)
        try:
            subprocess.run('tar -xzvf '+in_path+' -C '+tar_out,shell=True)
            
        except Exception as e:
            print(e)

print('Decompression completed')

for dirpath, dirnames, filenames in os.walk(tar_out, topdown=True):
    if dirpath.count(os.sep) - tar_out.count(os.sep) != 0:
        del dirnames[:]
        del filenames[:]
    for d in dirnames:
        sub_tar_out.append([os.path.join(dirpath,d)])


for out_dir in sub_tar_out:
    files=[]
    for dirpath, dirnames, filenames in os.walk(out_dir[0]):
        for f in filenames:
            files.append(os.path.join(dirpath, f))
    for dirpath, dirnames, filenames in os.walk(os.path.join(bcl_dir,out_dir[0].split('/')[-1])):
        for f in filenames:
            matching_count=[]
            
            for f1 in files:
                if os.path.basename(f1)==f:
                    f1_md5=md5_check.md5_file(f1)
                    f_md5=md5_check.md5_file(os.path.join(dirpath,f))
                    
                    if f1_md5==f_md5:
                        matching_count.append('md5 match for '+f+' and '+os.path.basename(f1))
            if len(matching_count) > 0:
                print('untar md5 ok for '+f)
            else:
                print('ERROR! Untar md5 bad for '+f)
                        
print('MD5 checksum validation completed')

with open('./log.txt') as out_log:
    for line in out_log:
        if 'ERROR' in line or 'error' in line:
            raise NameError('Error in output file')
