from Structures.Message import Message
import discord
from discord.ext import commands
from Commands.Map.travel import travel
from datetime import datetime, timedelta
from Structures.battlesystem import battlesystem

class catch:
    def __init__(self):
        self.name = "catch"
        self.category = "Map"
        self.number_args = 1
        self.cooldown = 5 * 60
        self.description = "Command to catch the user when they are sneaking into another guild. Use !catch <user>."
        self.user_permissions = []

    async def run(self, message, args, client):
        person = message.author.id 
        hunter = client.usersCollection.find_one({"_id": person})
        if not message.mentions:
            await message.channel.send(embed=Message(
                description="⚠️ **No Target Mentioned!**\nYou need to mention someone to try and catch them.",
                color=discord.Color.gold()
            ))
            return
        prey = client.usersCollection.find_one({"_id": message.mentions[0].id})
        if not prey:
            await message.channel.send(embed=Message(
                description="❌ **Invalid Target**\nThis person doesn’t seem to be part of our realm yet.\nInvite them to use the bot before trying to catch them! 👤✨",
                color=discord.Color.dark_red()
            ))
            return
        if hunter == prey:
            if prey["is_sneaking"] == True:
                ban_expiry = datetime.utcnow() + timedelta(days=3)
                client.guildsCollection.update_one({"_id" : prey["visitingGuild"]}, {"$set":{f"sneak_bans.{message.mentions[0].id}": ban_expiry}})
                await message.channel.send(embed=Message(
                    description=(
                        "**Self-Report?!**\n"
                        "You just outed *yourself* as a fugitive... bold move. 🔍\n" 
                        "You have been kicked and transferred to your original guild"
                    ),
                    color = discord.Color.orange()
                ))
                if(prey["money"] < 400):
                    client.usersCollection.update_one({"_id": message.mentions[0].id}, {"$set":{"money":400}})
                travel_cmd = travel()
                return await travel_cmd.run(message, [prey["homeGuild"]], client)
            else:
                return await message.channel.send(embed=Message(
                    description=(
                        " **Suspicious Behavior**\n"
                        "You're reporting yourself for... nothing?\n"
                        "Guild people are watching you a little closer now. 👀"
                    ),
                    color= discord.Color.green()
                ))
        if(hunter["homeGuild"] == hunter["visitingGuild"] and hunter["homeGuild"] == prey["visitingGuild"]):
            if prey["homeGuild"] == prey["visitingGuild"]:
                await message.channel.send(embed=Message(
                    description="🔵 **Guild Member Detected!**\nThis person is part of your guild.",
                    color=discord.Color.blue()
                ))
            elif prey["is_sneaking"] == False:
                await message.channel.send(embed=Message(
                    description="🟢 **Legal Entry**\nThis person has travelled into your guild legally.",
                    color=discord.Color.green()
                ))
            else:
                
                await message.channel.send(embed=Message(
                    description=(
                        "🔴 **Fugitive Caught!**\n"
                        "You have caught someone sneaking into your guild!\n\n"
                        "💥 Beat them in a battle to claim a reward, or\n"
                        "💰 Pay their travelling fee to let them go."
                    ),
                    color=discord.Color.red()
                ))
                challenger = client.usersCollection.find_one({"_id": message.author.id})
                opponent = client.usersCollection.find_one({"_id": message.mentions[0].id})
                ba = battlesystem(client,args,message,challenger,opponent)
                winner = await ba.battlestart()
                print(winner)
                if(winner["_id"] == hunter["_id"]):
                    client.usersCollection.update_one({"_id": hunter["_id"]}, {"$inc": {"money": 400}})
                    
                    if prey["money"] < 400:
                        client.usersCollection.update_one({"_id": prey["_id"]}, {"$set":{"money": 0}})
                    else:
                        client.usersCollection.update_one({"_id": prey["_id"]}, {"$inc":{"money": -400}})
                    client.usersCollection.update_one({"_id": prey["_id"]}, {"$set":{"visitingGuild": prey["homeGuild"], "is_sneaking" : False}})
                    ban_expiry = datetime.utcnow() + timedelta(days=3)
                    client.guildsCollection.update_one({"_id": prey["visitingGuild"]},{"$set": {f"sneak_bans.{message.mentions[0].id}": ban_expiry}})
                    member = message.guild.get_member(prey["_id"])
                    await member.remove_roles(discord.utils.get(message.guild.roles, name = prey["visitingGuild"]))
                else:
                    client.usersCollection.update_one({"_id": prey["_id"]}, {"$inc": {"money": 400}})
                    if hunter["money"] < 400:
                        client.usersCollection.update_one({"_id": hunter["_id"]}, {"$set":{"money": 0}})
                    else:
                        client.usersCollection.update_one({"_id": hunter["_id"]}, {"$inc":{"money": -400}})
                    client.usersCollection.update_one({"_id": prey["_id"]}, {"$set": {"is_sneaking": False}})

        else:
            return await message.channel.send(embed=Message(
                        description="🧐 **There's no one to catch!**\nThat member isn't sneaking into your guild, or they're off lurking somewhere else. Keep your eyes peeled!",
                        color=discord.Color.orange()
                    ))
