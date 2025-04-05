from Structures.Message import Message
import discord
from discord.ext import commands

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
            coins = client.users[person]["money"]
            target_guild = args[0].lower()
            
            if coins < 400:
                await message.channel.send(embed=Message(description="You dont have enough money to travel!"))
                return

            client.guilds_dict[target_guild]["visitor_list"].append(person)
            client.users[person]["money"] = coins - 400
            
            role = discord.utils.get(message.guild.roles, name=f"{target_guild}'s visitor")
            if role:
                member = message.guild.get_member(person)
                if member:
                    await member.add_roles(role)
            
            await message.channel.send(embed=Message(description=f"You have travelled to {target_guild}!"))

        except discord.Forbidden:
            await message.channel.send(embed=Message(description="Error: I don't have permission to add roles"))
    