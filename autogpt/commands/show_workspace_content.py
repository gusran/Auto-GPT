import os
import chardet

from autogpt.workspace import path_in_workspace, WORKSPACE_PATH


def show_workspace_content() -> str:
    content_str = "Here follows the content of the workspace,\n------ separates each file:\n"
    content_str += recurse(path_in_workspace('.'), content_str)
    content_str += "------"
    return content_str


def append_file_content_to_str(directory, file, content_str):
    path = os.path.join(directory, file)

    with open(path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    rel_path = os.path.relpath(path, WORKSPACE_PATH)
    with open(path, 'r', encoding=encoding) as f:
        content_str += f"content of file {rel_path}:\n"
        content_str += f.read()
        content_str += '\n------\n'

    return content_str


def recurse(directory, content_str):
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            content_str = append_file_content_to_str(directory, file, content_str)
        else:
            content_str = recurse(os.path.join(directory, file), content_str)

    return content_str
