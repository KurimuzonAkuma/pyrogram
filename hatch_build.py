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

import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

sys.path.insert(0, ".")


class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name not in ["wheel", "install"]:
            return

        # `hatch_build.py` is imported for every build target, and only wheel and install
        #  builds reach this line, so the compilers are imported here rather than at the top.
        from compiler.api.compiler import start as compile_api  # noqa: PLC0415
        from compiler.errors.compiler import start as compile_errors  # noqa: PLC0415

        compile_api(format=False)
        compile_errors()
