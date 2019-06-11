# this script is written in python 3. might not work with a python 2 open cv environment


from zipfile import ZipFile
import os
from shutil import copyfile
import zipfile




dir_path = "/mnt/hgfs/code/ISI/gen_data/f/"
fonts_path = dir_path+'fonts/'

names_file = 'names.txt'

def main():
    files_list_in_directory = os.listdir(dir_path) # C:\Users\achin\Desktop\es_fonts
    names_txt = open(dir_path+names_file, 'w')    
    for each_file in files_list_in_directory:
        if zipfile.is_zipfile(dir_path+each_file):
            zf = ZipFile(dir_path+each_file)
            for f in zf.infolist():
                if(f.filename.split(".")[1] == 'ttf'):
                    zf.extract(f.filename, path=fonts_path)
                    names_txt.write(f.filename+'\n')


    names_txt.close()


def refresh_names():
    files_list_in_directory = os.listdir(fonts_path)
    names_txt = open(dir_path+names_file, 'w') 
    for each_file in files_list_in_directory:
        names_txt.write('sp_fonts/'+each_file+'\n')


if __name__=="__main__":
    # main()
    refresh_names()


