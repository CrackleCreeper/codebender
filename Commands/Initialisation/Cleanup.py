from Structures.Message import Message
import discord


# Name the class the same as your command name preferably.
class Cleanup:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "cleanup"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Initialisation"

        # What this command is used for. This description will be later used in the help command.
        self.description = "Command to remove all roles and channels the bot created, before kicking the bot."

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = ["manage_channels", "manage_roles"]

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        # Delete roles
        role_names = [
            "Visitor: Water", "Visitor: Fire", "Visitor: Earth", "Visitor: Air",
            "Water", "Fire", "Earth", "Air"
        ]
        for role in message.guild.roles:
            if role.name in role_names:
                try:
                    await role.delete()
                    print(f"Deleted role: {role.name}")
                except Exception as e:
                    print(f"Failed to delete role {role.name}: {e}")

        # Delete categories and their channels
        category_names = [
            "Water Nation", "Fire Nation", "Earth Nation", "Air Nation", "No Man's Land"
        ]
        for category in message.guild.categories:
            if category.name in category_names:
                # Delete channels inside the category first
                for channel in category.channels:
                    try:
                        await channel.delete()
                        print(f"Deleted channel: {channel.name}")
                    except Exception as e:
                        print(f"Failed to delete channel {channel.name}: {e}")
                try:
                    await category.delete()
                    print(f"Deleted category: {category.name}")
                except Exception as e:
                    print(f"Failed to delete category {category.name}: {e}")

