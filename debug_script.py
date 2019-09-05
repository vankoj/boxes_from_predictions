
import os
import sys


assert len(sys.argv) >= 2, 'Wrong number of arguments! Required argument: input_file_path'

CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PYTHON_PATH = os.path.join(CUR_DIR_PATH, 'venv_Copy', 'Scripts', 'python.exe')
INPUT_FILE_PATH = sys.argv[1]
INPUT_FILE_NAME = INPUT_FILE_PATH.split('\\')[-1]
TAB_SPACES_NUM = 4
if len(sys.argv) >= 3:
	TAB_SPACES_NUM = int(sys.argv[2])


def tab_to_four_spaces(file_path):
    with open(file_path) as f:
        file_content = f.read()
    file_content = file_content.replace('\t', ' ' * TAB_SPACES_NUM)
    with open(file_path + '.tmp', 'w') as f:
	    f.write(file_content)


def main():
    tab_to_four_spaces(INPUT_FILE_PATH)
    os.system(PYTHON_PATH + ' ' + INPUT_FILE_NAME + '.tmp')


main()
