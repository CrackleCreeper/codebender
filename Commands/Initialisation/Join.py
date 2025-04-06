from Structures.Message import Message
from Structures.User import User
import discord


# Name the class the same as your command name preferably.
class Join:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "join"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Initialisation"

        # What this command is used for. This description will be later used in the help command.
        self.description = "Command to induct a new user"

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        user = client.usersCollection.find_one({"_id": message.author.id})
        if user:
            return await message.channel.send(embed=Message(description=f"You are already a member of {user['homeGuild']} Nation'!"))
        newUser = User(message.author.id, client)
        client.usersCollection.insert_one(newUser.to_dict())
        await message.channel.send(embed=Message(title="Welcome",description=f"<@{message.author.id}>, the {newUser.homeGuild} Nation welcomes you! We hope you enjoy your journey with your first companion, your very own {newUser.pets[0]}"))

        role = discord.utils.get(message.guild.roles, name=f"{newUser.homeGuild}")
        if role:
            member = message.guild.get_member(message.author.id)
            if member:
                await member.add_roles(role)

