from Structures.Message import Message
import discord
from discord.ui import View, Button
from Structures.battlesystem import battlesystem
class battle:

    def __init__(self):
        self.name = "battle"
        self.category = "Battle"
        self.description = "command to check currency owned"
        self.number_args = 1
        self.cooldown = 30
        self.user_permissions = []

    async def run(self, message, args, client):
        challenger = client.usersCollection.find_one({"_id": message.author.id})
        if len(args) == 1:
            args.append(0)
        if not message.mentions:
            await message.channel.send(embed=Message(
                description="⚠️ **No Target Mentioned!**\nYou need to mention someone to try and catch them.",
                color=discord.Color.gold()
            ))
            return
        opponent = client.usersCollection.find_one({"_id": message.mentions[0].id})
        if not opponent:
            await message.channel.send(embed=Message(
                description="❌ **Invalid Target**\nThis person doesn’t seem to be part of our realm yet.\nInvite them to use the bot before trying to catch them! 👤✨",
                color=discord.Color.dark_red()
            ))
            return
        if opponent == challenger:
            return await message.channel.send(embed=Message(description="why do you want to battle urself",color=discord.Color.dark_red()))
        if (opponent["money"] < int(args[1]) or  challenger["money"]< int(args[1])):
            return await message.channel.send(embed=Message(description="One or more players don’t have enough coins to cover their bet.",color=discord.Color.dark_red()))
        if(opponent["visitingGuild"] != challenger["visitingGuild"]):
            return await message.channel.send(embed=Message(description="You need to be in the same guild to battle!",color=discord.Color.dark_red()))
        
        ba = battlesystem(client,args,message,opponent,challenger)
        winner = await ba.battlestart()
        if(winner == challenger):
            client.usersCollection.update_one({"_id": challenger["_id"]}, {"$inc": {"money": int(args[1])}})
            client.usersCollection.update_one({"_id": opponent["_id"]}, {"$inc":{"money": -int(args[1])}})
        else:
            client.usersCollection.update_one({"_id": opponent["_id"]}, {"$inc": {"money": int(args[1])}})
            client.usersCollection.update_one({"_id": challenger["_id"]}, {"$inc":{"money": -int(args[1])}})