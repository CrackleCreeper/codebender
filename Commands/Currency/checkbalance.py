from Structures.Message import Message
import discord


# Name the class the same as your command name preferably.
class CheckBalance:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "checkbalance"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Currency"

        # What this command is used for. This description will be later used in the help command.
        self.description = "command to check currency owned"

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        user = client.usersCollection.find_one({"_id": message.author.id})
        await message.channel.send(embed=Message(description=f"Balance: {user['money']}"))

        
