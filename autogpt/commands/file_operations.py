"""File operations for AutoGPT"""
from __future__ import annotations

import os
import os.path
from pathlib import Path
from typing import Generator
from autogpt.workspace import path_in_workspace, WORKSPACE_PATH
from autogpt.commands import util

LOG_FILE = "file_logger.txt"
LOG_FILE_PATH = WORKSPACE_PATH / LOG_FILE


def check_duplicate_operation(operation: str, filename: str) -> bool:
    """Check if the operation has already been performed on the given file

    Args:
        operation (str): The operation to check for
        filename (str): The name of the file to check for

    Returns:
        bool: True if the operation has already been performed on the file
    """
    log_content = read_file(LOG_FILE)
    log_entry = f"{operation}: {filename}\n"
    return log_entry in log_content


def split_file(
        content: str, max_length: int = 4000, overlap: int = 0
) -> Generator[str, None, None]:
    """
    Split text into chunks of a specified maximum length with a specified overlap
    between chunks.

    :param content: The input text to be split into chunks
    :param max_length: The maximum length of each chunk,
        default is 4000 (about 1k token)
    :param overlap: The number of overlapping characters between chunks,
        default is no overlap
    :return: A generator yielding chunks of text
    """
    start = 0
    content_length = len(content)

    while start < content_length:
        end = start + max_length
        if end + overlap < content_length:
            chunk = content[start: end + overlap]
        else:
            chunk = content[start:content_length]
        yield chunk
        start += max_length - overlap


def read_file(filename: str) -> str:
    """Read a file and return the contents

    Args:
        filename (str): The name of the file to read

    Returns:
        str: The contents of the file
    """
    try:
        filepath = path_in_workspace(filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {str(e)}"


def ingest_file(
        filename: str, memory, max_length: int = 4000, overlap: int = 200
) -> None:
    """
    Ingest a file by reading its content, splitting it into chunks with a specified
    maximum length and overlap, and adding the chunks to the memory storage.

    :param filename: The name of the file to ingest
    :param memory: An object with an add() method to store the chunks in memory
    :param max_length: The maximum length of each chunk, default is 4000
    :param overlap: The number of overlapping characters between chunks, default is 200
    """
    try:
        print(f"Working with file {filename}")
        content = read_file(filename)
        content_length = len(content)
        print(f"File length: {content_length} characters")

        chunks = list(split_file(content, max_length=max_length, overlap=overlap))

        num_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            print(f"Ingesting chunk {i + 1} / {num_chunks} into memory")
            memory_to_add = (
                f"Filename: {filename}\n" f"Content part#{i + 1}/{num_chunks}: {chunk}"
            )

            memory.add(memory_to_add)

        print(f"Done ingesting {num_chunks} chunks from {filename}.")
    except Exception as e:
        print(f"Error while ingesting file '{filename}': {str(e)}")


def write_to_file(filename: str, text: str, create: bool) -> str:
    """Write text to a file

    Args:
        filename (str): The name of the file to write to
        text (str): The text to write to the file

    Returns:
        str: A message indicating success or failure
    """
    if os.path.exists(path_in_workspace(filename)) and os.path.isdir(filename):
        return "Error: Command had no effect. A directory already exists with the same name, " \
               "you need to choose a different name."
    if os.path.exists(path_in_workspace(filename)) and create:
        return f"Error: Command had no effect, {filename} has already been created. Replace {filename} if your " \
               f"intention is to overwrite the content or append if your intention is to add text to the file."
    try:
        filepath = path_in_workspace(filename)
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return "File created successfully!" if create else "File replaced successfully1"
    except Exception as e:
        return f"Error: {str(e)}"


def patch_python_file(filename: str, text: str):
    valid, message = util.validate_python_code(text)
    if not valid:
        return f"The patch code has syntax errors {message}"

    if util.is_python_code(text):
        file_content = util.read_file_with_detected_encoding(path_in_workspace(filename))
        if util.is_python_code(file_content):
            has_collision, common_function_names = util.has_function_name_collision(file_content, text)
            if has_collision:
                for function_name in common_function_names:
                    functions_in_file = util.extract_functions_by_name(file_content, function_name)
                    functions = util.extract_functions_by_name(text, function_name)

                    if len(functions_in_file) > 1:
                        return f"There are multiple definitions of {function_name} in the file" \
                               f", and I was not able to determine which one to patch"

                    if len(functions) > 1:
                        return "I failed to patch the file. The code I am trying to patch with contains several " \
                               f"definitions of {function_name}, when patching there cannot be multiple " \
                               "definitions of the same function in the code I am patching with!"
                util.replace_functions_by_name(file_content, text)
                return f"The functions {list(common_function_names).join(' ,')} was successfully patched!"
            else:
                return f"I failed to patch the file, non of the functions defined in the patch code exist in the file"
        else:
            return f"I failed to patch the file with the patch, the file does not seem to contain functions to patch"
    else:
        return f"I failed to patch the file with the patch, the patch code does not seem to contain any functions"


def append_to_file(filename: str, text: str) -> str:
    """Append text to a file

    Args:
        filename (str): The name of the file to append to
        text (str): The text to append to the file

    Returns:
        str: A message indicating success or failure
    """

    if util.is_python_code(text):
        file_content = util.read_file_with_detected_encoding(path_in_workspace(filename))
        if util.is_python_code(file_content):
            has_collision, common_function_names = util.has_function_name_collision(file_content, text)
            if has_collision:
                return f"The text you are trying to append " \
                       f"is python code with functions that already exist in the file, " \
                       f"the following functions are already in the file {', '.join(common_function_names)}! " \
                       f"You can try patching the functions one by one using the patch_python_file command " \
                       f"or replace the file with new content."

    try:
        filepath = path_in_workspace(filename)
        with open(filepath, "a") as f:
            f.write(text)

        return "Text appended successfully!"
    except Exception as e:
        return f"Error: {str(e)}"


def delete_file(filename: str) -> str:
    """Delete a file

    Args:
        filename (str): The name of the file to delete

    Returns:
        str: A message indicating success or failure
    """
    try:
        filepath = path_in_workspace(filename)
        os.remove(filepath)
        return "File deleted successfully!"
    except Exception as e:
        return f"Error: {str(e)}"


def search_files(directory: str) -> list[str]:
    """Search for files in a directory

    Args:
        directory (str): The directory to search in

    Returns:
        list[str]: A list of files found in the directory
    """
    found_files = []

    if directory in {"", "/"}:
        search_directory = WORKSPACE_PATH
    else:
        search_directory = path_in_workspace(directory)

    for root, _, files in os.walk(search_directory):
        for file in files:
            if file.startswith("."):
                continue
            relative_path = os.path.relpath(os.path.join(root, file), WORKSPACE_PATH)
            found_files.append(relative_path)

    return found_files
