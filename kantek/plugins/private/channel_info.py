"""Plugin to get information about a channel."""
import logging
from typing import Dict, List

from telethon import events
from telethon.events import NewMessage
from telethon.tl.types import Channel, User

from config import cmd_prefix
from utils import helpers
from utils.client import KantekClient
from utils.mdtex import Bold, Code, Item, KeyValueItem, MDTeXDocument, Section

__version__ = '0.1.0'

tlog = logging.getLogger('kantek-channel-log')


@events.register(events.NewMessage(outgoing=True, pattern=f'{cmd_prefix}info'))
async def info(event: NewMessage.Event) -> None:
    """Show information about a group or channel.

    Args:
        event: The event of the command

    Returns: None

    """
    client: KantekClient = event.client
    keyword_args, args = await helpers.get_args(event)
    if args:
        chat: Channel = await client.get_entity(args[0])
    else:
        chat: Channel = await event.get_chat()
    if event.is_private:
        return
    chat_info = Section(f'info for {chat.title}:',
                        KeyValueItem(Bold('title'), Code(chat.title)),
                        KeyValueItem(Bold('chat_id'), Code(chat.id)),
                        KeyValueItem(Bold('access_hash'), Code(chat.access_hash)),
                        KeyValueItem(Bold('creator'), Code(chat.creator)),
                        KeyValueItem(Bold('broadcast'), Code(chat.broadcast)),
                        KeyValueItem(Bold('megagroup'), Code(chat.megagroup)),
                        KeyValueItem(Bold('min'), Code(chat.min)),
                        KeyValueItem(Bold('username'), Code(chat.username)),
                        KeyValueItem(Bold('verified'), Code(chat.verified)),
                        KeyValueItem(Bold('version'), Code(chat.version)),
                        )

    bot_accounts = 0
    total_users = 0
    deleted_accounts = 0
    user: User
    async for user in client.iter_participants(chat):
        total_users += 1
        if user.bot:
            bot_accounts += 1
        if user.deleted:
            deleted_accounts += 1

    user_stats = Section('user stats:',
                         KeyValueItem(Bold('total_users'), Code(total_users)),
                         KeyValueItem(Bold('bots'), Code(bot_accounts)),
                         KeyValueItem(Bold('deleted_accounts'), Code(deleted_accounts)))

    chat_document = client.db.groups.get_chat(event.chat_id)
    db_named_tags: Dict = chat_document['named_tags'].getStore()
    db_tags: List = chat_document['tags']
    data = []
    data += [KeyValueItem(Bold(key), value) for key, value in db_named_tags.items()]
    data += [Item(_tag) for _tag in db_tags]
    tags = Section('tags:', *data)
    info_msg = MDTeXDocument(chat_info, user_stats, tags)
    await client.respond(event, info_msg)
