from Structures.Message import Message
import discord
from discord.ui import View, Button
import json

# Load pet data from the file
with open("./Structures/Pets.json", "r") as pet_data:
    pets = json.load(pet_data)

def create_shop_embed(type, pet_data):
    embed = discord.Embed(
        title=f"{type} Nation Creatures",
        description=f"Pets found in the {type} Nation.\n",
        colour=discord.Color.red() if type == "Fire" else 
               discord.Color.blue() if type == "Water" else 
               discord.Color.green() if type == "Earth" else 
               discord.Color.purple() if type == "Air" else 
               discord.Color.default()
    )

    for item in pet_data[type.lower()]:
        embed.add_field(
            name=item["name"],
            value=f"Image: {item['image']}\nRarity: {item['rarity']}\nDescription: {item['description']}",
            inline=False
        )

    return embed

class ShopView(View):
    def init(self, type, pet_data):
        super().init(timeout=None)
        self.current_tier = type  # Set the initial tier type (Fire, Water, Earth, Air)
        self.pet_data = pet_data
        self.type = type

    @discord.ui.button(label="Fire", style=discord.ButtonStyle.secondary)
    async def fire_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Fire", self.pet_data), view=self)

    @discord.ui.button(label="Water", style=discord.ButtonStyle.secondary)
    async def water_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Water", self.pet_data), view=self)

    @discord.ui.button(label="Earth", style=discord.ButtonStyle.secondary)
    async def earth_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Earth", self.pet_data), view=self)

    @discord.ui.button(label="Air", style=discord.ButtonStyle.secondary)
    async def air_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Air", self.pet_data), view=self)

# Name the class the same as your command name preferably.
class PetDictionary:

    def init(self):
        # The command name. In this case this command will run when you type !test
        self.name = "petdictionary"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Battle"

        # What this command is used for. This description will be later used in the help command.
        self.description = "Displays name and description of all pets available"

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        # Send an initial message with the Fire pet data and a view for button interaction
        await message.channel.send(embed=create_shop_embed("Fire", pets), view=ShopView("Fire", pets))
