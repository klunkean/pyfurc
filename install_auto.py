import subprocess
import os
import urllib.request
from zipfile import ZipFile

def get_auto_archive(target_dir):
    zipname = "auto.zip"
    target_path = os.path.abspath(os.path.join(target_dir, zipname))
    if not os.path.exists(target_dir):
        # ask for directory creation
        pass
    url = "https://github.com/auto-07p/auto-07p/archive/refs/heads/master.zip"
    urllib.request.urlretrieve(url, target_path)
    return target_path

def unpack_auto_archive(archive_path):
    zip_path, _ = os.path.split(archive_path)
    
    with ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(zip_path)
        auto_dir_name = zip_ref.infolist()[0].filename
    path_to_auto_dir = os.path.join(zip_path,auto_dir_name)

    try:
        os.rename(path_to_auto_dir, os.path.join(zip_path, "auto_07p"))
        os.remove(archive_path)
    except OSError:
        # catch if directory auto_07p is already present, 
        # or better: check beforehand
        pass 

def install_auto(auto_dir):
    ...

if __name__ == "__main__":
    zip_file = get_auto_archive("/home/andre/Downloads")
    unpack_auto_archive(zip_file)