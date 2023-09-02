#    This file is part of the ForveSub distribution (https://github.com/xditya/ForceSub).
#    Copyright (c) 2021 Adiya
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
#    License can be found in < https://github.com/xditya/ForceSub/blob/main/License> .

import logging
from telethon.utils import get_display_name
import re
from telethon import TelegramClient, events, Button
from decouple import config
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.INFO
)
log = logging.getLogger("BotzHub")

# start the bot
log.info("Starting...")
try:
    bottoken = config("BOT_TOKEN")
    xchannel = config("CHANNEL")
    welcome_msg = config("WELCOME_MSG")
    welcome_not_joined = config("WELCOME_NOT_JOINED")
    on_join = config("ON_JOIN", cast=bool)
    on_new_msg = config("ON_NEW_MSG", cast=bool)
except Exception as e:
    log.error(e)
    log.info("Bot is quiting...")
    exit()

try:
    BotzHub = TelegramClient("BotzHub", 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e").start(
        bot_token=bottoken
    )
except Exception as e:
    log.error(f"ERROR!\n{str(e)}")
    log.error("Bot is quiting...")
    exit()

channel = xchannel.replace("@", "")
bot_self = BotzHub.loop.run_until_complete(BotzHub.get_me())


# join check
async def get_user_join(id):
    ok = True
    try:
        await BotzHub(GetParticipantRequest(channel=channel, participant=id))
        ok = True
    except UserNotParticipantError:
        ok = False
    return ok


@BotzHub.on(events.ChatAction)
async def _(event):
    if on_join is False:
        return
    if not event.is_group:
        return
    if event.action_message:
        return
    if event.user_joined or event.user_added:
        user = await event.get_user()
        chat = await event.get_chat()
        title = chat.title or "this chat"
        pp = await BotzHub.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        fullname = f"{name} {last}" if last else name
        username = f"@{uu}" if (uu := user.username) else mention
        x = await get_user_join(user.id)
        if x is True:
            msg = welcome_msg.format(
                mention=mention,
                title=title,
                fullname=fullname,
                username=username,
                name=name,
                last=last,
                channel=f"@{channel}",
                count=count,
            )
            butt = [Button.url("Channel", url=f"https://t.me/{channel}")]
        else:
            msg = welcome_not_joined.format(
                mention=mention,
                title=title,
                fullname=fullname,
                username=username,
                name=name,
                last=last,
                channel=f"@{channel}",
                count=count,
            )
            butt = [
                Button.url("Channel", url=f"https://t.me/{channel}"),
                Button.inline("UnMute Me", data=f"unmute_{user.id}"),
            ]
            await BotzHub.edit_permissions(
                event.chat.id, user.id, until_date=None, send_messages=False
            )

        await event.reply(msg, buttons=butt)


@BotzHub.on(events.NewMessage(incoming=True))
async def mute_on_msg(event):
    if event.is_private:
        return
    if on_new_msg is False:
        return
    x = await get_user_join(event.sender_id)
    temp = await BotzHub.get_entity(event.sender_id)
    if x is False:
        if temp.bot:
            return
        nm = temp.first_name
        try:
            await BotzHub.edit_permissions(
                event.chat.id, event.sender_id, until_date=None, send_messages=False
            )
        except Exception as e:
            log.error(e)
            return
        user = await event.get_sender()
        chat = await event.get_chat()
        title = chat.title or "this chat"
        pp = await BotzHub.get_participants(chat)
        count = len(pp)
        mention = f"[{get_display_name(user)}](tg://user?id={user.id})"
        name = user.first_name
        last = user.last_name
        fullname = f"{name} {last}" if last else name
        username = f"@{uu}" if (uu := user.username) else mention
        reply_msg = welcome_not_joined.format(
            mention=mention,
            title=title,
            fullname=fullname,
            username=username,
            name=name,
            last=last,
            channel=f"@{channel}",
            count=count,
        )
        butt = [
            Button.url("Channel", url=f"https://t.me/{channel}"),
            Button.inline("UnMute Me", data=f"unmute_{event.sender_id}"),
        ]
        await event.reply(reply_msg, buttons=butt)


@BotzHub.on(events.callbackquery.CallbackQuery(data=re.compile(b"unmute_(.*)")))
async def _(event):
    uid = int(event.data_match.group(1).decode("UTF-8"))
    if uid == event.sender_id:
        x = await get_user_join(uid)
        nm = event.sender.first_name
        if x is False:
            await event.answer(
                f"You haven't joined @{channel} yet!", cache_time=0, alert=True
            )
        elif x is True:
            try:
                await BotzHub.edit_permissions(
                    event.chat.id, uid, until_date=None, send_messages=True
                )
            except Exception as e:
                log.error(e)
                return
            msg = f"Welcome to {(await event.get_chat()).title}, {nm}!\nGood to see you here!"
            butt = [Button.url("Channel", url=f"https://t.me/{channel}")]
            await event.edit(msg, buttons=butt)
    else:
        await event.answer(
            "You are an old member and can speak freely! This isn't for you!",
            cache_time=0,
            alert=True,
        )


@BotzHub.on(events.NewMessage(pattern="^/start$"))
async def strt(event):
    await event.reply(
        f"Hi. I'm a force subscribe bot made specially for @{channel}!\n\nCheckout @BotzHub :)",
        buttons=[
            Button.url("Channel", url=f"https://t.me/{channel}"),
            Button.url("Repository", url="https://github.com/xditya/ForceSub"),
        ],
    )


log.info("ForceSub Bot has started as @%s.\nDo visit @BotzHub!", bot_self.username)
BotzHub.run_until_disconnected()
