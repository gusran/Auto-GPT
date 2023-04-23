import unittest
from autogpt.commands import util

import textwrap


def reformat_and_strip(code_str, indent_level=0):
    # Dedent the code string
    dedented_code = textwrap.dedent(code_str)

    # Reformat the code string
    reformatted_code = textwrap.indent(dedented_code, ' ' * indent_level)

    # Strip leading and trailing whitespace from each line
    stripped_lines = [line.strip() for line in reformatted_code.split('\n')]

    # Join the stripped lines back into a single string
    stripped_code = '\n'.join(stripped_lines)

    return stripped_code.strip()


class TestUtils(unittest.TestCase):
    def test_has_python_code(self):
        code_str = """import connect_four\n\ndef start_new_game():\n    game = connect_four.ConnectFour()\n    game.print_board()\n    while True:\n        move = None\n        valid_move = False\n        while not valid_move:\n            try:\n                move = int(input(f"{game.current_player}: Enter column number (0-6): "))\n                if not game.is_valid_move(move):\n                    raise Exception(f"Move {move} is invalid.")\n                valid_move = True\n            except ValueError:\n                print("Move must be a number")\n            except Exception as e:\n                print(str(e))\n\n        game.make_move(move)\n        game.print_board()\n        winner = game.check_winner()\n        if winner:\n            print(f"{winner} wins!")\n            break\n        elif game.is_full():\n            print("Draw!")\n            break\n        game.switch_player()"""

        self.assertTrue(util.is_python_code(code_str))

    def test_has_function_name_collision(self):
        code_str1 = """
        def foo():
            return "Hello from foo"
        
        def bar():
            return "Hello from bar"
        """

        code_str2 = """
        def baz():
            return "Hello from baz"
        
        def bar():
            return "Hello from another bar"
        """

        collision, common_names = util.has_function_name_collision(code_str1, code_str2)
        self.assertTrue(collision)
        self.assertEqual(common_names, {"bar"})

    def test_extract_functions_by_name(self):
        code_str = """
def foo():
    return "Hello from foo"

def bar():
    return "Hello from bar"

def foo(a, b):
    return a + b

def baz():
    return "Hello from baz"
"""

        function_name = "foo"
        functions = util.extract_functions_by_name(code_str, function_name)

        self.assertEqual(len(functions), 2)
        self.assertTrue("def foo():" in functions[0])
        self.assertTrue("def foo(a, b):" in functions[1])

    def test_replace_functions_by_name(self):
        code_str = """
def bar():
    return "Hello from bar"

def foo(a, b):
    return a + b

def baz():
    return "Hello from baz"
        """

        new_function_str = """
def foo(x, y):
    return x * y
        """

        patched_code_str = util.replace_functions_by_name(code_str, new_function_str)

        self.assertIn("def foo(x, y):", patched_code_str)
        self.assertNotIn("def foo():", patched_code_str)
        self.assertNotIn("def foo(a, b):", patched_code_str)

    def test_has_function_name_collision_method(self):
        code_str1 = """
class MyClass:
    def foo(self):
        return "Hello from foo"

def bar():
    return "Hello from bar"
        """

        code_str2 = """
class MyClass:
    def baz(self):
        return "Hello from baz"

def bar():
    return "Hello from another bar"
        """

        collision, common_names = util.has_function_name_collision(code_str1, code_str2)
        self.assertTrue(collision)
        self.assertEqual(common_names, {"bar"})

    def test_extract_functions_by_name_method(self):
        code_str = """
class MyClass:
    def foo(self):
        return "Hello from foo"

def bar():
    return "Hello from bar"

class AnotherClass:
    def foo(self, a, b):
        return a + b

def baz():
    return "Hello from baz"
        """

        function_name = "foo"
        functions = util.extract_functions_by_name(code_str, function_name)

        self.assertEqual(len(functions), 2)
        self.assertTrue("def foo(self):" in functions[0])
        self.assertTrue("def foo(self, a, b):" in functions[1])

    def test_replace_functions_by_name_method(self):
        code_str = """
class MyClass:
    def foo(self):
        return "Hello from foo"

def bar():
    return "Hello from bar"

class AnotherClass:
    def foo(self, a, b):
        return a + b

def baz():
    return "Hello from baz"
        """

        new_function_str = """
def foo(self, x, y):
    return x * y
        """

        patched_code_str = util.replace_functions_by_name(code_str, new_function_str)

        self.assertIn("def foo(self, x, y):", patched_code_str)
        self.assertNotIn("def foo(self):", patched_code_str)
        self.assertNotIn("def foo(self, a, b):", patched_code_str)

    def test_replace_functions_by_name_with_methods_check_complete_body(self):
        code_str = """
class MyClass:
    def bar(self):
        print("Hello from bar")
        return "Hello from bar"

    def foo(self, a, b):
        print("Hello from foo with parameters")
        return a + b
        """

        new_function_str = """
def foo(self, x, y):
    print('Hello from new foo')
    return x * y
        """

        patched_code_str = util.replace_functions_by_name(code_str, new_function_str)
        extracted_functions = util.extract_functions_by_name(patched_code_str, "foo")

        print(extracted_functions)

        print(patched_code_str)

        self.assertEqual(len(extracted_functions), 1)
        for extracted_function in extracted_functions:
            self.assertEqual(reformat_and_strip(new_function_str, 4), reformat_and_strip(extracted_function, 4))


if __name__ == '__main__':
    unittest.main()
