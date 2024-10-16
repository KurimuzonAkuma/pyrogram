from typing import (
    Dict,
    Union,
)
from typing_extensions import TypeAlias

import pyrogram
from pyrogram.handlers import (
    CallbackQueryHandler,
    ChatBoostHandler,
    ChatJoinRequestHandler,
    ChatMemberUpdatedHandler,
    ChosenInlineResultHandler,
    DeletedMessagesHandler,
    EditedMessageHandler,
    InlineQueryHandler,
    MessageHandler,
    MessageReactionCountHandler,
    MessageReactionHandler,
    PollHandler,
    PreCheckoutQueryHandler,
    PurchasedPaidMediaHandler,
    ShippingQueryHandler,
    StoryHandler,
    UserStatusHandler,
)
from pyrogram.raw.core import TLObject
from pyrogram.raw.types import (
    Channel,
    ChannelForbidden,
    Chat,
    ChatEmpty,
    ChatForbidden,
    UpdateBotCallbackQuery,
    UpdateBotChatBoost,
    UpdateBotChatInviteRequester,
    UpdateBotDeleteBusinessMessage,
    UpdateBotEditBusinessMessage,
    UpdateBotInlineQuery,
    UpdateBotInlineSend,
    UpdateBotMessageReaction,
    UpdateBotMessageReactions,
    UpdateBotNewBusinessMessage,
    UpdateBotPrecheckoutQuery,
    UpdateBotPurchasedPaidMedia,
    UpdateBotShippingQuery,
    UpdateBusinessBotCallbackQuery,
    UpdateChannelParticipant,
    UpdateChatParticipant,
    UpdateDeleteChannelMessages,
    UpdateDeleteMessages,
    UpdateEditChannelMessage,
    UpdateEditMessage,
    UpdateInlineBotCallbackQuery,
    UpdateMessagePoll,
    UpdateNewChannelMessage,
    UpdateNewMessage,
    UpdateNewScheduledMessage,
    UpdateStory,
    UpdateUserStatus,
    User,
    UserEmpty,
)
from pyrogram.utils import parse_deleted_messages

UsersType: TypeAlias = Dict[int, Union[User, UserEmpty]]
ChatsType: TypeAlias = Dict[int, Union[Channel, ChannelForbidden, Chat, ChatEmpty, ChatForbidden]]

NewMessageType: TypeAlias = Union[
    UpdateNewMessage,
    UpdateNewChannelMessage,
    UpdateNewScheduledMessage,
    UpdateBotNewBusinessMessage
]
EditMessageType: TypeAlias = Union[
    UpdateEditMessage, UpdateEditChannelMessage, UpdateBotEditBusinessMessage
]
DeleteMessageType: TypeAlias = Union[
    UpdateDeleteMessages,
    UpdateDeleteChannelMessages,
    UpdateBotDeleteBusinessMessage,
]
CallbackQueryUpdateType: TypeAlias = Union[UpdateBotCallbackQuery, UpdateInlineBotCallbackQuery, UpdateBusinessBotCallbackQuery]
ChatMemberUpdateType: TypeAlias = Union[UpdateChatParticipant, UpdateChannelParticipant]
UserStatusUpdateType: TypeAlias = Union[UpdateUserStatus]
InlineQueryUpdateType: TypeAlias = Union[UpdateBotInlineQuery]
PollUpdateType: TypeAlias = Union[UpdateMessagePoll]
ChosenInlineResultUpdateType: TypeAlias = Union[UpdateBotInlineSend]
ChatJoinRequestUpdateType: TypeAlias = Union[UpdateBotChatInviteRequester]
NewStoryUpdateType: TypeAlias = Union[UpdateStory]
BotPreCheckoutQueryUpdateType: TypeAlias = Union[UpdateBotPrecheckoutQuery]
BotShippingQueryUpdateType: TypeAlias = Union[UpdateBotShippingQuery]
MessageReactionUpdateType: TypeAlias = Union[UpdateBotMessageReaction]
MessageReactionCountUpdateType: TypeAlias = Union[UpdateBotMessageReactions,]
ChatBoostUpdateType: TypeAlias = Union[UpdateBotChatBoost]
PurchasedPaidMediaUpdateType: TypeAlias = Union[UpdateBotPurchasedPaidMedia]


