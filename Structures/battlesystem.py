from Structures.Message import Message
import discord
from discord.ui import View, Button
import asyncio
from PIL import Image, ImageDraw, ImageFont

class battlesystem:
    def __init__(self, client, args, message, opponent, challenger):
        self.client = client
        self.args = args
        self.message = message
        self.opponent = opponent
        self.challenger = challenger
        self.battlestate = {}
        self.output_path=f"PICTURES/battle_preview{self.challenger["_id"]}.png"



    async def battlestart(self):
        pets1 = self.challenger.get("pets", [])
        pets2 = self.opponent.get("pets", [])

        # Get members for challenger and opponent to mention them properly
        challenger_member = self.message.guild.get_member(self.challenger['_id'])
        opponent_member = self.message.guild.get_member(self.opponent['_id'])

        embed1 = discord.Embed(title=f"{challenger_member.display_name}'s pets", color=discord.Color.green())
        for i, pet in enumerate(pets1, start=1):
            embed1.add_field(name=f"{i}. {pet['name']}", value=pet["rarity"], inline=True)

        embed2 = discord.Embed(title=f"{opponent_member.display_name}'s pets", color=discord.Color.blue())
        for i, pet in enumerate(pets2, start=1):
            embed2.add_field(name=f"{i}. {pet['name']}", value=pet["rarity"], inline=True)

        challenger_choice = None
        opponent_choice = None
        selection_event = asyncio.Event()

        # Create two separate views for challenger and opponent
        challenger_view = View(timeout=60)
        opponent_view = View(timeout=60)

        async def check_done(interaction):
            if challenger_choice and opponent_choice:
                selection_event.set()
                await interaction.message.edit(view=None)
                await self.message.channel.send(
                    f"⚔️ Both players have selected!\n"
                    f"**{challenger_member.mention}** chose: `{challenger_choice[1]}`\n"
                    f"**{opponent_member.mention}** chose: `{opponent_choice[1]}`"
                )
                pet1 = pets1[challenger_choice[0]-1]
                pet2 = pets2[opponent_choice[0]-1]
                self.battlestate = {
                "hp":{
                    "user" : pet1["base_hp"],
                    "opponent" : pet2["base_hp"]
                },
                "buffs" : {},
                "status_effects" : {},
                "used_abilities" : set(),
                "ongoing_effects": {
                    "user": [],
                    "opponent": []
                }
                }
                await self.battling(pet1,pet2,self.message,self.client)

        # Challenger's buttons
        for i, pet in enumerate(pets1, start=1):
            async def make_callback(interaction, index=i, pet_name=pet["name"]):
                nonlocal challenger_choice
                if interaction.user.id != self.challenger["_id"]:
                    return await interaction.response.send_message("⛔ Not your pet to select.", ephemeral=True)
                if not challenger_choice:
                    challenger_choice = (index, pet_name)
                    await interaction.response.send_message(f"✅ You selected pet #{index}: **{pet_name}**", ephemeral=True)
                    await check_done(interaction)
            btn = Button(label=f"{i}", style=discord.ButtonStyle.green, custom_id=f"challenger_{i}")
            btn.callback = make_callback
            challenger_view.add_item(btn)

        # Opponent's buttons
        for i, pet in enumerate(pets2, start=1):
            async def make_callback(interaction, index=i, pet_name=pet["name"]):
                nonlocal opponent_choice
                if interaction.user.id != self.opponent["_id"]:
                    return await interaction.response.send_message("⛔ Not your pet to select.", ephemeral=True)
                if not opponent_choice:
                    opponent_choice = (index, pet_name)
                    await interaction.response.send_message(f"✅ You selected pet #{index}: **{pet_name}**", ephemeral=True)
                    await check_done(interaction)
            btn = Button(label=f"{i}", style=discord.ButtonStyle.blurple, custom_id=f"opponent_{i}")
            btn.callback = make_callback
            opponent_view.add_item(btn)

        # Send messages with different views for each player
        msg1 = await self.message.channel.send(embed=embed1, view=challenger_view)
        msg2 = await self.message.channel.send(embed=embed2, view=opponent_view)

        try:
            await asyncio.wait_for(selection_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            if not selection_event.is_set():
                await msg1.edit(view=None)
                await msg2.edit(view=None)
                await self.message.channel.send("⏰ Battle cancelled — one or both players didn’t pick in time.")

    async def prompt_move_selection(self, user_id, pet, message):
        view = View(timeout=60)
        move_choice = {"value": None}
        event = asyncio.Event()

        for index, move in enumerate(pet["moves"], start=1):
            btn = Button(label=f"{index}. {move['name']}", style=discord.ButtonStyle.primary)

            async def callback(interaction, move_name=move['name']):
                if interaction.user.id != user_id:
                    await interaction.response.send_message("❌ You can't choose this move.", ephemeral=True)
                    return
                if move_choice["value"] is None:
                    move_choice["value"] = move_name
                    await interaction.response.send_message(f"✅ You selected **{move_name}**!", ephemeral=True)
                    event.set()

            btn.callback = callback
            view.add_item(btn)

        # Send the ephemeral message to the correct user
        user = message.guild.get_member(user_id)
        await user.send(f"⚔️ Choose a move for **{pet['name']}**:", view=view)

        try:
            await asyncio.wait_for(event.wait(), timeout=60)
        except asyncio.TimeoutError:
            move_choice["value"] = "No Move (Timed Out)"

        return move_choice["value"]

    def apply_move_effects(self, move, attacker, defender):
    # Apply attack buffs/debuffs
        if "atkboost" in move:
            self.battlestate["buffs"][attacker]["attack"] += move["atkbuff"]
        if "atkreduction" in move:
            self.battlestate["buffs"][defender]["attack"] -= move["atkreduction"]

        if "defbuff" in move:
            self.battlestate["buffs"][attacker]["defense"] += move["defbuff"]
        if "defreduction" in move:
            self.battlestate["buffs"][defender]["defense"] -= move["defreduction"]
        
        if move["numInstances"] > 1 and move["power"] > 0:
            self.battlestate["ongoing_effects"][defender].append({
                "name": move["name"],
                "power": move["power"],
                "turns_left": move["numInstances"]
            })
    def draw_hp_bar(self, draw, x, y, width, height, current_hp, max_hp):
        """Draws a green HP bar with a black border."""
        bar_outline = (x, y, x + width, y + height)
        fill_width = int((current_hp / max_hp) * width)
        bar_fill = (x, y, x + fill_width, y + height)

        draw.rectangle(bar_outline, outline="black", width=2)
        draw.rectangle(bar_fill, fill="green")


    def generate_battle_image(self, pet1,pet2):
        max_hp1 = pet1["base_hp"]
        max_hp2 = pet2["base_hp"]
        hp1 = self.battlestate["hp"]["user"]
        hp2 = self.battlestate["hp"]["opponent"]
        # Load and resize images
        image1 = Image.open(pet1["image"]).resize((200, 200))
        image2 = Image.open(pet2["image"]).resize((200, 200))

        # Create canvas
        canvas = Image.new("RGBA", (500, 320), (240, 240, 240, 255))  # Light grey background
        draw = ImageDraw.Draw(canvas)

        # Paste images
        canvas.paste(image1, (25, 30), image1.convert("RGBA"))
        canvas.paste(image2, (275, 30), image2.convert("RGBA"))

        # Fonts (use default or replace with truetype if needed)
        font = ImageFont.load_default()

        # Names
        draw.text((100, 10), pet1["name"], font=font, fill="black")
        draw.text((350, 10), pet2["name"], font=font, fill="black")

        # HP bars
        self.draw_hp_bar(draw, 25, 240, 200, 20, hp1, max_hp1)
        draw.text((100, 265), f"HP: {hp1}/{max_hp1}", font=font, fill="black")

        self.draw_hp_bar(draw, 275, 240, 200, 20, hp2, max_hp2)
        draw.text((350, 265), f"HP: {hp2}/{max_hp2}", font=font, fill="black")

        canvas.save(self.output_path)

    def process_ongoing_effects(self, defender):
        total_damage = 0
        remaining = list()

        for effect in self.battlestate["ongoing_effects"][defender]:
            damage = effect["power"]
            total_damage += damage
            effect["turns_left"] -= 1

            if effect["turns_left"] > 0:
                remaining.append(effect)
        self.battlestate["ongoing_effects"][defender] = remaining
        return total_damage

    def calculate_damage(self, attacker, defender, move):
        self.apply_move_effects(move)
        atk = max(5,(attacker["attack"] + self.battlestate["buffs"][attacker]["attack"]) * move["power"]  / 100 - (defender["defense"] + self.battlestate["buffs"][defender]["defense"])+self.process_ongoing_effects(defender))
        return atk
    
    async def battling(self, pet1 ,pet2, message, client):
        user_hp = pet1["base_hp"]
        opponent_hp = pet2['base_hp']
        self.battlestate["buffs"] = {
            "opponent": {"attack": 0, "defense": 0},
            "user" : {"attack" : 0, "defense":0}
        }
        priority = pet1 if pet1["speed"] > pet2["speed"] else pet2
        turn = 1
        self.generate_battle_image(pet1,pet2)
        detail_embed = discord.Embed(title=f"Turn {turn} Begins", description="Waiting for move selection...", color=discord.Color.green())
        file = discord.File(self.output_path, filename="battle.png")
        image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
        image_embed.set_image(url="attachment://battle.png")
        battle_message = await message.channel.send(embeds = [image_embed, detail_embed], file=file)
        move_challenger = None
        move_opponent = None
        while(user_hp > 0 and opponent_hp > 0):
            await asyncio.sleep(1)
            move_challenger = self.prompt_move_selection(self.challenger["_id"], pet1, message)
            move_opponent = self.prompt_move_selection(self.opponent["_id"], pet2,message)
            dmg1 = self.calculate_damage("user", "opponent", move_challenger)
            dmg2 = self.calculate_damage("opponent", "user", move_opponent)
            if(priority == pet1):
                self.battlestate["hp"]["opponent"] -= dmg1
                if(self.battlestate["hp"]["opponent"] <= 0):
                    self.battle_end(self.challenger, self.opponent)
                self.battlestate["hp"]["user"] -= dmg2
            else:
                self.battlestate["hp"]["user"] -= dmg2
                if(self.battlestate["hp"]["user"] <= 0):
                    self.battle_end(self.opponent, self.challenger)
                self.battlestate["hp"]["opponent"] -= dmg1
            self.generate_battle_image(pet1,pet2)
            file = discord.File(self.output_path, filename="battle.png")
            image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
            image_embed.set_image(url="attachment://battle.png")
            status_text = (
                f"**Turn {turn}**\n\n"
                f"🟢 **{pet1['name']} (You)**\n"
                f"HP: {user_hp} | ATK Buff: {self.battlestate['buffs']['user']['attack']} | DEF Buff: {self.battlestate['buffs']['user']['defense']}\n"
                f"Last Move: `{move_challenger}`\n\n"
                f"🔵 **{pet2['name']} (Opponent)**\n"
                f"HP: {opponent_hp} | ATK Buff: {self.battlestate['buffs']['opponent']['attack']} | DEF Buff: {self.battlestate['buffs']['opponent']['defense']}\n"
                f"Last Move: `{move_opponent}`"
            )
            detail_embed = discord.Embed(title=f"Turn {turn}", description=status_text, color=discord.Color.green())
            await battle_message.edit(attachments=[file],embeds=[image_embed, detail_embed])
            if(self.battlestate["hp"]["opponent"] <= 0):
                    self.battle_end(self.challenger, self.opponent)
            if(self.battlestate["hp"]["user"] <= 0):
                    self.battle_end(self.opponent, self.challenger)
            turn += 1
    
    async def battle_end(self , winner , loser):
        print(f"{winner["_id"].display_name} - winner, {loser["_id"].display_name} - loser")

