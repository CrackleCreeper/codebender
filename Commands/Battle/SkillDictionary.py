from Structures.Message import Message
import discord
from discord.ui import View, Button
import json

# Load skill data from the file
with open("./Structures/Skills.json", "r") as skill_data:
    skills = json.load(skill_data)

def create_skill_embed(skill, element):
    """Create an embed for a single skill"""
    
    # Set color based on element
    color = discord.Color.red() if element == "fire" else \
           discord.Color.blue() if element == "water" else \
           discord.Color.green() if element == "earth" else \
           discord.Color.purple() if element == "air" else \
           discord.Color.default()
    
    # Create the embed
    embed = discord.Embed(
        title=skill['name'],
        description=skill['description'],
        colour=color
    )
    
    # Add skill metadata
    embed.add_field(name="Type", value=skill['skilltype'], inline=True)
    embed.add_field(name="Attack Type", value=skill['atktype'], inline=True)
    embed.add_field(name="Power", value=skill['power'], inline=True)
    
    # Add effects
    effects = []
    if skill['defreduction'] > 0:
        effects.append(f"**Defense Reduction**: {skill['defreduction']}")
    if skill['defbuff'] > 0:
        effects.append(f"**Defense Buff**: +{skill['defbuff']}")
    if skill['atkbuff'] > 0:
        effects.append(f"**Attack Buff**: +{skill['atkbuff']}")
    if skill['atkreduction'] > 0:
        effects.append(f"**Attack Reduction**: {skill['atkreduction']}")
    if skill['heal'] > 0:
        effects.append(f"**Heal**: {skill['heal']} HP")
    if skill['dodge']:
        effects.append("**Dodge**: Yes")
    if skill['skipNextTurn']:
        effects.append("**Skip Next Turn**: Yes")
    if skill['numInstances'] > 1:
        effects.append(f"**Hits**: {skill['numInstances']} times")
    
    embed.add_field(name="Effects", value="\n".join(effects) if effects else "None", inline=False)
    
    return embed

class SkillNavigationView(View):
    def __init__(self, element, skill_data):
        super().__init__(timeout=180)
        self.element = element
        self.skill_data = skill_data
        self.current_index = 0
        self.skills_list = skill_data[self.element]
        
        self._update_buttons()
    
    def _update_buttons(self):
        self.previous_button.disabled = (self.current_index == 0)
        self.next_button.disabled = (self.current_index == len(self.skills_list) - 1)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        self.current_index -= 1
        self._update_buttons()
        current_skill = self.skills_list[self.current_index]
        embed = create_skill_embed(current_skill, self.element)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        self.current_index += 1
        self._update_buttons()
        current_skill = self.skills_list[self.current_index]
        embed = create_skill_embed(current_skill, self.element)
        await interaction.response.edit_message(embed=embed, view=self)

class ElementSelectionView(View):
    def __init__(self, skill_data):
        super().__init__(timeout=180)
        self.skill_data = skill_data

    @discord.ui.button(label="Fire Skills", style=discord.ButtonStyle.danger)
    async def fire_button(self, interaction: discord.Interaction, button: Button):
        await self._show_element_skills(interaction, "fire")

    @discord.ui.button(label="Water Skills", style=discord.ButtonStyle.primary)
    async def water_button(self, interaction: discord.Interaction, button: Button):
        await self._show_element_skills(interaction, "water")

    @discord.ui.button(label="Earth Skills", style=discord.ButtonStyle.success)
    async def earth_button(self, interaction: discord.Interaction, button: Button):
        await self._show_element_skills(interaction, "earth")

    @discord.ui.button(label="Air Skills", style=discord.ButtonStyle.secondary)
    async def air_button(self, interaction: discord.Interaction, button: Button):
        await self._show_element_skills(interaction, "air")
        
    async def _show_element_skills(self, interaction, element):
        current_skill = self.skill_data[element][0]
        embed = create_skill_embed(current_skill, element)
        view = SkillNavigationView(element, self.skill_data)
        await interaction.response.send_message(embed=embed, view=view)

class SkillDictionary:
    def __init__(self):
        self.name = "skills"
        self.category = "Battle"
        self.description = "Browse all skills available in the game, view their stats and effects"
        self.number_args = 0
        self.user_permissions = []

    async def run(self, message, args, client):
        instruction_embed = discord.Embed(
            title="Skill Dictionary",
            description="Select an element to browse its skills.",
            color=discord.Color.gold()
        )
        await message.channel.send(embed=instruction_embed, view=ElementSelectionView(skills))