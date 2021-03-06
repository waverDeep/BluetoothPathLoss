import glob
import natsort
import os


def get_all_file_path(input_dir, file_extension, sort=True):
    temp = glob.glob(os.path.join(input_dir, '**', '*.{}'.format(file_extension)), recursive=True)
    if sort:
        temp = natsort.natsorted(temp)
    return temp


def get_filename(input_filepath):
    return input_filepath.split('/')[-1]


def get_pure_filename(input_filepath):
    temp = input_filepath.split('/')[-1]
    return temp.split('.')[0]


def create_directory(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    except OSError:
        print('Error : Creating directory: '+dir_path)


def get_directory_list(dir_path, sort=True):
    if sort:
        return natsort.natsorted(os.listdir(dir_path))
    else:
        return os.listdir(dir_path)


def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return lines


def extract_only_directory(dir_list):
    new_dir_list = []
    for name in dir_list:
        if '.csv' in name:
            pass
        else:
            new_dir_list.append(name)
    return new_dir_list