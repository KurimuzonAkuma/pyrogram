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

import base64
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from collections.abc import Iterable

if TYPE_CHECKING:
    from pyrogram import raw


@dataclass(frozen=True)
class UpdateState:
    id: int
    pts: int | None
    qts: int | None
    date: int | None
    seq: int | None


class Storage(ABC):
    """Abstract class for storage engines."""

    OLD_SESSION_STRING_FORMAT = ">B?256sI?"
    OLD_SESSION_STRING_FORMAT_64 = ">B?256sQ?"
    SESSION_STRING_SIZE = 351
    SESSION_STRING_SIZE_64 = 356

    SESSION_STRING_FORMAT = ">BI?256sQ?"

    @abstractmethod
    async def open(self):
        """Opens the storage engine."""
        raise NotImplementedError

    @abstractmethod
    async def save(self):
        """Saves the current state of the storage engine."""
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        """Closes the storage engine."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        """Deletes the storage file."""
        raise NotImplementedError

    @abstractmethod
    async def update_peers(self, peers: Iterable[tuple[int, int, str, str | None]]):
        """
        Update the peers table with the provided information.

        Parameters:
            peers (List of ``tuple[int, int, str, str | None]``):
                A list of tuples containing the
                information of the peers to be updated.
                Each tuple must contain the following information:
                - ``int``: The peer id.
                - ``int``: The peer access hash.
                - ``str``: The peer type ("user", "bot", "group", "direct", "channel", "forum", "supergroup" or "community").
                - ``str`` | ``None``: The peer phone number (if any).
        """
        raise NotImplementedError

    @abstractmethod
    async def update_usernames(self, usernames: Iterable[tuple[int, list[str | None]]]):
        """
        Update the usernames table with the provided information.

        Parameters:
            usernames (List of ``tuple[int, list[str | None]]``):
                A list of tuples containing the
                information of the usernames to be updated. Each tuple must contain the following
                information:
                - ``int``: The peer id.
                - List of ``str`` | ``None``: The peer username (if any).
        """
        raise NotImplementedError

    @abstractmethod
    async def get_update_states(self, ids: int | Iterable[int] | None = None) -> list[UpdateState]:
        """Get the update state of the current session.

        Parameters:
            ids (``int`` | Iterable of ``int``, *optional*):
                Limit the result to the specified state IDs.
                If omitted, all states are returned.

        Returns:
            List of ``UpdateState``: On success, a list of update states is returned.
        """
        raise NotImplementedError

    @abstractmethod
    async def set_update_state(self, update_state: UpdateState | Iterable[UpdateState]):
        """Set the update state of the current session.

        Parameters:
            update_state (``UpdateState`` | Iterable of ``UpdateState``):
                The update state or states to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_update_state(self, state_id: int | Iterable[int]):
        """Delete the update state of the current session.

        Parameters:
            state_id (``int`` | List of ``int``):
                The id of the update state to delete.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_id(self, peer_id: int) -> raw.base.InputPeer | None:
        """Retrieve a peer by its ID.

        Parameters:
            peer_id (``int``):
                The ID of the peer to retrieve.

        Returns:
            :obj:`~pyrogram.raw.base.InputPeer` | ``None``: On success, the resolved peer is returned.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_username(self, username: str) -> raw.base.InputPeer | None:
        """Retrieve a peer by its username.

        Parameters:
            username (``str``):
                The username of the peer to retrieve.

        Returns:
            :obj:`~pyrogram.raw.base.InputPeer` | ``None``: On success, the resolved peer is returned.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_peer_by_phone_number(self, phone_number: str) -> raw.base.InputPeer | None:
        """Retrieve a peer by its phone number.

        Parameters:
            phone_number (``str``):
                The phone number of the peer to retrieve.

        Returns:
            :obj:`~pyrogram.raw.base.InputPeer` | ``None``: On success, the resolved peer is returned.
        """
        raise NotImplementedError

    @abstractmethod
    async def dc_id(self, value: int | None = None) -> int:
        """Get or set the DC ID of the current session.

        Parameters:
            value (``int``, *optional*):
                The DC ID to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def api_id(self, value: int | None = None) -> int:
        """Get or set the API ID of the current session.

        Parameters:
            value (``int``, *optional*):
                The API ID to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def server_address(self, value: str | None = None) -> str:
        """Get or set the server address of the current session.

        Parameters:
            value (``str``, *optional*):
                The server address to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def port(self, value: int | None = None) -> int:
        """Get or set the server port of the current session.

        Parameters:
            value (``int``, *optional*):
                The server port to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def test_mode(self, value: bool | None = None) -> bool:
        """Get or set the test mode of the current session.

        Parameters:
            value (``bool``, *optional*):
                The test mode to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def auth_key(self, value: bytes | None = None) -> bytes:
        """Get or set the authorization key of the current session.

        Parameters:
            value (``bytes``, *optional*):
                The authorization key to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def date(self, value: int | None = None) -> int:
        """Get or set the date of the current session.

        Parameters:
            value (``int``, *optional*):
                The date to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def user_id(self, value: int | None = None) -> int:
        """Get or set the user ID of the current session.

        Parameters:
            value (``int``, *optional*):
                The user ID to set.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_bot(self, value: bool | None = None) -> bool:
        """Get or set the bot flag of the current session.

        Parameters:
            value (``bool``, *optional*):
                The bot flag to set.
        """
        raise NotImplementedError

    async def export_session_string(self) -> str:
        """Exports the session string for the current session.

        Returns:
            ``str``: The session string for the current session.
        """
        packed = struct.pack(
            self.SESSION_STRING_FORMAT,
            await self.dc_id(),
            await self.api_id(),
            await self.test_mode(),
            await self.auth_key(),
            await self.user_id(),
            await self.is_bot(),
        )

        return base64.urlsafe_b64encode(packed).decode().rstrip("=")
