"""
Copyright 2021 crazygmr101

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

import hikari
import nio

if TYPE_CHECKING:
    from main import Master


class DiscordApp:
    def __init__(self, master: Master):
        self._master = master
        self._token = os.getenv("DISCORD_TOKEN")
        self._bot = hikari.GatewayBot(token=self._token)
        self._channel_id = os.getenv("DISCORD_CHANNEL")
        self._bot.event_manager.subscribe(hikari.MessageCreateEvent, self._message_callback)
        self._hook_url = os.getenv("DISCORD_HOOK")
        self._hook: Optional[hikari.PartialWebhook] = None

    async def run(self):
        self._bot.run()

    async def _message_callback(self, event: hikari.MessageCreateEvent):
        if event.author.id == self._bot.get_me().id or \
                event.author.discriminator == "0000" or int(event.channel_id) != int(self._channel_id):
            return
        await self._master.matrix.forward(event)

    async def forward(self, room: nio.MatrixRoom, event: nio.RoomMessageText):
        # noinspection PyTypeChecker
        channel: hikari.TextableGuildChannel = self._bot.cache.get_guild_channel(self._channel_id)
        guild: hikari.Guild = self._bot.cache.get_guild(channel.id)
        self._hook: hikari.IncomingWebhook = self._hook or (await self._bot.rest.fetch_channel_webhooks(channel))[0]
        await self._hook.execute(
            username=event.sender,
            content=event.body,
            role_mentions=None,
            user_mentions=None,
            mentions_everyone=None
        )
