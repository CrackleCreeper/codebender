from Structures.Message import Message
import discord

class Help:
    def __init__(self):
        self.name = "help"
        self.category = "Initialisation"
        self.description = "Displays every command and description"
        self.number_args = 0
        self.user_permissions = []

    async def run(self, message, args, client):
        all_cmds = client.commands
        cats = {}
        # Group commands by their category
        for cmd in all_cmds.values():
            cats.setdefault(cmd.category, []).append(cmd)
        
        embed = discord.Embed(
            title="📖 Bot Commands",
            description="Type `!help <command>` for more info",
            color=discord.Color.green()
        )
        
        # Add each category as a field in the embed
        for category, cmds in cats.items():
            lines = [f"**!{cmd.name}** - {cmd.description}" for cmd in cmds]
            embed.add_field(
                name=f"{category} [{len(cmds)}]",
                value="\n".join(lines),
                inline=False
            )
        
        await message.channel.send(embed=embed)