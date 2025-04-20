from Structures.Message import Message
import discord
import asyncio

class SetupTradePost:
    def __init__(self):
        self.name = "setuptradepost"
        self.description = "Setup a trade post channel for your server"
        self.number_args = 0
        self.category = "Admin"
        self.user_permissions = ["administrator"]
    
    async def run(self, message, args, client):
        # Check if user has admin permissions
        if not message.author.guild_permissions.administrator:
            return await message.channel.send(embed=Message(description="You need administrator permissions to use this command."))
        
        # Find the no-mans-forest channel
        trade_channel = discord.utils.get(message.guild.channels, name="no-mans-forest")
        if not trade_channel:
            return await message.channel.send(embed=Message(description="Could not find the no-mans-forest channel. Please make sure it exists."))
        
        # Create confirmation embed
        embed = discord.Embed(
            title="🏪 Setup Trade Post Channel",
            description="This will set up the trade post in the #no-mans-forest channel. Continue?",
            color=discord.Color.blue()
        )
        
        # Create confirmation buttons
        class ConfirmView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None
            
            @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
            async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.value = True
                self.stop()
                await interaction.response.defer()
            
            @discord.ui.button(label="No", style=discord.ButtonStyle.red)
            async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                self.value = False
                self.stop()
                await interaction.response.defer()
        
        view = ConfirmView()
        confirm_msg = await message.channel.send(embed=embed, view=view)
        
        # Wait for confirmation
        await view.wait()
        
        if view.value is None:
            await confirm_msg.edit(embed=Message(description="Setup timed out."), view=None)
            return
        
        if not view.value:
            await confirm_msg.edit(embed=Message(description="Setup cancelled."), view=None)
            return
        
        # Set up the channel
        try:
            # Set up permissions for trade post functionality
            overwrites = trade_channel.overwrites
            overwrites[message.guild.default_role] = discord.PermissionOverwrite(
                send_messages=True,
                add_reactions=True,
                read_messages=True
            )
            overwrites[message.guild.me] = discord.PermissionOverwrite(
                send_messages=True,
                embed_links=True,
                attach_files=True,
                add_reactions=True,
                manage_messages=True
            )
            
            # Update channel topic if it doesn't already mention trading
            if not trade_channel.topic or "trade" not in trade_channel.topic.lower():
                new_topic = f"{trade_channel.topic or ''} | Buy and sell pets with custom skills! Use !tradepost to browse or list pets."
                await trade_channel.edit(topic=new_topic, overwrites=overwrites)
            else:
                await trade_channel.edit(overwrites=overwrites)
            
            # Set up the welcome message
            await self.setup_welcome_message(trade_channel)
            
            # Confirm to user
            success_embed = discord.Embed(
                title="✅ Trade Post Setup Complete!",
                description=f"Trade post has been set up in {trade_channel.mention}\n\nUsers can now use `!tradepost` commands to buy and sell pets.",
                color=discord.Color.green()
            )
            
            await confirm_msg.edit(embed=success_embed, view=None)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Setup Failed",
                description=f"Failed to set up trade post: {str(e)}",
                color=discord.Color.red()
            )
            
            await confirm_msg.edit(embed=error_embed, view=None)
    
    # New method for programmatic setup in an existing channel
    async def setup_in_channel(self, channel):
        try:
            # Check if this channel already has trade post setup
            async for message in channel.history(limit=100):
                if message.author == channel.guild.me and message.embeds:
                    for embed in message.embeds:
                        if embed.title and "Welcome to the Pet Trade Post!" in embed.title:
                            print(f"Trade post already set up in {channel.name}")
                            return
            
            # Set up permissions for trade post functionality
            overwrites = channel.overwrites
            overwrites[channel.guild.default_role] = discord.PermissionOverwrite(
                send_messages=True,
                add_reactions=True,
                read_messages=True
            )
            overwrites[channel.guild.me] = discord.PermissionOverwrite(
                send_messages=True,
                embed_links=True,
                attach_files=True,
                add_reactions=True,
                manage_messages=True
            )
            
            # Update channel topic if it doesn't already mention trading
            if not channel.topic or "trade" not in channel.topic.lower():
                new_topic = f"{channel.topic or ''} | Buy and sell pets with custom skills! Use !tradepost to browse or list pets."
                await channel.edit(topic=new_topic, overwrites=overwrites)
            else:
                await channel.edit(overwrites=overwrites)
            
            # Send welcome message
            await self.setup_welcome_message(channel)
            
            print(f"Successfully set up trade post in {channel.name}")
            
        except Exception as e:
            print(f"Failed to set up trade post in {channel.name}: {str(e)}")
    
    # Helper method to set up welcome message
    async def setup_welcome_message(self, channel):
        welcome_embed = discord.Embed(
            title="🏪 Welcome to the Pet Trade Post!",
            description="This channel is dedicated to buying and selling pets with custom skills.",
            color=discord.Color.blue()
        )
        
        welcome_embed.add_field(
            name="How to Use",
            value="• `!tradepost` - Browse all active listings\n"
                  "• `!tradepost sell` - Create a new listing\n"
                  "• `!tradepost my` - View your active listings\n"
                  "• `!tradepost buy <id>` - Purchase a pet\n"
                  "• `!tradepost info <id>` - View listing details\n"
                  "• `!tradepost help` - See all commands",
            inline=False
        )
        
        welcome_embed.add_field(
            name="Trading Tips",
            value="• Pets with rare skills are more valuable\n"
                  "• Higher level pets command higher prices\n"
                  "• Legendary pets with custom skills are the most valuable\n"
                  "• Set fair prices to attract buyers",
            inline=False
        )
        
        welcome_embed.set_footer(text="New listings will appear in this channel automatically")
        
        await channel.send(embed=welcome_embed)