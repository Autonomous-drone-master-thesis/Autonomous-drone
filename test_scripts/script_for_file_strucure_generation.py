import os

def get_directory_structure(path, indent=0):
    dir_structure = ''
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            dir_structure += ' ' * indent + '--' + item + '\n'
        elif os.path.isdir(item_path):
            dir_structure += ' ' * indent + item + '/\n'
            dir_structure += get_directory_structure(item_path, indent + 2)
    return dir_structure

if __name__ == '__main__':
    start_path = os.getcwd()
    structure_string = get_directory_structure(start_path)
    print(structure_string)