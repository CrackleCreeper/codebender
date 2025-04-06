from Structures.Message import Message
import discord
from discord.ext import commands
from pymongo import MongoClient


class travel:
    def __init__(self):
        self.name = "travel"
        self.category = "Map"
        self.number_args = 1
        self.description = "travel command"
        self.user_permissions = []

    async def run(self, message,args,client):
        try:
            person = message.author.id 
            user = client.usersCollection.find_one({"_id" : person})
            coins = user["money"]
            target_guild = args[0].lower().capitalize()
            
            if coins < 400:
                await message.channel.send(embed=Message(description="You dont have enough money to travel!"))
                return
            if(user["visitingGuild"] == None):
                pass
            elif(user["visitingGuild"] == target_guild):
                await message.channel.send(embed=Message(description=f"You are already here dumbfuck"))
                return
            elif(target_guild == user["homeGuild"]):
                member = message.guild.get_member(person)
                await member.remove_roles(discord.utils.get(message.guild.roles, name=f"Visitor: {user["visitingGuild"]}"))
                client.guildsCollection.update_one({"_id": user["visitingGuild"]}, {"$pull":{"visitors" : person}})
                client.usersCollection.update_one({"_id" : person},{"$set" :{"money" : coins - 400, "visitingGuild": target_guild}})
                await message.channel.send(embed=Message(description=f"Welcome back home!"))
                return
            else:
                client.guildsCollection.update_one({"_id": user["visitingGuild"]}, {"$pull":{"visitors" : person}})
                member = message.guild.get_member(person)
                await member.remove_roles(discord.utils.get(message.guild.roles, name=f"Visitor: {user["visitingGuild"]}"))
            client.guildsCollection.update_one({"_id": target_guild}, {"$push":{"visitors" : person}})
            client.usersCollection.update_one({"_id" : person},{"$set" :{"money" : coins - 400, "visitingGuild": target_guild}})
            
            role = discord.utils.get(message.guild.roles, name=f"Visitor: {target_guild}")
            if role:
                member = message.guild.get_member(person)
                if member:
                    await member.add_roles(role)
            
            await message.channel.send(embed=Message(description=f"You have travelled to {target_guild}!"))

        except discord.Forbidden:
            await message.channel.send(embed=Message(description="Error: I don't have permission to add roles"))
    