async def message_parser(
    client: "pyrogram.Client",
    update: Union[NewMessageType, EditMessageType],
    users: UsersType,
    chats: ChatsType,
):
    is_scheduled = isinstance(update, UpdateNewScheduledMessage)
    business_connection_id = getattr(update, "connection_id", None)

    # noinspection PyProtectedMember
    update = await pyrogram.types.Message._parse(
        client=client,
        message=update.message,
        users=users,
        chats=chats,
        is_scheduled=is_scheduled,
        replies=0 if business_connection_id else 1,
        business_connection_id=business_connection_id,
        raw_reply_to_message=getattr(update, "reply_to_message", None),
    )

    return (
        update,
        MessageHandler,
    )


async def edited_message_parser(
    client: "pyrogram.Client",
    update: EditMessageType,
    users: UsersType,
    chats: ChatsType,
):
    update, _ = await message_parser(
        client=client,
        update=update,
        users=users,
        chats=chats,
    )

    return update, EditedMessageHandler


def deleted_messages_parser(
    client: "pyrogram.Client",
    update: DeleteMessageType,
    users: UsersType,
    chats: ChatsType,
):
    update = parse_deleted_messages(
        client=client, update=update, users=users, chats=chats
    )

    return update, DeletedMessagesHandler


async def callback_query_parser(
    client: "pyrogram.Client", update: CallbackQueryUpdateType, users: UsersType,
    chats: ChatsType,
):
    # noinspection PyProtectedMember
    update = await pyrogram.types.CallbackQuery._parse(
        client=client, callback_query=update, users=users, chats=chats
    )

    return update, CallbackQueryHandler


def user_status_parser(client: "pyrogram.Client", update: UserStatusUpdateType):
    # noinspection PyProtectedMember
    update = pyrogram.types.User._parse_user_status(client=client, user_status=update)

    return update, UserStatusHandler


def inline_query_parser(
    client: "pyrogram.Client", update: InlineQueryUpdateType, users: UsersType
):
    # noinspection PyProtectedMember
    update = pyrogram.types.InlineQuery._parse(client=client, inline_query=update, users=users)

    return update, InlineQueryHandler


def poll_parser(client: "pyrogram.Client", update: PollUpdateType):
    # noinspection PyProtectedMember
    update = pyrogram.types.Poll._parse_update(client=client, update=update)

    return update, PollHandler


def chosen_inline_result_parser(
    client: "pyrogram.Client",
    update: ChosenInlineResultUpdateType,
    users: UsersType,
):
    # noinspection PyProtectedMember
    update = pyrogram.types.ChosenInlineResult._parse(
        client=client,
        chosen_inline_result=update,
        users=users,
    )

    return update, ChosenInlineResultHandler


def chat_member_updated_parser(
    client: "pyrogram.Client",
    update: ChatMemberUpdateType,
    users: UsersType,
    chats: ChatsType,
):
    # noinspection PyProtectedMember
    update = pyrogram.types.ChatMemberUpdated._parse(
        client=client, update=update, users=users, chats=chats
    )

    return update, ChatMemberUpdatedHandler


def chat_join_request_parser(
    client: "pyrogram.Client",
    update: ChatJoinRequestUpdateType,
    users: UsersType,
    chats: ChatsType,
):
    # noinspection PyProtectedMember
    update = pyrogram.types.ChatJoinRequest._parse(
        client=client, update=update, users=users, chats=chats
    )

    return update, ChatJoinRequestHandler


async def story_parser(
    client: "pyrogram.Client",
    update: NewStoryUpdateType,
    users: UsersType,
    chats: ChatsType,
):
    # noinspection PyProtectedMember
    update = await pyrogram.types.Story._parse(
        client=client,
        story=update.story,
        users=users,
        chats=chats,
        peer=update.peer,
    )
    return update, StoryHandler


