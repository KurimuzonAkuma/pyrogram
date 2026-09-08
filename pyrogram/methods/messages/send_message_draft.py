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

import pyrogram
from pyrogram import enums, raw, types


class SendMessageDraft:
    async def send_message_draft(
        self: pyrogram.Client,
        chat_id: int | str,
        draft_id: int,
        text: str = "",
        message_thread_id: int | None = None,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        can_stop: bool | None = None,
        keep_on_stop: bool | None = None,
    ) -> bool:
        """Use this method to stream a partial message to a user while the message is being generated.

        .. note::

            The streamed draft is ephemeral and acts as a temporary 30-second preview - once the output is finalized,
            you must call :meth:`~pyrogram.Client.send_message` with the complete message to persist it in the user's chat.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            draft_id (``int``):
                Unique identifier of the message draft, must be non-zero.
                Changes of drafts with the same identifier are animated.

            text (``str``):
                Text of the message to be sent, 0-4096 characters after entities parsing.
                Pass an empty text to show a "Thinking…" placeholder.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            can_stop (``bool``, *optional*):
                Pass *True* to show the user a button to stop further drafts.

            keep_on_stop (``bool``, *optional*):
                Pass *True* to keep the draft in the chat when the button is pressed.
                The draft will still disappear after a short time or if the bot sends a message.
                To fully preserve the partial draft, the bot should send it as a new message.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python


                text = "Hello! I'm your Pyrogram bot! How can I help you?"
                words = text.split()
                draft_id = app.rnd_id()

                # Send thinking placeholder
                await app.send_message_draft(chat_id, draft_id)

                await asyncio.sleep(5)

                for i, word in enumerate(words):
                    await app.send_message_draft(
                        chat_id=chat_id,
                        draft_id=draft_id,
                        text=" ".join(words[:i+1]),
                    )

                    await asyncio.sleep(0.33)

                await app.send_message(chat_id, text)

        """
        return await self.invoke(
            raw.functions.messages.SetTyping(
                peer=await self.resolve_peer(chat_id),
                action=raw.types.SendMessageTextDraftAction(
                    random_id=draft_id,
                    text=await types.FormattedText(
                        text=text, parse_mode=parse_mode, entities=entities
                    ).write(self),
                    can_stop=can_stop,
                    keep_on_stop=keep_on_stop,
                ),
                top_msg_id=message_thread_id,
            )
        )
