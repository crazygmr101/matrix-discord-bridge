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
from typing import TYPE_CHECKING

import hikari
import nio

if TYPE_CHECKING:
    from main import Master


class MatrixApp:
    def __init__(self, master: Master):
        self._master = master
        self._creds = tuple(os.getenv("MATRIX_CREDS").split(";"))
        self._room_id = os.getenv("MATRIX_ROOM")
        self._client = nio.AsyncClient("http://matrix.org", self._creds[0])

    async def run(self):
        self._client.add_event_callback(self._message_callback, nio.RoomMessageText)
        print(await self._client.login(self._creds[1]))
        await self._client.sync_forever(timeout=30000)

    async def _message_callback(self, room: nio.MatrixRoom, event: nio.RoomMessageText) -> None:
        if room.room_id != self._room_id:
            return
        if room.own_user_id == event.sender:
            return
        await self._master.discord.forward(room, event)

    async def forward(self, event: hikari.MessageCreateEvent):
        await self._client.room_send(
            room_id=self._room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": f"{event.author.username}#{event.author.discriminator} - {event.content}",
                "format": "org.matrix.custom.html",
                "formatted_body": f"<b>{event.author.username}#{event.author.discriminator}</b> - {event.content}",
            }
        )
