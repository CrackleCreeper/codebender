from Structures.Message import Message
import discord
from discord.ui import View, Button
import asyncio
from PIL import Image, ImageDraw, ImageFont
import os
import math

class BattleLogger:
    
    def __init__(self):
        self.battle_log = []
        
    def clear_log(self):
        
        self.battle_log = []
        
    def add_entry(self, message):
        
        self.battle_log.append(message)

        
    def get_log(self, limit=None):
        
        if limit:
            return self.battle_log[-limit:]
        return self.battle_log
    
    # Status effect logging methods
    def log_stun(self, pet_name, duration):
       
        self.add_entry(f"⚡ **{pet_name}** has been stunned for {duration} turn(s)!")
        
    def log_heal(self, pet_name, amount):
       
        self.add_entry(f"💚 **{pet_name}** healed for {amount} HP!")
        
    def log_dodge(self, pet_name):
        
        self.add_entry(f"💨 **{pet_name}** dodged the attack!")
        
    def log_skipped_turn(self, pet_name, reason="stunned"):
        
        self.add_entry(f"⏭️ **{pet_name}** is {reason} and skips their turn!")
        
    def log_burst_used(self, pet_name, move_name, cooldown):
        
        self.add_entry(f"🔥 **{pet_name}** used burst move **{move_name}**! Cooldown: {cooldown} turns")
        
    def log_throttled_skill(self, pet_name, skill_type, cooldown):

        self.add_entry(f"⏱️ **{pet_name}**'s {skill_type} skills are on cooldown for {cooldown} more turn(s)")
        
    def log_attack(self, attacker_name, defender_name, move_name, damage, is_critical=False):
        critical_text = "💥 CRITICAL HIT! " if is_critical else ""
        self.add_entry(f"⚔️ **{attacker_name}** used **{move_name}** on **{defender_name}**! {critical_text}Dealt {damage:.1f} damage!")
        
    def log_buff(self, pet_name, buff_type, amount):
        emoji = "🔼" if amount > 0 else "🔽"
        buff_name = {"attack": "Attack", "defense": "Defense", "atkreduction": "Attack Reduction", "defreduction": "Defense Reduction"}
        self.add_entry(f"{emoji} **{pet_name}**'s {buff_name.get(buff_type, buff_type)} {'increased' if amount > 0 else 'decreased'} by {abs(amount)}!")
        
    def log_status_effect(self, pet_name, effect_name, duration=None):
        duration_text = f" for {duration} turn(s)" if duration else ""
        self.add_entry(f"✨ **{pet_name}** is affected by **{effect_name}**{duration_text}!")

