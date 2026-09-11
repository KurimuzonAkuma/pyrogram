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

from ..object import Object


class RichMessageButton(Object):
    """This object represents a button in a :obj:`~pyrogram.types.RichMessage`.

    Exactly one of the fields other than *text* and *style* must be used to specify the type of the button.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the button.
            May contain only plain text, :obj:`~pyrogram.types.RichTextCustomEmoji` and :obj:`~pyrogram.types.RichTextDateTime` entities.

        style (:obj:`~pyrogram.enums.ButtonStyle`, *optional*):
            Style of the button.
            Must be one of :obj:`~pyrogram.enums.ButtonStyle.DANGER`, :obj:`~pyrogram.enums.ButtonStyle.SUCCESS`, :obj:`~pyrogram.enums.ButtonStyle.PRIMARY`, or :obj:`~pyrogram.enums.ButtonStyle.LINK` (the button is shown as a regular link without borders).
            Apps may use theme-specific colors for the button background and text based on the style.
            The style “link” is allowed only for callback buttons.

        url (``str``, *optional*):
            HTTP or tg:// URL to be opened when the button is pressed.
            Links ``tg://user?id=<user_id>`` can be used to mention a user by their identifier without using a username, if this is allowed by their privacy settings.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the `Web App <https://core.telegram.org/bots/webapps>`_ that will be launched when the user
            presses the button. The Web App will be able to send an arbitrary message on behalf of the user using the
            method :meth:`~pyrogram.Client.answer_web_app_query`. Available only in private chats between a user and the
            bot.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
            An HTTP URL used to automatically authorize the user. Can be used as a replacement for
            the `Telegram Login Widget <https://core.telegram.org/widgets/login>`_.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert the bot's username and the specified inline query in the input field.
            May be empty, in which case just the bot's username will be inserted.
            Not supported for messages sent in channel direct messages chats and on behalf of a business account.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username and the specified inline query in the current chat's input field.
            May be empty, in which case only the bot's username will be inserted.
            Not supported in channels and for messages sent in channel direct messages chats and on behalf of a business account.

        switch_inline_query_chosen_chat (:obj:`~pyrogram.types.SwitchInlineQueryChosenChat`, *optional*):
            If set, pressing the button will prompt the user to select one of their chats of the specified type, open that chat and insert the bot's username and the specified inline query in the input field.
            Not supported for messages sent in channel direct messages chats and on behalf of a business account.

        copy_text (:obj:`~pyrogram.types.CopyTextButton`, *optional*):
            A button that copies specified text to clipboard.
            Limited to 256 character.

        disabled (:obj:`~pyrogram.types.DisabledButton`, *optional*):
            If set, then the button is disabled and does nothing.
    """

    def __init__(
        self,
        text: types.RichText,
        style: enums.ButtonStyle = enums.ButtonStyle.DEFAULT,
        url: str | None = None,
        callback_data: str | bytes | None = None,
        web_app: types.WebAppInfo | None = None,
        login_url: types.LoginUrl | None = None,
        switch_inline_query: str | None = None,
        switch_inline_query_current_chat: str | None = None,
        switch_inline_query_chosen_chat: types.SwitchInlineQueryChosenChat | None = None,
        copy_text: types.CopyTextButton | None = None,
        disabled: types.DisabledButton | None = None,
    ):
        super().__init__()

        self.text = text
        self.style = style
        self.url = url
        self.callback_data = callback_data
        self.web_app = web_app
        self.login_url = login_url
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.switch_inline_query_chosen_chat = switch_inline_query_chosen_chat
        self.copy_text = copy_text
        self.disabled = disabled

    @staticmethod
    async def _parse(
        client: pyrogram.Client, button: raw.types.TextButton | raw.types.PageButton
    ) -> RichMessageButton:
        button_text = await types.RichText._parse(client, button.text)
        button_type = button.type
        button_style = enums.ButtonStyle.DEFAULT

        if button.style:
            if button.style.bg_primary:
                button_style = enums.ButtonStyle.PRIMARY
            elif button.style.bg_danger:
                button_style = enums.ButtonStyle.DANGER
            elif button.style.bg_success:
                button_style = enums.ButtonStyle.SUCCESS
            elif button.style.link:
                button_style = enums.ButtonStyle.LINK

        if isinstance(button_type, raw.types.InlineButtonTypeCallback):
            # Try decode data to keep it as string, but if fails, fallback to bytes so we don't lose any information,
            # instead of decoding by ignoring/replacing errors.
            try:
                data = button_type.data.decode()
            except UnicodeDecodeError:
                data = button_type.data

            return RichMessageButton(
                text=button_text,
                callback_data=data,
                style=button_style,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeCopy):
            return RichMessageButton(
                text=button_text,
                copy_text=types.CopyTextButton(text=button_type.copy_text),
                style=button_style,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeDisabled):
            return RichMessageButton(
                text=button_text,
                disabled=types.DisabledButton(),
                style=button_style,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeSwitchInline):
            if button_type.peer_types:
                return RichMessageButton(
                    text=button_text,
                    switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat._parse(
                        button_type
                    ),
                    style=button_style,
                )

            if button_type.same_peer:
                return RichMessageButton(
                    text=button_text,
                    switch_inline_query_current_chat=button_type.query,
                    style=button_style,
                )

            return RichMessageButton(
                text=button_text,
                switch_inline_query=button_type.query,
                style=button_style,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeUrl):
            return RichMessageButton(
                text=button_text,
                url=button_type.url,
                style=button_style,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeUrlAuth):
            return RichMessageButton(
                text=button_text,
                login_url=types.LoginUrl.read(button_type),
                style=button_style,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeWebView):
            return RichMessageButton(
                text=button_text,
                web_app=types.WebAppInfo(url=button_type.url),
                style=button_style,
            )

        # `InlineButtonType` holds constructors a rich button cannot express, `inlineButtonTypeBuy`
        #  and `inlineButtonTypeGame` among them, and the server may add more. Falling through used
        #  to hand a `None` to `RichBlockButtons.buttons`, which then fails wherever it is read.
        return RichMessageButton(text=button_text, style=button_style)

    async def write(
        self, client: pyrogram.Client, is_block: bool = False
    ) -> raw.types.TextButton | raw.types.PageButton:
        style = (
            raw.types.RichButtonStyle(
                bg_primary=self.style == enums.ButtonStyle.PRIMARY,
                bg_danger=self.style == enums.ButtonStyle.DANGER,
                bg_success=self.style == enums.ButtonStyle.SUCCESS,
                link=self.style == enums.ButtonStyle.LINK,
            )
            if self.style != enums.ButtonStyle.DEFAULT
            else None
        )

        set_fields = [
            name
            for name, value in (
                ("url", self.url),
                ("callback_data", self.callback_data),
                ("web_app", self.web_app),
                ("login_url", self.login_url),
                ("switch_inline_query", self.switch_inline_query),
                ("switch_inline_query_current_chat", self.switch_inline_query_current_chat),
                ("switch_inline_query_chosen_chat", self.switch_inline_query_chosen_chat),
                ("copy_text", self.copy_text),
                ("disabled", self.disabled),
            )
            if value is not None
        ]

        # The raw button carries one `InlineButtonType`, so a second field set here would
        #  overwrite the first without a word, and none at all sends a button with no type.
        if len(set_fields) != 1:
            raise ValueError(
                "Exactly one field other than `text` and `style` must be set, "
                f"got {set_fields or 'none'}"
            )

        button_type = None

        if self.callback_data is not None:
            # Telegram only wants bytes, but we are allowed to pass strings too, for convenience.
            button_type = raw.types.InlineButtonTypeCallback(
                data=(
                    bytes(self.callback_data, "utf-8")
                    if isinstance(self.callback_data, str)
                    else self.callback_data
                )
            )

        if self.copy_text is not None:
            button_type = raw.types.InlineButtonTypeCopy(
                copy_text=self.copy_text.text,
            )

        if self.disabled is not None:
            button_type = raw.types.InlineButtonTypeDisabled()

        if self.switch_inline_query is not None:
            button_type = raw.types.InlineButtonTypeSwitchInline(
                query=self.switch_inline_query,
            )

        if self.switch_inline_query_chosen_chat is not None:
            peer_types = []

            if self.switch_inline_query_chosen_chat.allow_user_chats:
                peer_types.append(raw.types.InlineQueryPeerTypePM())
            if self.switch_inline_query_chosen_chat.allow_bot_chats:
                peer_types.extend(
                    (
                        raw.types.InlineQueryPeerTypeBotPM(),
                        raw.types.InlineQueryPeerTypeSameBotPM(),
                    )
                )
            if self.switch_inline_query_chosen_chat.allow_group_chats:
                peer_types.extend(
                    (raw.types.InlineQueryPeerTypeChat(), raw.types.InlineQueryPeerTypeMegagroup())
                )
            if self.switch_inline_query_chosen_chat.allow_channel_chats:
                peer_types.append(raw.types.InlineQueryPeerTypeBroadcast())

            button_type = raw.types.InlineButtonTypeSwitchInline(
                query=self.switch_inline_query_chosen_chat.query, peer_types=peer_types
            )

        if self.switch_inline_query_current_chat is not None:
            button_type = raw.types.InlineButtonTypeSwitchInline(
                query=self.switch_inline_query_current_chat,
                same_peer=True,
            )

        if self.url is not None:
            button_type = raw.types.InlineButtonTypeUrl(
                url=self.url,
            )

        if self.login_url is not None:
            button_type = raw.types.InputInlineButtonTypeUrlAuth(
                url=self.login_url.url,
                request_write_access=self.login_url.request_write_access,
                fwd_text=self.login_url.forward_text,
                bot=await client.resolve_peer(self.login_url.bot_username or "self"),
            )

        if self.web_app is not None:
            button_type = raw.types.InlineButtonTypeWebView(
                url=self.web_app.url,
            )

        if is_block:
            return raw.types.PageButton(
                text=await types.RichText._write(client, self.text),
                type=button_type,
                style=style,
            )

        return raw.types.TextButton(
            text=await types.RichText._write(client, self.text),
            type=button_type,
            style=style,
        )
