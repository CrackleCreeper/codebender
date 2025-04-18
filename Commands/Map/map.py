from Structures.Message import Message
import discord
from discord.ext import commands
from Commands.Map.travel import travel
from PICTURES import *
class map:
    def __init__(self):
        self.name = "map"
        self.category = "Map"
        self.number_args = 0
        self.description = "map command"
        self.user_permissions = []

    async def run(self, message, args, client):
        person = message.author.id 
        user = client.usersCollection.find_one({"_id": person})
        if user["visitingGuild"] == "Fire":
            with open('./PICTURES/fire.jpg', 'rb') as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)
        if user["visitingGuild"] == "Water":
            with open('./PICTURES/water.jpg', 'rb') as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)
        if user["visitingGuild"] == "Air":
            with open('./PICTURES/air.jpg', 'rb') as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)
        if user["visitingGuild"] == "Earth":
            with open('./PICTURES/earth.jpg', 'rb') as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)
