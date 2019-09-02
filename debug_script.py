
import os


CUR_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PYTHON_PATH = os.path.join(CUR_DIR_PATH, 'venv', 'Scripts', 'python.exe')
INPUT_FILE_NAME = 'test.py'
INPUT_FILE_PATH = os.path.join(CUR_DIR_PATH, INPUT_FILE_NAME)


def tab_to_four_spaces(file_path):
    with open(file_path) as f:
        file_content = f.read()
    file_content = file_content.replace('\t', '    ')
    with open(file_path + '.tmp', 'w') as f:
	    f.write(file_content)


def main():
    tab_to_four_spaces(INPUT_FILE_PATH)
    os.system(PYTHON_PATH + ' ' + INPUT_FILE_NAME + '.tmp')


main()
