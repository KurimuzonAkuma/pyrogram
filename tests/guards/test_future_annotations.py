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

"""Every module of the package that writes an annotation defers it.

Without `from __future__ import annotations` a name used in an annotation has to exist at
import time, and the tree is one import cycle wide: the way round it was to quote the
annotation, which hides it from `ruff`'s `UP037` and from anything else that reads one. With
the import, the quotes are unnecessary everywhere and their absence is checkable.

The sweep reads the package. `tests/` and `compiler/` carry the import too, and nothing here
asserts that they keep it.
"""

from __future__ import annotations as _annotations

import ast

from tests.guards.name_resolution import REPOSITORY_ROOT, hand_written_files


def writes_an_annotation(tree: ast.Module) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            return True

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            arguments = node.args
            parameters = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]

            if node.returns or any(parameter.annotation for parameter in parameters):
                return True

    return False


def defers_its_annotations(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )


def modules_that_do_not_defer() -> list[str]:
    found: list[str] = []

    for path in hand_written_files():
        tree = ast.parse(path.read_text(), filename=path.name)

        if writes_an_annotation(tree) and not defers_its_annotations(tree):
            found.append(path.relative_to(REPOSITORY_ROOT).as_posix())

    return found


def test_every_annotated_module_defers_its_annotations() -> None:
    assert modules_that_do_not_defer() == []


def test_the_sweep_reads_the_modules_it_claims_to() -> None:
    annotated = [
        path.relative_to(REPOSITORY_ROOT).as_posix()
        for path in hand_written_files()
        if writes_an_annotation(ast.parse(path.read_text(), filename=path.name))
    ]

    assert len(annotated) > 700
    assert "pyrogram/client.py" in annotated


def test_the_sweep_reads_both_halves_of_what_it_asks() -> None:
    bare = ast.parse("x: int = 1\n")
    deferred = ast.parse("from __future__ import annotations as _annotations\n\nx: int = 1\n")
    unannotated = ast.parse("x = 1\n")

    assert writes_an_annotation(bare)
    assert not defers_its_annotations(bare)

    assert writes_an_annotation(deferred)
    assert defers_its_annotations(deferred)

    assert not writes_an_annotation(unannotated)
