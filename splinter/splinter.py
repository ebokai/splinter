import ast
import os
import sys


class ShortVariableNameLinter(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) and len(node.id) < 4:
            self.issues.append((node.lineno, node.id))
        self.generic_visit(node)


def lint_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError as e:
            print(f"SyntaxError in {filepath}: {e}")
            return

    linter = ShortVariableNameLinter(filepath)
    linter.visit(tree)

    for lineno, var in linter.issues:
        print(f"{filepath}:{lineno}: Variable name '{var}' is too short")


def scan_directory(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                lint_file(os.path.join(root, file))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python my_linter.py <directory>")
        sys.exit(1)

    scan_directory(sys.argv[1])