async def pre_checkout_query_parser(
    client: "pyrogram.Client",
    update: BotPreCheckoutQueryUpdateType,
    users: UsersType
):
    # noinspection PyProtectedMember
    update = await pyrogram.types.PreCheckoutQuery._parse(
        client=client,
        pre_checkout_query=update,
        users=users,
    )
    return update, PreCheckoutQueryHandler


async def shipping_query_parser(
    client: "pyrogram.Client",
    update: BotShippingQueryUpdateType,
    users: UsersType
):
    # noinspection PyProtectedMember
    update = await pyrogram.types.ShippingQuery._parse(client, update, users),
    return update, ShippingQueryHandler


async def message_reaction_parser(
    client: "pyrogram.Client",
    update: MessageReactionUpdateType,
    users: UsersType,
    chats: ChatsType
):
    # noinspection PyProtectedMember
    update = pyrogram.types.MessageReactionUpdated._parse(client, update, users, chats),
    return update, MessageReactionHandler


async def message_reaction_count_parser(
    client: "pyrogram.Client",
    update: MessageReactionCountUpdateType,
    users: UsersType,
    chats: ChatsType
):
    # noinspection PyProtectedMember
    update = pyrogram.types.MessageReactionCountUpdated._parse(client, update, users, chats),
    return update, MessageReactionCountHandler


async def chat_boost_parser(
    client: "pyrogram.Client",
    update: ChatBoostUpdateType,
    users: UsersType,
    chats: ChatsType
):
    # noinspection PyProtectedMember
    update = pyrogram.types.ChatBoostUpdated._parse(client, update, users, chats),
    return (
        update,
        ChatBoostHandler
    )


async def purchased_paid_media_parser(
    client: "pyrogram.Client",
    update: PurchasedPaidMediaUpdateType,
    users: UsersType
):
    # noinspection PyProtectedMember
    update = pyrogram.types.PurchasedPaidMedia._parse(client, update, users),
    return (
        update,
        PurchasedPaidMediaHandler
    )

async def parse_update(
    client: "pyrogram.Client",
    update: TLObject,
    users: UsersType,
    chats: ChatsType,
):
    if isinstance(update, NewMessageType):
        return await message_parser(client, update, users, chats)
    elif isinstance(update, EditMessageType):
        return await edited_message_parser(client, update, users, chats)
    elif isinstance(update, DeleteMessageType):
        return deleted_messages_parser(client, update, users, chats)
    elif isinstance(update, CallbackQueryUpdateType):
        return await callback_query_parser(client, update, users, chats)
    elif isinstance(update, ChatMemberUpdateType):
        return chat_member_updated_parser(client, update, users, chats)
    elif isinstance(update, UserStatusUpdateType):
        return user_status_parser(client, update)
    elif isinstance(update, InlineQueryUpdateType):
        return inline_query_parser(client, update, users)
    elif isinstance(update, PollUpdateType):
        return poll_parser(client, update)
    elif isinstance(update, ChosenInlineResultUpdateType):
        return chosen_inline_result_parser(client, update, users)
    elif isinstance(update, ChatJoinRequestUpdateType):
        return chat_join_request_parser(client, update, users, chats)
    elif isinstance(update, NewStoryUpdateType):
        return await story_parser(client, update, users, chats)
    elif isinstance(update, BotPreCheckoutQueryUpdateType):
        return await pre_checkout_query_parser(client, update, users)
    elif isinstance(update, BotShippingQueryUpdateType):
        return await shipping_query_parser(client, update, users)
    elif isinstance(update, MessageReactionUpdateType):
        return await message_reaction_parser(client, update, users, chats)
    elif isinstance(update, MessageReactionCountUpdateType):
        return await message_reaction_count_parser(client, update, users, chats)
    elif isinstance(update, ChatBoostUpdateType):
        return await chat_boost_parser(client, update, users, chats)
    elif isinstance(update, PurchasedPaidMediaUpdateType):
        return await purchased_paid_media_parser(client, update, users)
    else:
        return None, None
