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

import ast
import pathlib
from typing import Dict, Final, Iterator, List, Tuple

from tests.guards.name_resolution import REPOSITORY_ROOT, hand_written_files, subscript_of

# A parameter annotated `Optional` and defaulting to something else says two things at once:
#  the caller may pass `None`, and the caller who passes nothing does not get `None`. Almost
#  always only the second is true, and the body then never handles the `None` it advertises.
#
# The exemptions are the cases where both really are true, keyed by file and parameter name.
_EXEMPTIONS: Final[Dict[Tuple[str, str], str]] = {
    (
        "pyrogram/filters.py",
        "prefixes",
    ): "`None` matches commands written with no prefix at all, `'/'` is the ordinary one.",
    (
        "pyrogram/methods/messages/copy_message.py",
        "reply_markup",
    ): "`object` is the not-specified sentinel, so `None` is free to mean remove the markup.",
    (
        "pyrogram/types/messages_and_media/message.py",
        "reply_markup",
    ): "`object` is the not-specified sentinel, so `None` is free to mean remove the markup.",
}


def mentions_none(node: ast.expr) -> bool:
    """Whether the annotation admits `None`, written in any of the three spellings."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            try:
                return mentions_none(ast.parse(node.value, mode="eval").body)

            except SyntaxError:
                return False

        return node.value is None

    if isinstance(node, ast.Subscript):
        head = node.value
        name = head.attr if isinstance(head, ast.Attribute) else getattr(head, "id", "")

        if name == "Optional":
            return True

        if name == "Union":
            inner = subscript_of(node)
            arguments = inner.elts if isinstance(inner, ast.Tuple) else [inner]

            return any(
                isinstance(argument, ast.Constant) and argument.value is None
                for argument in arguments
            )

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return mentions_none(node.left) or mentions_none(node.right)

    return False


def defaults_to_none(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def parameters_with_defaults(node: ast.AST) -> Iterator[Tuple[ast.arg, ast.expr]]:
    arguments = node.args
    positional: List[ast.arg] = arguments.posonlyargs + arguments.args

    for parameter, default in zip(reversed(positional), reversed(arguments.defaults)):
        yield parameter, default

    for parameter, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
        if default is not None:
            yield parameter, default


def optional_parameters_that_do_not_default_to_none() -> List[Tuple[str, int, str]]:
    found: List[Tuple[str, int, str]] = []

    for path in hand_written_files():
        relative = path.relative_to(REPOSITORY_ROOT).as_posix()
        tree = ast.parse(path.read_text(), filename=relative)

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            for parameter, default in parameters_with_defaults(node):
                if parameter.annotation is None or defaults_to_none(default):
                    continue

                if mentions_none(parameter.annotation):
                    found.append((relative, parameter.lineno, parameter.arg))

    return found


def test_a_parameter_that_admits_none_defaults_to_none() -> None:
    offenders = [
        "{}:{}: {}".format(relative, line, name)
        for relative, line, name in optional_parameters_that_do_not_default_to_none()
        if (relative, name) not in _EXEMPTIONS
    ]

    assert offenders == []


def test_every_exemption_names_a_parameter_that_is_still_there() -> None:
    found = {(relative, name) for relative, _, name in optional_parameters_that_do_not_default_to_none()}

    assert sorted(set(_EXEMPTIONS) - found) == []


def test_the_sweep_reads_the_parameters_it_claims_to() -> None:
    source: str = (
        "def f(\n"
        "    plain: int = 1,\n"
        "    old: Optional[int] = 2,\n"
        "    written: Union[int, None] = 3,\n"
        "    quoted: 'Optional[int]' = 4,\n"
        "    modern: int | None = 5,\n"
        "    correct: Optional[int] = None,\n"
        "    *,\n"
        "    keyword: Optional[int] = 6,\n"
        "): ...\n"
    )
    node = ast.parse(source).body[0]

    caught = [
        parameter.arg
        for parameter, default in parameters_with_defaults(node)
        if parameter.annotation is not None
        and not defaults_to_none(default)
        and mentions_none(parameter.annotation)
    ]

    assert caught == ["modern", "quoted", "written", "old", "keyword"]


def test_the_sweep_reads_the_package_and_not_the_generated_tree() -> None:
    files = list(hand_written_files())

    assert len(files) > 100
    assert REPOSITORY_ROOT / "pyrogram" / "client.py" in files
    assert not [path for path in files if (REPOSITORY_ROOT / "pyrogram" / "raw") in path.parents]


def test_a_module_outside_the_package_is_not_swept() -> None:
    assert pathlib.Path(__file__) not in set(hand_written_files())
