from Structures.Message import Message
import discord
from discord.ui import View, Button
import json
import os

# Load pet data from the file
with open("./Structures/Pets.json", "r") as pet_data:
    pets = json.load(pet_data)

def create_pet_embed(pet, pet_type):
    """Create an embed for a single pet with its image"""
    
    # Set color based on pet type
    color = discord.Color.red() if pet_type == "Fire" else \
           discord.Color.blue() if pet_type == "Water" else \
           discord.Color.green() if pet_type == "Earth" else \
           discord.Color.purple() if pet_type == "Air" else \
           discord.Color.default()
    
    # Create the embed
    embed = discord.Embed(
        title=f"{pet['name']} ({pet['rarity'].capitalize()})",
        description=pet['description'],
        colour=color
    )
    
    # Add pet stats
    embed.add_field(name="Type", value=pet["type"], inline=True)
    embed.add_field(name="HP", value=pet["base_hp"], inline=True)
    embed.add_field(name="Attack", value=pet["attack"], inline=True)
    embed.add_field(name="Defense", value=pet["defense"], inline=True)
    
    # Add moves
    moves_text = ""
    for move in pet["moves"]:
        moves_text += f"**{move['name']}**\n"
    
    embed.add_field(name="Moves", value=moves_text, inline=False)
    
    # Set the image
    # Instead of checking if the file exists (which may fail if paths are relative),
    # directly attach the image and handle any errors during the send process
    image_path = pet["image"]
    # Convert path to standard format if needed
    
    return embed, image_path

class PetNavigationView(View):
    def __init__(self, pet_type, pet_data):
        super().__init__(timeout=180)  # 3 minute timeout
        self.pet_type = pet_type.lower()
        self.pet_data = pet_data
        self.current_index = 0
        self.pets_list = pet_data[self.pet_type]
        
        # Update button states initially
        self._update_buttons()
    
    def _update_buttons(self):
        """Update the state of navigation buttons"""
        # Disable previous button if at the first pet
        self.previous_button.disabled = (self.current_index == 0)
        
        # Disable next button if at the last pet
        self.next_button.disabled = (self.current_index == len(self.pets_list) - 1)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        self.current_index -= 1
        self._update_buttons()
        
        current_pet = self.pets_list[self.current_index]
        embed, image_path = create_pet_embed(current_pet, current_pet["type"])
        
        try:
            file = discord.File(image_path, filename="pet_image.png")
            embed.set_image(url=f"attachment://pet_image.png")
            await interaction.response.edit_message(embed=embed, attachments=[file], view=self)
        except Exception as e:
            # If image can't be loaded, just update the embed without changing the image
            print(f"Error loading image: {e}")
            await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_index += 1
        self._update_buttons()
        
        current_pet = self.pets_list[self.current_index]
        embed, image_path = create_pet_embed(current_pet, current_pet["type"])
        
        try:
            file = discord.File(image_path, filename="pet_image.png")
            embed.set_image(url="attachment://pet_image.png")

            await interaction.response.edit_message(embed=embed, attachments=[file], view=self)
        except Exception as e:
            # If image can't be loaded, just update the embed without changing the image
            print(f"Error loading image: {e}")
            await interaction.response.edit_message(embed=embed, view=self)

class TypeSelectionView(View):
    def __init__(self, pet_data):
        super().__init__(timeout=180)  # 3 minute timeout
        self.pet_data = pet_data

    @discord.ui.button(label="Fire Pets", style=discord.ButtonStyle.danger)
    async def fire_button(self, interaction: discord.Interaction, button: Button):
        await self._show_pet_type(interaction, "Fire")

    @discord.ui.button(label="Water Pets", style=discord.ButtonStyle.primary)
    async def water_button(self, interaction: discord.Interaction, button: Button):
        await self._show_pet_type(interaction, "Water")

    @discord.ui.button(label="Earth Pets", style=discord.ButtonStyle.success)
    async def earth_button(self, interaction: discord.Interaction, button: Button):
        await self._show_pet_type(interaction, "Earth")

    @discord.ui.button(label="Air Pets", style=discord.ButtonStyle.secondary)
    async def air_button(self, interaction: discord.Interaction, button: Button):
        await self._show_pet_type(interaction, "Air")
        
    async def _show_pet_type(self, interaction, pet_type):
        # Get the first pet of the selected type
        current_pet = self.pet_data[pet_type.lower()][0]
        
        # Create the embed and get the image path
        embed, image_path = create_pet_embed(current_pet, pet_type)
        
        # Create the navigation view
        view = PetNavigationView(pet_type, self.pet_data)
        
        # Try to send the response with the image
        try:
            file = discord.File(image_path, filename="pet_image.png")
            embed.set_image(url=f"attachment://pet_image.png")
            await interaction.response.send_message(embed=embed, file=file, view=view)
        except Exception as e:
            # If image can't be loaded, send without the image
            print(f"Error loading image: {e}")
            await interaction.response.send_message(
                content=f"⚠️ Image could not be loaded from path: {image_path}",
                embed=embed, 
                view=view
            )

# Name the class the same as your command name preferably.
class PetDictionary:
    def __init__(self):
        # The command name. In this case this command will run when you type !petdictionary
        self.name = "pets"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Battle"

        # What this command is used for. This description will be later used in the help command.
        self.description = "Browse all pets available in the game, view their stats and abilities"

        # The min number of arguments needed. In this case we need 0.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    async def run(self, message, args, client):
        # Create embed with instructions
        instruction_embed = discord.Embed(
            title="Pet Dictionary",
            description="Select a pet type to browse through the available pets.",
            color=discord.Color.gold()
        )
        
        # Send an initial message with the type selection view
        await message.channel.send(embed=instruction_embed, view=TypeSelectionView(pets))