class battlesystem:
    def __init__(self, client, args, message, opponent, challenger):
        self.client = client
        self.args = args
        self.message = message
        self.opponent = opponent
        self.challenger = challenger
        self.battlestate = {}
        self.output_path = f"PICTURES/battle_preview{self.challenger['_id']}.png"
        self.battle_started = False
        self.winner = None
        self.logger = BattleLogger()  # Initialize the battle logger


    async def battlestart(self):
        pets1 = self.challenger.get("pets", [])
        pets2 = self.opponent.get("pets", [])

        # Get Discord members
        challenger_member = self.message.guild.get_member(self.challenger['_id'])
        opponent_member = self.message.guild.get_member(self.opponent['_id'])

        # Embed showing both players' pets (no buttons yet)
        embed1 = discord.Embed(title=f"{challenger_member.display_name}'s pets", color=discord.Color.green())
        for i, pet in enumerate(pets1, start=1):
            embed1.add_field(name=f"{i}. {pet['name']}", value=pet["rarity"], inline=True)

        embed2 = discord.Embed(title=f"{opponent_member.display_name}'s pets", color=discord.Color.blue())
        for i, pet in enumerate(pets2, start=1):
            embed2.add_field(name=f"{i}. {pet['name']}", value=pet["rarity"], inline=True)

        await self.message.channel.send(embeds=[embed1, embed2])

        # --- STEP 1: Challenger Chooses ---
        challenger_choice = None
        challenger_view = View(timeout=60)
        challenger_event = asyncio.Event()

        for i, pet in enumerate(pets1, start=1):
            async def make_callback(interaction, index=i, pet_name=pet["name"]):
                nonlocal challenger_choice
                if interaction.user.id != self.challenger["_id"]:
                    return await interaction.response.send_message("⛔ Not your pet to select.", ephemeral=True)
                if not challenger_choice:
                    challenger_choice = (index, pet_name)
                    await interaction.response.send_message(f"✅ You selected pet #{index}: **{pet_name}**", ephemeral=True)
                    challenger_event.set()

            btn = Button(label=f"{i}", style=discord.ButtonStyle.green)
            btn.callback = make_callback
            challenger_view.add_item(btn)

        await self.message.channel.send(
            content=f"{challenger_member.mention}, choose your pet:",
            view=challenger_view
        )

        try:
            await asyncio.wait_for(challenger_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            await self.message.channel.send("⏰ Challenger didn't pick in time. Battle cancelled.")
            return

        # --- STEP 2: Opponent Chooses ---
        opponent_choice = None
        opponent_view = View(timeout=60)
        opponent_event = asyncio.Event()

        for i, pet in enumerate(pets2, start=1):
            async def make_callback(interaction, index=i, pet_name=pet["name"]):
                nonlocal opponent_choice
                if interaction.user.id != self.opponent["_id"]:
                    return await interaction.response.send_message("⛔ Not your pet to select.", ephemeral=True)
                if not opponent_choice:
                    opponent_choice = (index, pet_name)
                    await interaction.response.send_message(f"✅ You selected pet #{index}: **{pet_name}**", ephemeral=True)
                    opponent_event.set()

            btn = Button(label=f"{i}", style=discord.ButtonStyle.blurple)
            btn.callback = make_callback
            opponent_view.add_item(btn)

        await self.message.channel.send(
            content=f"{opponent_member.mention}, now choose your pet:",
            view=opponent_view
        )

        try:
            await asyncio.wait_for(opponent_event.wait(), timeout=60)
        except asyncio.TimeoutError:
            await self.message.channel.send("⏰ Opponent didn't pick in time. Battle cancelled.")
            return

        # --- Proceed to Battle ---
        pet1 = pets1[challenger_choice[0] - 1]
        pet2 = pets2[opponent_choice[0] - 1]
        self.challenger_pet = pet1
        self.opponent_pet = pet2
        
        # Log the battle start
        self.logger.clear_log()
        self.logger.add_entry(f"⚔️ Battle begins: **{pet1['name']}** vs **{pet2['name']}**!")
        
        await self.message.channel.send(
            f"⚔️ Both players have selected!\n"
            f"**{challenger_member.mention}** chose: `{pet1['name']}`\n"
            f"**{opponent_member.mention}** chose: `{pet2['name']}`"
        )

        self.battlestate = {
            "hp": {
                self.challenger["_id"]: pet1["base_hp"],
                self.opponent["_id"]: pet2["base_hp"]
            },
            "buffs": {},
            "status_effects": {},
            "used_abilities": set(),
            "ongoing_effects": {
                self.challenger["_id"]: [],
                self.opponent["_id"]: []
            },
            "throttle": { "burst" : {
                self.challenger["_id"] : 0,
                self.opponent["_id"] : 0
            },
            "stun" : {
                self.challenger["_id"] : 0,
                self.opponent["_id"] : 0
            },
            "dodge":{
                self.challenger["_id"] : 0,
                self.opponent["_id"] : 0
            }
            },
            "stunned":{
                self.challenger["_id"] : 0,
                self.opponent["_id"] : 0
            }
        }

        return await self.battling(pet1, pet2, self.message, self.client)

    def level_up(self, pet):
        ELEMENT_GROWTH_RATES = {
                    "Fire": {
                        "attack": 1.05,  # Main stat for Fire
                        "hp": 1.03,
                        "defense": 1.03,
                        "speed": 1.03
                    },
                    "Water": {
                        "attack": 1.03,
                        "hp": 1.05,      
                        "defense": 1.03,
                        "speed": 1.03
                    },
                    "Earth": {
                        "attack": 1.03,
                        "hp": 1.03,
                        "defense": 1.05, # Main stat for Earth
                        "speed": 1.03
                    },
                    "Air": {
                        "attack": 1.03,
                        "hp": 1.03,
                        "defense": 1.03,
                        "speed": 1.05    # Main stat for Air
                    }
                }
        pet["level"] += 1
        growth_rates = ELEMENT_GROWTH_RATES[pet["type"]]
        
        # Update stats
        pet["base_hp"] = round(pet["base_hp"] * growth_rates["hp"])
        pet["attack"] = round(pet["attack"] * growth_rates["attack"])
        pet["defense"] = round(pet["defense"] * growth_rates["defense"])
        pet["speed"] = round(pet["speed"] * growth_rates["speed"])
        
        # Log level up
        self.logger.add_entry(f"🌟 **{pet['name']}** leveled up to level {pet['level']}!")
        self.logger.add_entry(f"📊 New stats: HP: {pet['base_hp']}, ATK: {pet['attack']}, DEF: {pet['defense']}, SPD: {pet['speed']}")
        
        return pet
    
    async def prompt_move_selection(self, user_id, pet, message):
        view = discord.ui.View(timeout=60)
        move_choice = {"value": None}
        event = asyncio.Event()

        # Get pet name for logging
        pet_name = pet["name"]

        # Assuming throttling is tracked for each skill type (adjust this based on your logic)
        throttle_burst = self.battlestate["throttle"]["burst"].get(user_id, 0)
        throttle_stun = self.battlestate["throttle"]["stun"].get(user_id, 0)
        throttle_dodge = self.battlestate["throttle"]["dodge"].get(user_id, 0)

        # Log throttled skills
        if throttle_burst > 0:
            self.logger.log_throttled_skill(pet_name, "Burst", throttle_burst)
        if throttle_stun > 0:
            self.logger.log_throttled_skill(pet_name, "Stun", throttle_stun)
        if throttle_dodge > 0:
            self.logger.log_throttled_skill(pet_name, "Dodge", throttle_dodge)

        available_moves = []

        for index, move in enumerate(pet["moves"], start=1):
            # Skip moves if they are throttled
            if move.get("atktype") == "Burst" and throttle_burst > 0:
                continue
            if move.get("skilltype") == "Heal" and throttle_stun > 0:
                continue
            if move.get("skilltype") == "Dodge" and throttle_dodge > 0:
                continue

            available_moves.append(move)

            btn = discord.ui.Button(label=f"{index}. {move['name']}", style=discord.ButtonStyle.primary)

            async def callback(interaction: discord.Interaction, move_data=move):
                if interaction.user.id != user_id:
                    await interaction.response.send_message("❌ You can't choose this move.", ephemeral=True)
                    return
                if move_choice["value"] is None:
                    move_choice["value"] = move_data
                    await interaction.response.send_message(f"✅ You selected **{move_data['name']}**!", ephemeral=True)
                    event.set()

            btn.callback = callback
            view.add_item(btn)

        # If no available moves, skip turn
        if not available_moves:
            self.logger.log_skipped_turn(pet_name, "out of available moves")
            await message.channel.send(f"⚠ <@{user_id}> has no available moves this turn and must skip!")
            return {"name": "No Available Move", "power": 0, "numInstances": 0, "atktype": "Basic", "skilltype": "Basic"}

        await message.channel.send(
            content=f"<@{user_id}>, choose a move for **{pet['name']}**:",
            view=view
        )

        try:
            await asyncio.wait_for(event.wait(), timeout=60)
        except asyncio.TimeoutError:
            self.logger.add_entry(f"⏰ <@{user_id}> didn't pick a move in time!")
            await self.message.channel.send(f"⏰ <@{user_id}> didn't pick a move in time!")
            if user_id == self.challenger["_id"]:
                return await self.battle_end(self.opponent_pet, self.challenger_pet, self.opponent, self.challenger)
            else:
                return await self.battle_end(self.challenger_pet, self.opponent_pet, self.challenger, self.opponent)

        return move_choice["value"]

    def apply_move_effects(self, move, attacker_id, defender_id):
        # Get pet names for logging
        attacker_pet = self.challenger_pet if attacker_id == self.challenger["_id"] else self.opponent_pet
        defender_pet = self.opponent_pet if attacker_id == self.challenger["_id"] else self.challenger_pet
        
        if "atkbuff" in move and move["atkbuff"] > 0:
            if (self.battlestate["buffs"][attacker_id]["attack"]["nums"] > 1):
                atk = max(move["atkbuff"], self.battlestate["buffs"][attacker_id]["attack"]["value"])
                self.battlestate["buffs"][attacker_id]["attack"]["value"] = atk
                if(atk == move["atkbuff"]):
                    self.battlestate["buffs"][attacker_id]["attack"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][attacker_id]["attack"]["nums"] -= 1
            else:
                self.battlestate["buffs"][attacker_id]["attack"]["value"] = move["atkbuff"]
                self.battlestate["buffs"][attacker_id]["attack"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(attacker_pet["name"], "attack", move["atkbuff"])

        if "atkreduction" in move and move["atkreduction"] > 0:
            if (self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] > 1):
                atk = max(move["atkreduction"], self.battlestate["buffs"][defender_id]["atkreduction"]["value"])
                self.battlestate["buffs"][attacker_id]["atkreduction"]["value"] = atk
                if(atk == move["atkreduction"]):
                    self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] -= 1
            else:
                self.battlestate["buffs"][defender_id]["atkreduction"]["value"] = move["atkreduction"]
                self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(defender_pet["name"], "atkreduction", -move["atkreduction"])
            
        if "defbuff" in move and move["defbuff"] > 0:
            defe = max(move["defbuff"], self.battlestate["buffs"][attacker_id]["defense"]["value"])
            self.battlestate["buffs"][attacker_id]["defense"]["value"] = defe
            if (self.battlestate["buffs"][attacker_id]["defense"]["nums"] > 1):
                if(defe == move["defbuff"]):
                    self.battlestate["buffs"][attacker_id]["defense"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][attacker_id]["defense"]["nums"] -= 1
            else:
                self.battlestate["buffs"][attacker_id]["defense"]["value"] = move["defbuff"]
                self.battlestate["buffs"][attacker_id]["defense"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(attacker_pet["name"], "defense", move["defbuff"])
            
        if "defreduction" in move and move["defreduction"] > 0:
            if (self.battlestate["buffs"][defender_id]["defreduction"]["nums"] > 1):
                defe = max(move["defreduction"], self.battlestate["buffs"][defender_id]["defreduction"]["value"])
                self.battlestate["buffs"][attacker_id]["defreduction"]["value"] = defe
                if(defe == move["defreduction"]):
                    self.battlestate["buffs"][defender_id]["defreduction"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][defender_id]["defreduction"]["nums"] -= 1
            else:
                self.battlestate["buffs"][defender_id]["defreduction"]["value"] = move["defreduction"]
                self.battlestate["buffs"][defender_id]["defreduction"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(defender_pet["name"], "defreduction", -move["defreduction"])

    def draw_hp_bar(self, draw, x, y, width, height, current_hp, max_hp):
        """Draws an HP bar with a black border that shows empty when HP is negative."""
        # Draw the border
        bar_outline = (x, y, x + width, y + height)
        draw.rectangle(bar_outline, outline="black", width=2)
        
        # Ensure current_hp is not negative for display purposes
        display_hp = max(0, current_hp)
        
        # Calculate fill width based on current HP percentage
        if max_hp > 0:  # Prevent division by zero
            fill_width = int((display_hp / max_hp) * width)
            # Make sure fill doesn't go negative
            fill_width = max(0, fill_width)
            
            # Only draw the filled portion if there's HP remaining
            if fill_width > 0:
                bar_fill = (x, y, x + fill_width, y + height)
                
                # Choose color based on HP percentage
                hp_percent = display_hp / max_hp
                if hp_percent > 0.6:
                    color = "green"
                elif hp_percent > 0.3:
                    color = "yellow"
                else:
                    color = "red"
                    
                draw.rectangle(bar_fill, fill=color)


    def generate_battle_image(self, pet1, pet2):
        max_hp1 = pet1["base_hp"]
        max_hp2 = pet2["base_hp"]
        hp1 = max(0, math.floor(self.battlestate["hp"][self.challenger["_id"]]))
        hp2 = max(0, math.floor(self.battlestate["hp"][self.opponent["_id"]]))
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

        # Status indicators
        challenger_id = self.challenger["_id"]
        opponent_id = self.opponent["_id"]
        
        # Draw status indicators for challenger pet
        status_y = 290
        if self.battlestate["stunned"][challenger_id] > 0:
            draw.text((25, status_y), f"STUNNED ({self.battlestate['stunned'][challenger_id]})", font=font, fill="red")
            status_y += 15
        
        if self.battlestate["throttle"]["burst"][challenger_id] > 0:
            draw.text((25, status_y), f"BURST CD ({self.battlestate['throttle']['burst'][challenger_id]})", font=font, fill="blue")
            status_y += 15
            
        # Draw status indicators for opponent pet
        status_y = 290
        if self.battlestate["stunned"][opponent_id] > 0:
            draw.text((275, status_y), f"STUNNED ({self.battlestate['stunned'][opponent_id]})", font=font, fill="red")
            status_y += 15
            
        if self.battlestate["throttle"]["burst"][opponent_id] > 0:
            draw.text((275, status_y), f"BURST CD ({self.battlestate['throttle']['burst'][opponent_id]})", font=font, fill="blue")

        canvas.save(self.output_path)

    def process_ongoing_effects(self, defender):
        total_damage = 0
        remaining = []
        for effect in self.battlestate["ongoing_effects"][defender]:
            if effect["numInstances"] > 1:
                remaining.append(effect)

        for effect in remaining:
            damage = effect["power"]
            total_damage += damage
            
            # Log ongoing damage effects
            if damage > 0:
                defender_pet = self.challenger_pet if defender == self.challenger["_id"] else self.opponent_pet
                self.logger.add_entry(f"🔄 **{defender_pet['name']}** takes {damage} ongoing damage from status effects!")

        return total_damage

    def calculate_damage(self, attacker, defender, move, chal, defen):
        self.apply_move_effects(move, chal, defen)

        # Get stats with buffs/debuffs
        attacker_attack = attacker["attack"] + self.battlestate["buffs"][chal]["attack"]["value"] - self.battlestate["buffs"][chal]["atkreduction"]["value"]

        defender_defense = defender["defense"] + self.battlestate["buffs"][defen]["defense"]["value"] - self.battlestate["buffs"][defen]["defreduction"]["value"]

        defender_defense = max(1, defender_defense)

        base_damage = (attacker_attack * move["power"]) / defender_defense

        effect_damage = self.process_ongoing_effects(defen)

        atk = max(0, base_damage + effect_damage)

        # Log damage calculation detail
        
        return atk

            
    async def battling(self, pet1, pet2, message, client):
        challenger_id = self.challenger["_id"]
        opponent_id = self.opponent["_id"]
        user_hp = pet1["base_hp"]
        opponent_hp = pet2['base_hp']
        self.battlestate["buffs"] = {
            challenger_id: {"attack": {
                "value" : 0,
                "nums" : 0
            }, "defense": {
                "value" : 0,
                "nums" : 0
            },
            "atkreduction":{
                "value" : 0,
                "nums" : 0
            },
            "defreduction":{
                "value" : 0,
                "nums" : 0
            }
            },
            opponent_id: {"attack": {
                "value" : 0,
                "nums" : 0
            }, "defense": {
                "value" : 0,
                "nums" : 0
            },
            "atkreduction":{
                "value" : 0,
                "nums" : 0
            },
            "defreduction":{
                "value" : 0,
                "nums" : 0
            }
            }
        }
        priority = pet1 if pet1["speed"] > pet2["speed"] else pet2
        turn = 1
        self.generate_battle_image(self.challenger_pet, self.opponent_pet)
        
        # Log battle start with priority information
        self.logger.add_entry(f"🏁 Battle starts! **{priority['name']}** will go first due to higher speed ({priority['speed']})!")
        
        detail_embed = discord.Embed(title=f"Turn {turn} Begins", description="Waiting for move selection...", color=discord.Color.green())
        file = discord.File(self.output_path, filename="battle.png")
        image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
        image_embed.set_image(url="attachment://battle.png")
        await message.channel.send(embeds=[image_embed, detail_embed], file=file)
        move_challenger = None
        move_opponent = None
        
        while(user_hp > 0 and opponent_hp > 0):
            self.logger.add_entry(f"\n📢 **Turn {turn} begins!**")
            
            # Handle stun status
            if self.battlestate["stunned"][challenger_id] > 0:
                self.battlestate["stunned"][challenger_id] -= 1
                if self.battlestate["stunned"][challenger_id] == 0:
                    self.logger.add_entry(f"✅ **{pet1['name']}** is no longer stunned!")
                else:
                    self.logger.log_skipped_turn(pet1["name"])
            
            if self.battlestate["stunned"][opponent_id] > 0:
                self.battlestate["stunned"][opponent_id] -= 1
                if self.battlestate["stunned"][opponent_id] == 0:
                    self.logger.add_entry(f"✅ **{pet2['name']}** is no longer stunned!")
                else:
                    self.logger.log_skipped_turn(pet2["name"])
            
            # Reset moves
            move_challenger = {"name": "No Available Move", "power": 0, "numInstances": 0, "atktype": "Basic", "skilltype": "Basic"}
            move_opponent = {"name": "No Available Move", "power": 0, "numInstances": 0, "atktype": "Basic", "skilltype": "Basic"}
            
            # Handle throttle cooldowns
            throttle_types = ["burst", "stun", "dodge"]
            for throttle_type in throttle_types:
                if self.battlestate["throttle"][throttle_type].get(challenger_id, 0) > 0:
                    self.battlestate["throttle"][throttle_type][challenger_id] -= 1
                    if self.battlestate["throttle"][throttle_type][challenger_id] == 0:
                        self.logger.add_entry(f"✅ **{pet1['name']}**'s {throttle_type.capitalize()} skills are now available!")
                
                if self.battlestate["throttle"][throttle_type].get(opponent_id, 0) > 0:
                    self.battlestate["throttle"][throttle_type][opponent_id] -= 1
                    if self.battlestate["throttle"][throttle_type][opponent_id] == 0:
                        self.logger.add_entry(f"✅ **{pet2['name']}**'s {throttle_type.capitalize()} skills are now available!")
            
            await asyncio.sleep(1)
            
            # Get moves from players
            if self.battlestate["stunned"][challenger_id] == 0:
                move_challenger = await self.prompt_move_selection(self.challenger["_id"], pet1, message)
                if(move_challenger == self.winner):
                    return self.winner
            
            if self.battlestate["stunned"][opponent_id] == 0:
                move_opponent = await self.prompt_move_selection(self.opponent["_id"], pet2, message)
                if(move_opponent == self.winner):
                    return self.winner
            
            # Add ongoing effects
            self.battlestate["ongoing_effects"][challenger_id].append(move_opponent)
            self.battlestate["ongoing_effects"][opponent_id].append(move_challenger)
            
            # Handle throttled skills
            for throttle_type in throttle_types:
                if throttle_type == "burst":
                    if(move_challenger["atktype"] == throttle_type.capitalize()):
                        self.battlestate["throttle"][throttle_type][challenger_id] = 4
                        self.logger.log_burst_used(pet1["name"], move_challenger["name"], 4)
                    if move_opponent["atktype"] == throttle_type.capitalize():
                        self.battlestate["throttle"][throttle_type][opponent_id] = 4
                        self.logger.log_burst_used(pet2["name"], move_opponent["name"], 4)
                else:
                    if(move_challenger["skilltype"] == throttle_type.capitalize()):
                        self.battlestate["throttle"][throttle_type][challenger_id] = 4
                        self.logger.log_throttled_skill(pet1["name"], throttle_type.capitalize(), 4)
                    if move_opponent["skilltype"] == throttle_type.capitalize():
                        self.battlestate["throttle"][throttle_type][opponent_id] = 4
                        self.logger.log_throttled_skill(pet2["name"], throttle_type.capitalize(), 4)

            # Handle healing
            if move_challenger["skilltype"] == "Heal":
                old_hp = self.battlestate["hp"][challenger_id]
                self.battlestate["hp"][challenger_id] = min(self.challenger_pet["base_hp"], move_challenger["heal"] + self.battlestate["hp"][challenger_id])
                heal_amount = self.battlestate["hp"][challenger_id] - old_hp
                self.logger.log_heal(pet1["name"], heal_amount)
            if move_opponent["skilltype"] == "Heal":
                old_hp = self.battlestate["hp"][opponent_id]
                self.battlestate["hp"][opponent_id] = min(self.opponent_pet["base_hp"], move_opponent["heal"] + self.battlestate["hp"][opponent_id])
                heal_amount = self.battlestate["hp"][opponent_id] - old_hp
                self.logger.log_heal(pet2["name"], heal_amount)
                
            # Calculate damage
            dmg1 = self.calculate_damage(pet1, pet2, move_challenger, challenger_id, opponent_id)
            dmg2 = self.calculate_damage(pet2, pet1, move_opponent, opponent_id, challenger_id)

            # Handle stun effects
            if (move_challenger["skilltype"] == "Stun"):
                stun_duration = move_challenger["numInstances"] + 1
                self.battlestate["stunned"][opponent_id] = stun_duration
                self.logger.log_stun(pet2["name"], stun_duration)
            if (move_opponent["skilltype"] == "Stun"):
                stun_duration = move_opponent["numInstances"] + 1
                self.battlestate["stunned"][challenger_id] = stun_duration
                self.logger.log_stun(pet1["name"], stun_duration)
                
            # Apply damage based on priority
            if(priority == pet1):
                if(move_opponent["skilltype"] != "Dodge"):
                    self.battlestate["hp"][opponent_id] -= dmg1
                    self.logger.log_attack(pet1["name"], pet2["name"], move_challenger["name"], dmg1)
                else:
                    self.logger.log_dodge(pet2["name"])
                if(self.battlestate["hp"][opponent_id] <= 0):
                    return await self.battle_end(pet1, pet2, self.challenger, self.opponent)
                if(move_challenger["skilltype"] != "Dodge"):
                    self.battlestate["hp"][challenger_id] -= dmg2
                    self.logger.log_attack(pet2["name"], pet1["name"], move_opponent["name"], dmg2)
                else:
                    self.logger.log_dodge(pet1["name"])
            else:
                if(move_challenger["skilltype"] != "Dodge"):
                    self.battlestate["hp"][challenger_id] -= dmg2
                    self.logger.log_attack(pet2["name"], pet1["name"], move_opponent["name"], dmg2)
                else:
                    self.logger.log_dodge(pet1["name"])
                if(self.battlestate["hp"][challenger_id] <= 0):
                    return await self.battle_end(pet2, pet1, self.opponent, self.challenger)
                if(move_opponent["skilltype"] != "Dodge"):
                    self.battlestate["hp"][opponent_id] -= dmg1
                    self.logger.log_attack(pet1["name"], pet2["name"], move_challenger["name"], dmg1)
                else:
                    self.logger.log_dodge(pet2["name"])
                    
            # Check for battle end conditions
            if(self.battlestate["hp"][opponent_id] <= 0):
                return await self.battle_end(pet1, pet2, self.challenger, self.opponent)
            if(self.battlestate["hp"][challenger_id] <= 0):
                return await self.battle_end(pet2, pet1, self.opponent, self.challenger)
                
            # Update battle display
            self.generate_battle_image(pet1, pet2)
            file = discord.File(self.output_path, filename="battle.png")
            image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
            image_embed.set_image(url="attachment://battle.png")
            
            # Get recent battle log entries for the status text
            recent_log = self.logger.get_log(5)
            log_text = "\n".join(recent_log)
            
            status_text = (
                f"**Turn {turn}**\n\n"
                f"🟢 **{pet1['name']}**\n"
                f"HP: {max(0, math.floor(self.battlestate['hp'][challenger_id]))}/{pet1['base_hp']} | ATK Buff: {self.battlestate['buffs'][challenger_id]['attack']['value']} | DEF Buff: {self.battlestate['buffs'][challenger_id]['defense']['value']}\n"
                f"Last Move: `{move_challenger['name']}`\n\n"
                f"🔵 **{pet2['name']}**\n"
                f"HP: {max(0, math.floor(self.battlestate['hp'][opponent_id]))}/{pet2['base_hp']} | ATK Buff: {self.battlestate['buffs'][opponent_id]['attack']['value']} | DEF Buff: {self.battlestate['buffs'][opponent_id]['defense']['value']}\n"
                f"Last Move: `{move_opponent['name']}`\n\n"
                f"**Battle Log:**\n{log_text}"
            )
            
            detail_embed = discord.Embed(title=f"Turn {turn}", description=status_text, color=discord.Color.green())
            await message.channel.send(file=file, embeds=[image_embed, detail_embed])
            
            turn += 1
        
    async def battle_end(self, pet1, pet2, winner, loser):
        self.winner = winner
        self.logger.add_entry(f"🏆 **{pet1['name']}** has won the battle!")
        
        self.generate_battle_image(self.challenger_pet, self.opponent_pet)
        file = discord.File(self.output_path, filename="battle.png")
        image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
        image_embed.set_image(url="attachment://battle.png")
        
        # Create a battle summary embed
        battle_summary = discord.Embed(title="Battle Summary", color=discord.Color.gold())
        battle_summary.description = "\n".join(self.logger.get_log(10))  # Show the last 10 log entries
        
        await self.message.channel.send(file=file, embeds=[image_embed, battle_summary])
    
        challenger_member = self.message.guild.get_member(winner['_id'])
        opponent_member = self.message.guild.get_member(loser['_id'])
        self.output_path = pet1["image"]
        file = discord.File(self.output_path, filename="battle.png")
        image_embed = discord.Embed(title=f"{challenger_member.display_name} WINS!!")
        image_embed.set_image(url="attachment://battle.png")
        await self.message.channel.send(file=file, embed=image_embed)
        
        # Calculate and log XP gain
        xp = math.floor((pet1["level"] - pet2["level"] + 20) * (pet1["level"] + pet2["level"]) / 3)
        self.logger.add_entry(f"💫 **{pet1['name']}** gained {xp} XP from the battle!")
        
        xp_required = 100 * pow(1.2, pet1["level"] - 1)
        if xp + pet1["xp"] >= xp_required:
            file2 = discord.File(self.output_path, filename="battle.png")  # Reopen file
            image_embed = discord.Embed(title=f"{pet1['name']} LEVELLED UP to {pet1['level'] + 1}!!")
            pet1 = self.level_up(pet1)
            image_embed.set_image(url="attachment://battle.png")
            await self.message.channel.send(file=file2, embed=image_embed)
            self.client.usersCollection.update_one({"_id": winner["_id"], "pets.name": pet1["name"]}, {"$set": {"pets.$.xp": pet1["xp"] + xp - xp_required,
                                                                                                               "pets.$.level": pet1["level"], 
                                                                                                               'pets.$.attack': pet1["attack"], 
                                                                                                               "pets.$.defense": pet1["defense"],
                                                                                                               "pets.$.speed": pet1["speed"],
                                                                                                               "pets.$.base_hp": pet1["base_hp"]}})
        else:
            self.client.usersCollection.update_one({"_id": winner["_id"], "pets.name": pet1["name"]}, {"$inc": {"pets.$.xp": xp}})
        
        # Clean up temporary files
        os.remove(f"PICTURES/battle_preview{self.challenger['_id']}.png")
        return winner