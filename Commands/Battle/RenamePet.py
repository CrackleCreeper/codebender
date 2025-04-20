from Structures.Message import Message
import discord
import asyncio
import aiohttp
import time


# Name the class the same as your command name preferably.
class RenamePet:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "rename"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Battle"

        # What this command is used for. This description will be later used in the help command.
        self.description = "rename your pet to a name of your choice"

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        userId = message.author.id
        userData = client.usersCollection.find_one({"_id": userId})

        def check(m):
            return m.author.id == message.author.id and m.channel.id == message.channel.id

        # 1) Ask which pet
        try:
            await message.channel.send(embed=Message(description="Which pet do you want to rename?"))
            petChoiceMsg = await client.wait_for('message', check=check, timeout=20.0)
        except asyncio.TimeoutError:
            return await message.channel.send(embed=Message(description="Timeout, try again!"))

        original_name = petChoiceMsg.content
        # find the pet object
        userPets = next(
            (p for p in userData.get("pets", [])
            if p.get("petname", "").lower() == original_name.lower()),
            None
        )

        if userPets is None:
            return await message.channel.send(embed=Message(description="You don't have that pet!"))

        # 2) Ask for new name
        try:
            await message.channel.send(embed=Message(description="What should I rename it to?"))
            petNameMsg = await client.wait_for('message', check=check, timeout=20.0)
        except asyncio.TimeoutError:
            return await message.channel.send(embed=Message(description="Timeout, try again!"))

        new_name = petNameMsg.content

        # 3) Update in MongoDB using the positional operator
        client.usersCollection.update_one(
            { "_id": userId, "pets.petname": original_name },
            { "$set": { "pets.$.petname": new_name } }
        )

        # 4) Confirm
        return await message.channel.send(
            embed=Message(
                description=f"Your pet **{original_name}** has been renamed to **{new_name}**!"
            )
        )
