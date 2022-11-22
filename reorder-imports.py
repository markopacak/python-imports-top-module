"""
Move import statements declared inside function to the top of the module

Imports within functions should only be used to prevent circular imports,
for optional dependencies, or if an import is slow.

"""
import argparse
import ast
from ast import NodeVisitor
import importlib
import sys
import os

# these library imports will not be moved to the top of the module
EXCLUDE_LIBS = {
    "urllib.request",
    "xlrd",
    "xlsxwriter",
}

EXCLUDE_FILES = {
    "__init__.py"
}


class Visitor(NodeVisitor):
    def __init__(self, cur_file) -> None:
        self.ret = 0
        self.file = cur_file
        self.line_numbers = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for _node in ast.walk(node):
            if (
                isinstance(_node, ast.ImportFrom)
                and _node.__module__ != "__main__"
                and _node.module not in EXCLUDE_LIBS
                and _node.module.split(".")[0] not in EXCLUDE_LIBS
            ):
                try:
                    importlib.import_module(_node.module)
                except Exception as exp:  # noqa: F841
                    pass
                else:
                    print(
                        f"{self.file}:{_node.lineno}:{_node.col_offset} {_node.end_lineno} standard "
                        f"library import '{_node.module}' should be at the top of "
                        "the file"
                    )
                    self.ret = 1
                    self.line_numbers.append(_node.lineno)

            elif isinstance(_node, ast.Import):
                for _name in _node.names:
                    if (
                        _name.name == "__main__"
                        or _name.name in EXCLUDE_LIBS
                        or _name.name.split(".")[0] in EXCLUDE_LIBS
                    ):
                        continue
                    try:
                        importlib.import_module(_name.name)
                    except Exception as exp:  # noqa: F841
                        pass
                    else:
                        print(
                            f"{self.file}:{_node.lineno}:{_node.col_offset} standard "
                            f"library import '{_name.name}' should be at the top of "
                            "the file"
                        )
                        self.ret = 1
                        self.line_numbers.append(_node.lineno)
        self.generic_visit(node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    args = parser.parse_args()
    ret = 0

    for subdir, dirs, files in os.walk(args.folder):
        for file_ in files:
            if not file_.endswith(".py"):
                continue
            if file_ in EXCLUDE_FILES:
                continue

            file_path = subdir + os.sep + file_

            with open(file_path, encoding="utf-8", mode="r") as fd:
                content = fd.read()

            tree = ast.parse(content)
            visitor = Visitor(file_path)
            visitor.visit(tree)

            content = content.split("\n")
            import_lines = []
            if visitor.line_numbers:
                # make sure to iterate starting from the last element because we are removing lines by index
                for line_number in reversed(visitor.line_numbers):
                    import_lines.append(content.pop(line_number-1))

                for line in import_lines:
                    content.insert(0, line.strip())

                with open(file_path, encoding="utf-8", mode="w") as fd:
                    fd.write('\n'.join(content))

            ret |= visitor.ret

    sys.exit(ret)
