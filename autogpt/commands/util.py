import re

import chardet
import ast
import os


def replace_function(function_name, function_nodes, new_function_node):
    for index, node in enumerate(function_nodes):
        if node.name == function_name:
            function_nodes[index] = new_function_node
            break
    return function_nodes


def replace_functions_by_name(code_str, new_function_str):
    tree = ast.parse(code_str)
    new_function_nodes = ast.parse(new_function_str).body
    new_function_names = [node.name for node in new_function_nodes if
                          isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

    for new_function_name, new_function_node in zip(new_function_names, new_function_nodes):
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for i, body_node in enumerate(node.body):
                    if isinstance(body_node,
                                  (ast.FunctionDef, ast.AsyncFunctionDef)) and body_node.name == new_function_name:
                        node.body[i] = new_function_node
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == new_function_name:
                tree.body = replace_function(new_function_name, tree.body, new_function_node)

    return ast.unparse(tree)


def extract_functions_by_name(code_str, function_name):
    tree = ast.parse(code_str)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == function_name:
                source_lines = code_str.splitlines()
                function_def = source_lines[node.lineno - 1:node.end_lineno]
                functions.append('\n'.join(function_def))

    return functions


def read_file_with_detected_encoding(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()

    # Detect the encoding of the file
    detected_encoding = chardet.detect(binary_data)['encoding']

    # Decode the binary data using the detected encoding
    text_content = binary_data.decode(detected_encoding if detected_encoding is not None else 'utf-8')

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


def get_workspace_state(dir_path):
    result = []
    for root, dirs, files in os.walk(dir_path):
        level = root.replace(str(dir_path), '').count(os.sep)
        indent = ' ' * 4 * level
        result.append(f"{indent}Folder: {os.path.basename(root)}")

        for f in files:
            if f.endswith('.txt'):
                result.append(f"{indent}- File: {f}")
            elif f.endswith('.py'):
                result.append(f"{indent}- File: {f}")
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    try:
                        module = ast.parse(file.read())
                    except SyntaxError:
                        continue

                    classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
                    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]

                    for class_node in classes:
                        class_name = class_node.name
                        result.append(f"{indent}    Class: {class_name}")
                        for method_node in class_node.body:
                            if isinstance(method_node, ast.FunctionDef):
                                method_name = method_node.name
                                result.append(f"{indent}        Method: {class_name}.{method_name}(...)")

                    for function_node in functions:
                        function_name = function_node.name
                        result.append(f"{indent}    Function: {function_name}(...)")

    return '\n'.join(result)


def validate_python_code(code_str):
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        error_line = e.lineno
        error_offset = e.offset
        error_msg = e.msg
        error_line_text = code_str.splitlines()[error_line - 1]
        error_indicator = " " * error_offset + "^"
        return False, f"Syntax error in line {error_line}:\n{error_line_text}\n{error_indicator}\n{error_msg}"



