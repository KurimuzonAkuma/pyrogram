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

from __future__ import annotations as _annotations

from pyrogram import raw

from ..object import Object


class ChecklistTasksDone(Object):
    """Some tasks from a checklist were marked as done or not done.

    Parameters:
        checklist_message_id (``int``):
            Identifier of the message with the checklist.
            Can be None if the message was deleted.

        marked_as_done_task_ids (List of ``int``):
            Identifiers of tasks that were marked as done

        marked_as_not_done_task_ids (List of ``int``):
            Identifiers of tasks that were marked as not done
    """

    def __init__(
        self,
        *,
        checklist_message_id: int,
        marked_as_done_task_ids: list[int],
        marked_as_not_done_task_ids: list[int],
    ):

        super().__init__()

        self.checklist_message_id = checklist_message_id
        self.marked_as_done_task_ids = marked_as_done_task_ids
        self.marked_as_not_done_task_ids = marked_as_not_done_task_ids

    @staticmethod
    def _parse(message: raw.types.MessageService) -> ChecklistTasksDone:
        action: raw.types.MessageActionTodoCompletions = message.action

        return ChecklistTasksDone(
            checklist_message_id=getattr(message.reply_to, "reply_to_msg_id", None),
            marked_as_done_task_ids=action.completed,
            marked_as_not_done_task_ids=action.incompleted,
        )
