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

from .can_post_stories import CanPostStories
from .copy_story import CopyStory
from .delete_stories import DeleteStories
from .edit_story_caption import EditStoryCaption
from .edit_story_media import EditStoryMedia
from .edit_story_privacy import EditStoryPrivacy
from .enable_stealth_mode import EnableStealthMode
from .forward_story import ForwardStory
from .get_all_stories import GetAllStories
from .get_archived_stories import GetArchivedStories
from .get_chat_stories import GetChatStories
from .get_pinned_stories import GetPinnedStories
from .get_stories import GetStories
from .get_story_views import GetStoryViews
from .hide_chat_stories import HideChatStories
from .pin_chat_stories import PinChatStories
from .read_chat_stories import ReadChatStories
from .send_story import SendStory
from .show_chat_stories import ShowChatStories
from .unpin_chat_stories import UnpinChatStories
from .view_stories import ViewStories


class Stories(
    CanPostStories,
    CopyStory,
    DeleteStories,
    EditStoryCaption,
    EditStoryMedia,
    EditStoryPrivacy,
    EnableStealthMode,
    ForwardStory,
    GetAllStories,
    GetArchivedStories,
    GetChatStories,
    GetPinnedStories,
    GetStories,
    GetStoryViews,
    HideChatStories,
    PinChatStories,
    ReadChatStories,
    SendStory,
    ShowChatStories,
    UnpinChatStories,
    ViewStories,
):
    pass
