from Structures.Message import Message
import discord
from discord.ext import commands
from datetime import datetime, timedelta


class sneak:
    def __init__(self):
        self.name = "sneak"
        self.category = "Map"
        self.number_args = 1
        self.description = "Command to sneak into another guild. Use !sneak <guild>. Costs 80 coins."
        self.user_permissions = []

    async def run(self, message, args, client):
        guilds = ["Fire", "Water", "Air", "Earth"]
        person = message.author.id
        target_guild = args[0].lower().capitalize()
        target = client.guildsCollection.find_one({"_id": target_guild})
        user = client.usersCollection.find_one({"_id": person})
        if not user:
            return await message.channel.send(embed=Message(description="❌ **User not found in database.**"))

        if target_guild not in guilds:
            return await message.channel.send(embed=Message(description="❌ **Invalid guild location.**"))

        coins = user["money"]
        if coins < 80:
            return await message.channel.send(embed=Message(description="💸 **You don't have enough money to sneak!**"))

        if str(person) in target.get("sneak_bans", {}):
            ban_expiry = target["sneak_bans"][str(person)]

            if datetime.utcnow() < ban_expiry:
                remaining = ban_expiry - datetime.utcnow()
                return await message.channel.send(embed = Message(description=f"⛔ You are banned from sneaking into this guild for {remaining.days} days and {remaining.seconds//3600} hours."))
        if user["visitingGuild"] == target_guild:
            return await message.channel.send(embed=Message(description=" **You're already in that guild.**"))

        member = message.guild.get_member(person)
        old_visiting = user["visitingGuild"]
        home_guild = user["homeGuild"]

        # Roles
        visitor_role = discord.utils.get(message.guild.roles, name=f"Visitor: {old_visiting}")
        visiting_guild_role = discord.utils.get(message.guild.roles, name=old_visiting)
        home_guild_role = discord.utils.get(message.guild.roles, name=home_guild)
        new_guild_role = discord.utils.get(message.guild.roles, name=target_guild)

        # Remove visitor role
        if visitor_role and member:
            await member.remove_roles(visitor_role)

        # Remove guild role if not home guild
        if visiting_guild_role and visiting_guild_role != home_guild_role and member:
            await member.remove_roles(visiting_guild_role)

        # Update old guild's visitor list
        client.guildsCollection.update_one(
            {"_id": old_visiting},
            {"$pull": {"visitors": person}}
        )

        # Travel back home
        if target_guild == home_guild:
            client.usersCollection.update_one(
                {"_id": person},
                {"$set": {"money": coins - 80, "visitingGuild": target_guild, "is_sneaking": "false"}}
            )
            return await message.channel.send(embed=Message(
                description="🏠 **You quietly returned to your home guild.**",
                color=discord.Color.green()
            ))

        # Sneaking into another guild
        if new_guild_role and member:
            await member.add_roles(new_guild_role)

        client.usersCollection.update_one(
            {"_id": person},
            {"$set": {"money": coins - 80, "visitingGuild": target_guild, "is_sneaking": "true"}}
        )

        await message.channel.send(embed=Message(
            description=f"🕵️ **You have successfully sneaked into `{target_guild}` guild.**\nStay low, stay sneaky.",
            color=discord.Color.dark_purple()
        ))
