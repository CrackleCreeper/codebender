from Structures.Message import Message
import discord
from discord.ui import View, Button

def create_pet_embed(pet):
        """Create an embed for a single pet with its image"""
        
        # Set color based on pet type
        color = discord.Color.red() if pet["type"] == "Fire" else \
            discord.Color.blue() if pet["type"] == "Water" else \
            discord.Color.green() if pet["type"] == "Earth" else \
            discord.Color.purple() if pet["type"] == "Air" else \
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
        image_path = pet["image"]
        
        return embed, image_path

class PetNavigationView(View):
    def __init__(self, pets_list):
        super().__init__(timeout=180)  # 3 minute timeout
        
        # Store the list of pets and initialize current index
        self.pets_list = pets_list
        self.current_index = 0
        
        # Create buttons
        self.previous_button = Button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
        self.previous_button.callback = self.previous_callback
        
        self.next_button = Button(label="Next", style=discord.ButtonStyle.primary)
        self.next_button.callback = self.next_callback
        
        # Add buttons to view
        self.add_item(self.previous_button)
        self.add_item(self.next_button)
        
        # Update button states initially
        self._update_buttons()
    
    def _update_buttons(self):
        """Update the state of navigation buttons"""
        # Disable previous button if at the first pet
        self.previous_button.disabled = (self.current_index == 0)
        
        # Disable next button if at the last pet
        self.next_button.disabled = (self.current_index == len(self.pets_list) - 1)
    
    async def previous_callback(self, interaction: discord.Interaction):
        self.current_index -= 1
        self._update_buttons()
        
        current_pet = self.pets_list[self.current_index]
        embed, image_path = create_pet_embed(current_pet)
        
        try:
            file = discord.File(image_path, filename="pet_image.png")
            embed.set_image(url=f"attachment://pet_image.png")
            await interaction.response.edit_message(embed=embed, attachments=[file], view=self)
        except Exception as e:
            # If image can't be loaded, just update the embed without changing the image
            print(f"Error loading image: {e}")
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_callback(self, interaction: discord.Interaction):
        self.current_index += 1
        self._update_buttons()
        
        current_pet = self.pets_list[self.current_index]
        embed, image_path = create_pet_embed(current_pet)
        
        try:
            file = discord.File(image_path, filename="pet_image.png")
            embed.set_image(url="attachment://pet_image.png")
            await interaction.response.edit_message(embed=embed, attachments=[file], view=self)
        except Exception as e:
            # If image can't be loaded, just update the embed without changing the image
            print(f"Error loading image: {e}")
            await interaction.response.edit_message(embed=embed, view=self)


# Name the class the same as your command name preferably.
class Inventory:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "inventory"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Battle"

        # What this command is used for. This description will be later used in the help command.
        self.description = "Function to see what pets a user has"

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        userID = message.author.id
        userData = client.usersCollection.find_one({"_id": userID})
        userPets = userData.get("pets", [])

        if not userPets:   
            return await message.channel.send(embed=Message(description="You don't have any pets!"))
        
        # Get the first pet to display initially
        first_pet = userPets[0]
        embed, image_path = create_pet_embed(first_pet)
        
        # Create the pet navigation view
        pet_navigation_view = PetNavigationView(userPets)
        
        # Send the initial message with the pet and navigation view
        try:
            file = discord.File(image_path, filename="pet_image.png")
            embed.set_image(url="attachment://pet_image.png")
            await message.channel.send(embed=embed, file=file, view=pet_navigation_view)
        except Exception as e:
            print(f"Error loading image: {e}")
            await message.channel.send(embed=embed, view=pet_navigation_view)