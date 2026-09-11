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

import logging
from datetime import datetime
from typing import BinaryIO
from collections.abc import Callable

import pyrogram
from pyrogram import StopTransmission, enums, raw, types, utils
from pyrogram._typing import PathType
from pyrogram.errors import FilePartMissing

log = logging.getLogger(__name__)


class SendLivePhoto:
    async def send_live_photo(
        self: pyrogram.Client,
        chat_id: int | str,
        live_photo: PathType | BinaryIO,
        photo: PathType | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[types.MessageEntity] | None = None,
        has_spoiler: bool | None = None,
        width: int = 0,
        height: int = 0,
        disable_notification: bool | None = None,
        message_thread_id: int | None = None,
        direct_messages_topic_id: int | None = None,
        ephemeral_message_parameters: types.EphemeralMessageParameters | None = None,
        effect_id: int | None = None,
        show_caption_above_media: bool | None = None,
        reply_parameters: types.ReplyParameters | None = None,
        schedule_date: datetime | None = None,
        repeat_period: int | None = None,
        protect_content: bool | None = None,
        business_connection_id: str | None = None,
        allow_paid_broadcast: bool | None = None,
        paid_message_star_count: int | None = None,
        suggested_post_parameters: types.SuggestedPostParameters | None = None,
        reply_markup: (
            types.InlineKeyboardMarkup
            | types.ReplyKeyboardMarkup
            | types.ReplyKeyboardRemove
            | types.ForceReply
            | None
        ) = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> types.Message | None:
        """Send video files.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            live_photo (``str`` | ``os.PathLike`` | ``BinaryIO``):
                Live photo video to send.
                The video must be no longer than 10 seconds and must not exceed 10 MB in size.
                Pass a file_id as string to send a video that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a video from the Internet,
                pass a file path as string to upload a new video that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            photo (``str`` | ``os.PathLike`` | ``BinaryIO``):
                The static photo to send.
                The video must be no longer than 10 seconds and must not exceed 10 MB in size.
                Pass a file_id as string to send a video that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a video from the Internet,
                pass a file path as string to upload a new video that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            caption (``str``, *optional*):
                Video caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the video needs to be covered with a spoiler animation.

            width (``int``, *optional*):
                Video width.

            height (``int``, *optional*):
                Video height.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For direct chats only.only.

            ephemeral_message_parameters (:obj:`~pyrogram.types.EphemeralMessageParameters`, *optional*):
                Parameters of the ephemeral message to send.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            no_sound (``bool``, *optional*):
                Pass True, if the uploaded video is a video message with no sound.
                Doesn't work for external links.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent live photo message is returned, otherwise, in
            case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned.
        """
        file = None
        peer = await self.resolve_peer(chat_id)

        try:
            while True:
                try:
                    if ephemeral_message_parameters:
                        rpc = raw.functions.ephemeral.SendMessage(
                            peer=peer,
                            receiver_id=await self.resolve_peer(
                                ephemeral_message_parameters.receiver_user_id
                            ),
                            query_id=int(ephemeral_message_parameters.callback_query_id)
                            if ephemeral_message_parameters.callback_query_id is not None
                            else None,
                            media=await types.InputMediaLivePhoto(
                                media=live_photo,
                                photo=photo,
                                caption=caption,
                                parse_mode=parse_mode,
                                caption_entities=caption_entities,
                                has_spoiler=has_spoiler,
                            ).write(
                                client=self,
                                width=width,
                                height=height,
                                progress=progress,
                                progress_args=progress_args,
                            ),
                            reply_to=await utils.get_reply_to(
                                self, reply_parameters, message_thread_id, direct_messages_topic_id
                            ),
                            random_id=self.rnd_id(),
                            invert_media=show_caption_above_media,
                            anchor=ephemeral_message_parameters.replace_callback_query_message,
                            reply_markup=await reply_markup.write(self) if reply_markup else None,
                            **await utils.parse_text_entities(
                                self, caption, parse_mode, caption_entities
                            ),
                        )
                    else:
                        rpc = raw.functions.messages.SendMedia(
                            peer=peer,
                            media=await types.InputMediaLivePhoto(
                                media=live_photo,
                                photo=photo,
                                caption=caption,
                                parse_mode=parse_mode,
                                caption_entities=caption_entities,
                                has_spoiler=has_spoiler,
                            ).write(
                                client=self,
                                width=width,
                                height=height,
                                progress=progress,
                                progress_args=progress_args,
                            ),
                            silent=disable_notification or None,
                            invert_media=show_caption_above_media,
                            reply_to=await utils.get_reply_to(
                                self, reply_parameters, message_thread_id, direct_messages_topic_id
                            ),
                            random_id=self.rnd_id(),
                            schedule_date=utils.datetime_to_timestamp(schedule_date),
                            schedule_repeat_period=repeat_period,
                            noforwards=protect_content,
                            allow_paid_floodskip=allow_paid_broadcast,
                            allow_paid_stars=paid_message_star_count,
                            suggested_post=suggested_post_parameters.write()
                            if suggested_post_parameters
                            else None,
                            reply_markup=await reply_markup.write(self) if reply_markup else None,
                            effect=effect_id,
                            **await utils.parse_text_entities(
                                self, caption, parse_mode, caption_entities
                            ),
                        )

                    r = await self.invoke(rpc, business_connection_id=business_connection_id)
                except FilePartMissing as e:
                    await self.save_file(live_photo, file_id=file.id, file_part=e.file_part)
                else:
                    messages = await utils.parse_messages(client=self, messages=r)

                    return messages[0] if messages else None
        except StopTransmission:
            return None
