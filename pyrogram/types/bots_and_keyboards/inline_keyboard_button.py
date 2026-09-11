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


class InlineKeyboardButton(Object):
    """One button of an inline keyboard.

    You must use exactly one of the optional fields.

    Parameters:
        text (``str``):
            Label text on the button.

        icon_custom_emoji_id (``str``, *optional*):
            Identifier of the custom emoji that must be shown on the button.

        style (:obj:`~pyrogram.enums.ButtonStyle`, *optional*):
            Style of the button.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when button is pressed, 1-64 bytes.

        requires_password (``bool``, *optional*):
            A button that asks for the 2-step verification password of the current user and then sends a callback query to a bot Data to be sent to the bot via a callback query.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the `Web App <https://core.telegram.org/bots/webapps>`_ that will be launched when the user
            presses the button. The Web App will be able to send an arbitrary message on behalf of the user using the
            method :meth:`~pyrogram.Client.answer_web_app_query`. Available only in private chats between a user and the
            bot.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
             An HTTP URL used to automatically authorize the user. Can be used as a replacement for
             the `Telegram Login Widget <https://core.telegram.org/widgets/login>`_.

        user_id (``int``, *optional*):
            User id, for links to the user profile.

        switch_inline_query (``str``, *optional*):
            If set, pressing the button will prompt the user to select one of their chats, open that chat and insert
            the bot's username and the specified inline query in the input field. Can be empty, in which case just
            the bot's username will be inserted.Note: This offers an easy way for users to start using your bot in
            inline mode when they are currently in a private chat with it. Especially useful when combined with
            switch_pm… actions – in this case the user will be automatically returned to the chat they switched from,
            skipping the chat selection screen.

        switch_inline_query_current_chat (``str``, *optional*):
            If set, pressing the button will insert the bot's username and the specified inline query in the current
            chat's input field. Can be empty, in which case only the bot's username will be inserted.This offers a
            quick way for the user to open your bot in inline mode in the same chat – good for selecting something
            from multiple options.

        switch_inline_query_chosen_chat (:obj:`~pyrogram.types.SwitchInlineQueryChosenChat`, *optional*):
            If set, pressing the button will prompt the user to select one of their chats of the specified type, open that chat and insert
            the bot's username and the specified inline query in the input field.
            Not supported for messages sent in channel direct messages chats and on behalf of a business account.

        copy_text (:obj:`~pyrogram.types.CopyTextButton`, *optional*):
            A button that copies specified text to clipboard.
            Limited to 256 character.

        callback_game (:obj:`~pyrogram.types.CallbackGame`, *optional*):
            Description of the game that will be launched when the user presses the button.
            **NOTE**: This type of button **must** always be the first button in the first row.

        pay (``bool``, *optional*):
            Pass True, to send a Pay button.
            Substrings `⭐` and `XTR` in the buttons's text will be replaced with a Telegram Star icon.
            Available in :meth:`~pyrogram.Client.send_invoice`.

            **NOTE**: This type of button **must** always be the first button in the first row and can only be used in invoice messages.

        disabled (:obj:`~pyrogram.types.DisabledButton`, *optional*):
            If set, then the button is disabled and does nothing.
    """

    def __init__(
        self,
        text: str,
        icon_custom_emoji_id: str | None = None,
        style: enums.ButtonStyle = enums.ButtonStyle.DEFAULT,
        url: str | None = None,
        callback_data: str | bytes | None = None,
        requires_password: bool | None = None,
        web_app: types.WebAppInfo | None = None,
        login_url: types.LoginUrl | None = None,
        user_id: int | None = None,
        switch_inline_query: str | None = None,
        switch_inline_query_current_chat: str | None = None,
        switch_inline_query_chosen_chat: types.SwitchInlineQueryChosenChat | None = None,
        copy_text: types.CopyTextButton | None = None,
        callback_game: types.CallbackGame | None = None,
        pay: bool | None = None,
        disabled: types.DisabledButton | None = None,
    ):
        super().__init__()

        self.text = str(text)
        self.icon_custom_emoji_id = icon_custom_emoji_id
        self.style = style
        self.url = url
        self.callback_data = callback_data
        self.requires_password = requires_password
        self.web_app = web_app
        self.login_url = login_url
        self.user_id = user_id
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.switch_inline_query_chosen_chat = switch_inline_query_chosen_chat
        self.copy_text = copy_text
        self.callback_game = callback_game
        self.pay = pay
        self.disabled = disabled

    @staticmethod
    def read(button: raw.base.KeyboardInlineButton):
        button_text = button.text
        button_type = button.type
        button_style = enums.ButtonStyle.DEFAULT

        icon_custom_emoji_id = None

        if button.style:
            if button.style.bg_primary:
                button_style = enums.ButtonStyle.PRIMARY
            elif button.style.bg_danger:
                button_style = enums.ButtonStyle.DANGER
            elif button.style.bg_success:
                button_style = enums.ButtonStyle.SUCCESS

            if button.style.icon:
                icon_custom_emoji_id = str(button.style.icon)

        if isinstance(button_type, raw.types.InlineButtonTypeBuy):
            return InlineKeyboardButton(
                text=button_text,
                pay=True,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeCallback):
            # Try decode data to keep it as string, but if fails, fallback to bytes so we don't lose any information,
            # instead of decoding by ignoring/replacing errors.
            try:
                data = button_type.data.decode()
            except UnicodeDecodeError:
                data = button_type.data

            return InlineKeyboardButton(
                text=button_text,
                callback_data=data,
                requires_password=button_type.requires_password,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeCopy):
            return InlineKeyboardButton(
                text=button_text,
                copy_text=types.CopyTextButton(text=button_type.copy_text),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeDisabled):
            return InlineKeyboardButton(
                text=button_text,
                disabled=types.DisabledButton(),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeGame):
            return InlineKeyboardButton(
                text=button_text,
                callback_game=types.CallbackGame(),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeSwitchInline):
            if button_type.peer_types:
                return InlineKeyboardButton(
                    text=button_text,
                    switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat._parse(
                        button_type
                    ),
                    style=button_style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                )

            if button_type.same_peer:
                return InlineKeyboardButton(
                    text=button_text,
                    switch_inline_query_current_chat=button_type.query,
                    style=button_style,
                    icon_custom_emoji_id=icon_custom_emoji_id,
                )

            return InlineKeyboardButton(
                text=button_text,
                switch_inline_query=button_type.query,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeUrl):
            return InlineKeyboardButton(
                text=button_text,
                url=button_type.url,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeUrlAuth):
            return InlineKeyboardButton(
                text=button_text,
                login_url=types.LoginUrl.read(button_type),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeUserProfile):
            return InlineKeyboardButton(
                text=button_text,
                user_id=button_type.user_id,
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

        if isinstance(button_type, raw.types.InlineButtonTypeWebView):
            return InlineKeyboardButton(
                text=button_text,
                web_app=types.WebAppInfo(url=button_type.url),
                style=button_style,
                icon_custom_emoji_id=icon_custom_emoji_id,
            )

    async def write(self, client: pyrogram.Client) -> raw.types.KeyboardInlineButton:
        if self.style is enums.ButtonStyle.LINK:
            # `keyboardButtonStyle` carries no `link` flag, so the style would go out empty.
            #  `compiler/api/source/main_api.tl:2188`
            raise ValueError("`ButtonStyle.LINK` is only available on `RichMessageButton`")

        style = (
            raw.types.KeyboardButtonStyle(
                bg_primary=self.style == enums.ButtonStyle.PRIMARY,
                bg_danger=self.style == enums.ButtonStyle.DANGER,
                bg_success=self.style == enums.ButtonStyle.SUCCESS,
                icon=int(self.icon_custom_emoji_id)
                if self.icon_custom_emoji_id is not None
                else None,
            )
            if self.style != enums.ButtonStyle.DEFAULT or self.icon_custom_emoji_id is not None
            else None
        )

        button_type = None

        if self.pay is not None:
            button_type = raw.types.InlineButtonTypeBuy()

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

        if self.callback_game is not None:
            button_type = raw.types.InlineButtonTypeGame()

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
                    (raw.types.InlineQueryPeerTypeBotPM(), raw.types.InlineQueryPeerTypeSameBotPM())
                )
            if self.switch_inline_query_chosen_chat.allow_group_chats:
                peer_types.extend(
                    (raw.types.InlineQueryPeerTypeChat(), raw.types.InlineQueryPeerTypeMegagroup())
                )
            if self.switch_inline_query_chosen_chat.allow_channel_chats:
                peer_types.append(raw.types.InlineQueryPeerTypeBroadcast())

            button_type = raw.types.InlineButtonTypeSwitchInline(
                query=self.switch_inline_query_chosen_chat.query,
                peer_types=peer_types,
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

        if self.user_id is not None:
            button_type = raw.types.InputInlineButtonTypeUserProfile(
                user_id=await client.resolve_peer(self.user_id),
            )

        if self.web_app is not None:
            button_type = raw.types.InlineButtonTypeWebView(
                url=self.web_app.url,
            )

        return raw.types.KeyboardInlineButton(
            text=self.text,
            type=button_type,
            style=style,
        )
