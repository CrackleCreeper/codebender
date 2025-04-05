from Structures.Message import Message
import discord


# Name the class the same as your command name preferably.
class Joke:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "test"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Testing"

        # What this command is used for. This description will be later used in the help command.
        self.description = "Example command of no use."

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 1

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = ["manage_messages"]

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        await message.channel.send(args[0])
