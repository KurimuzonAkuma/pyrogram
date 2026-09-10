#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

"""Where a module declares `__all__`, the declaration covers everything the module defines.

`ruff` already holds one half of this: `F401` fails on a name imported and neither used nor
listed, and `F822` fails on a listed name that resolves to nothing. Neither looks at a class
or a function the module defines itself, so a barrel that grows a class beside its imports
drops it from the public API the moment `__all__` appears, and nothing says so.

That is not hypothetical: the commit that first gave `pyrogram/__init__.py` an `__all__` left
`StopTransmission`, `StopPropagation` and `ContinuePropagation` out of it, and all three are
documented, caught by name in `pyrogram/dispatcher.py`, and imported by the methods.
"""

from __future__ import annotations as _annotations

import ast
from itertools import chain
from typing import Final

from tests.guards.name_resolution import REPOSITORY_ROOT, hand_written_files, tooling_files

# `pyrogram/errors/__init__.py` is the one module that cannot declare one: it re-exports a
#  package `make api` generates, which is absent from a fresh checkout and unenumerable.
MODULES_EXPECTED_TO_DECLARE: Final[tuple[str, ...]] = (
    "pyrogram/__init__.py",
    "pyrogram/types/__init__.py",
    "pyrogram/raw/core/primitives/__init__.py",
)


def declared_exports(tree: ast.Module) -> list[str] | None:
    """The strings of the module's `__all__`, or `None` where it declares none."""
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue

        if not any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            continue

        if not isinstance(node.value, ast.List):
            return []

        return [
            element.value
            for element in node.value.elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        ]

    return None


def defined_names(tree: ast.Module) -> list[str]:
    """Every public name the module binds itself, imports excluded: `ruff` owns those."""
    names: list[str] = []

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)

        elif isinstance(node, ast.Assign):
            names.extend(target.id for target in node.targets if isinstance(target, ast.Name))

        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)

    return [name for name in names if not name.startswith("_")]


def modules_declaring_exports() -> list[tuple[str, list[str], list[str]]]:
    found: list[tuple[str, list[str], list[str]]] = []

    for path in chain(hand_written_files(), tooling_files()):
        tree = ast.parse(path.read_text(), filename=path.name)
        exports = declared_exports(tree)

        if exports is not None:
            relative = path.relative_to(REPOSITORY_ROOT).as_posix()
            found.append((relative, exports, defined_names(tree)))

    return found


def test_every_declaration_covers_what_the_module_defines() -> None:
    undeclared = {
        module: [name for name in defined if name not in exports]
        for module, exports, defined in modules_declaring_exports()
        if any(name not in exports for name in defined)
    }

    assert undeclared == {}


def test_no_declaration_repeats_a_name() -> None:
    repeated = {
        module: sorted({name for name in exports if exports.count(name) > 1})
        for module, exports, _ in modules_declaring_exports()
        if len(set(exports)) != len(exports)
    }

    assert repeated == {}


def test_every_declaration_is_a_plain_list_of_strings() -> None:
    # An `__all__` built by concatenation or comprehension reads as a declaration and is not
    #  one: nothing above can check it, and the two tests would pass by seeing nothing.
    assert [module for module, exports, _ in modules_declaring_exports() if not exports] == []


def test_the_sweep_reads_the_modules_it_claims_to() -> None:
    modules = [module for module, _, _ in modules_declaring_exports()]

    assert len(modules) > 12

    for expected in MODULES_EXPECTED_TO_DECLARE:
        assert expected in modules


def test_the_sweep_reads_both_halves_of_what_it_asks() -> None:
    listed = ast.parse('class Thing:\n    pass\n\n\n__all__ = ["Thing"]\n')
    unlisted = ast.parse("class Thing:\n    pass\n\n\n__all__ = []\n")
    silent = ast.parse("class Thing:\n    pass\n")

    assert declared_exports(listed) == ["Thing"]
    assert defined_names(listed) == ["Thing"]

    assert declared_exports(unlisted) == []
    assert declared_exports(silent) is None

    # An import is `ruff`'s to judge, and a private name is nobody's.
    assert defined_names(ast.parse("from .thing import Thing\n")) == []
    assert defined_names(ast.parse("_private = 1\n__version__ = '1'\n")) == []
