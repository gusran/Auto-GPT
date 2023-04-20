import re

import chardet


def replace_functions_by_name(code_str, new_function_str):
    # Extract the function name from the new function definition
    function_name = re.match(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', new_function_str, re.MULTILINE).group(1)

    # Regular expression pattern to match function definitions with the same name
    function_pattern = re.compile(
        r'^\s*def\s+{0}\s*\(.*?\)\s*:\s*(?:(?:[^{1}]*{1})?[^{1}]*?)*'.format(
            re.escape(function_name),
            re.escape("def")
        ),
        re.MULTILINE | re.DOTALL
    )

    # Replace the matching functions with the new function definition
    patched_code_str = function_pattern.sub(new_function_str, code_str)

    return patched_code_str


def extract_functions_by_name(code_str, function_name):
    # Regular expression pattern to match function definitions and their content
    function_pattern = re.compile(
        r'^\s*def\s+{0}\s*\(.*?\)\s*:\s*(?:(?:[^{1}]*{1})?[^{1}]*?)*'.format(
            re.escape(function_name),
            re.escape("def")
        ),
        re.MULTILINE | re.DOTALL
    )

    # Extract matching functions
    functions = function_pattern.findall(code_str)

    return functions


def read_file_with_detected_encoding(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()

    # Detect the encoding of the file
    detected_encoding = chardet.detect(binary_data)['encoding']

    # Decode the binary data using the detected encoding
    text_content = binary_data.decode(detected_encoding)

    return text_content


def is_python_code(text):
    # Check for 'def' keyword
    def_pattern = re.compile(r'^\s*def\b', re.IGNORECASE | re.MULTILINE)

    # Check for a colon at the end of a line
    colon_pattern = re.compile(r':\s*$', re.MULTILINE)

    # If both 'def' and a colon at the end of a line are present, it's likely a Python file
    if def_pattern.search(text) and colon_pattern.search(text):
        return True
    else:
        return False


def has_function_name_collision(code_str1, code_str2):
    # Regular expression pattern to match function definitions
    function_pattern = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)

    # Extract function names from both code strings
    function_names1 = set(function_pattern.findall(code_str1))
    function_names2 = set(function_pattern.findall(code_str2))

    # Check if there are any common function names (collisions)
    common_names = function_names1.intersection(function_names2)

    if common_names:
        return True, common_names
    else:
        return False, set()
