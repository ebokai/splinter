# /splinter/splinter.py

import ast
import os
import sys
from pathlib import Path


class ShortVarLinter(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []
        self.allowed_var_names = []

        allowlist_path = Path(__file__).parent.parent / "allowlist.txt"
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                self.allowed_var_names.append(line.strip("\n"))

    def visit_Name(self, node):
        # check for short variable names
        if isinstance(node.ctx, ast.Store) and len(node.id) < 4:
            self.issues.append((node.lineno, node.id))
        self.generic_visit(node)


def lint_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError as e:
            print(f"{filepath}: SyntaxError: {e}")
            return 1

    linter = ShortVarLinter(filepath)
    linter.visit(tree)

    for lineno, var in linter.issues:
        if var not in linter.allowed_var_names:
            print(
                f"{filepath}:{lineno}: Variable name '{var}' is too short [short-variable]"
            )
    return len(linter.issues)


def scan_directory(path):
    total_issues = 0
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                total_issues += lint_file(os.path.join(root, file))
    return total_issues


def main():
    if len(sys.argv) != 2:
        print("usage: python -m splinter <directory>")
        sys.exit(1)

    issues = scan_directory(sys.argv[1])
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
