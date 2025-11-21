# /splinter/splinter.py

import ast
import json
import os
import sys
from pathlib import Path

ISSUE_MESSAGES = {
    "short-variable-name": "Variable name '{var}' is too short",
    "long-variable-name": "Variable name '{var}' is too long",
    "short-function-name": "Function name '{var} is too short",
    "long-function-name": "Function name {var} is too long",
}


class ShortVarLinter(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []
        self.allowed_var_names = []

        config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        allowlist_path = Path(__file__).parent.parent / "allowlist.txt"
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                self.allowed_var_names.append(line.strip("\n"))

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Store):
            return self.generic_visit(node)

        if len(node.id) < self.config["short-variable-length"]:
            self.issues.append((node.lineno, node.id, "short-variable-name"))
        elif len(node.id) > self.config["long-variable-length"]:
            self.issues.append((node.lineno, node.id, "long-variable-name"))
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        name_len = len(node.name)
        if name_len < self.config["short-function-length"]:
            self.issues.append((node.lineno, node.name, "short-function-name"))
        elif name_len > self.config["long-function-length"]:
            self.issues.append((node.lineno, node.name, "long-function-name"))
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

    for lineno, var, issue in linter.issues:
        if var not in linter.allowed_var_names:
            message = ISSUE_MESSAGES.get(issue, "Unknown issue").format(var=var)
            print(f"{filepath}:{lineno}: {message} [{issue}]")

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
