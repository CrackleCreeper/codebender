from datetime import datetime
import discord


class Message(discord.Embed):
    def __init__(self, title=None, description=None, color=discord.Color.dark_gold(), timestamp=None):
        super().__init__(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now() if timestamp is not None else None
        )



