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

    async def run(self, message, args, client):
        guilds = ["Fire", "Water", "Air", "Earth"]
        person = message.author.id
        target_guild = args[0].lower().capitalize()

        user = client.usersCollection.find_one({"_id": person})
        if not user:
            return await message.channel.send(embed=Message(description="❌ **User not found in database.**"))

        if target_guild not in guilds:
            return await message.channel.send(embed=Message(description="❌ **Invalid guild location.**"))

        coins = user["money"]
        if coins < 400:
            return await message.channel.send(embed=Message(description="💸 **You don't have enough money to travel!**"))

        if user["visitingGuild"] == target_guild:
            return await message.channel.send(embed=Message(description=" **You're already here, traveler.**"))

        # Member and role setup
        member = message.guild.get_member(person)
        old_visiting = user["visitingGuild"]
        home_guild = user["homeGuild"]

        visitor_role = discord.utils.get(message.guild.roles, name=f"Visitor: {old_visiting}")
        visiting_guild_role = discord.utils.get(message.guild.roles, name=old_visiting)
        home_guild_role = discord.utils.get(message.guild.roles, name=home_guild)
        new_visitor_role = discord.utils.get(message.guild.roles, name=f"Visitor: {target_guild}")

        # Remove old visitor role if it exists
        if visitor_role and member:
            await member.remove_roles(visitor_role)

        # Remove old guild role IF it is not the home guild
        if visiting_guild_role and visiting_guild_role != home_guild_role and member:
            await member.remove_roles(visiting_guild_role)

        # Remove from old guild's visitor list
        client.guildsCollection.update_one(
            {"_id": old_visiting},
            {"$pull": {"visitors": person}}
        )

        # Handle travel to home guild
        if target_guild == home_guild:
            client.usersCollection.update_one(
                {"_id": person},
                {"$set": {"money": coins - 400, "visitingGuild": target_guild, "is_sneaking": "false"}}
            )
            return await message.channel.send(embed=Message(description="🏡 **Welcome back home!**"))

        # Travel to new guild
        if member and new_visitor_role:
            await member.add_roles(new_visitor_role)

        client.guildsCollection.update_one(
            {"_id": target_guild},
            {"$push": {"visitors": person}}
        )

        client.usersCollection.update_one(
            {"_id": person},
            {"$set": {"money": coins - 400, "visitingGuild": target_guild, "is_sneaking": "false"}}
        )

        await message.channel.send(embed=Message(
            description=f"🌍 **You have travelled to `{target_guild}` guild! Safe travels, adventurer.**"
        ))
