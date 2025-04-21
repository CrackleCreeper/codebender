import random
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont
import asyncio
import discord
from discord.ui import View, Button

# Create a battle logger class
class BattleLogger:
    def __init__(self):
        self.log_entries = []
    
    def add_entry(self, entry):
        """Add a general entry to the battle log"""
        self.log_entries.append(entry)
    
    def log_attack(self, attacker_name, defender_name, move_name, damage):
        """Log an attack"""
        entry = f"⚔️ **{attacker_name}** used **{move_name}** on **{defender_name}**, dealing **{round(damage, 1)}** damage!"
        self.add_entry(entry)
    
    def log_heal(self, pet_name, heal_amount):
        """Log a healing action"""
        entry = f"💚 **{pet_name}** healed for **{round(heal_amount, 1)}** HP!"
        self.add_entry(entry)
    
    def log_buff(self, pet_name, buff_type, value):
        """Log a buff application"""
        if value > 0:
            entry = f"🔼 **{pet_name}**'s {buff_type} increased by {value}!"
        else:
            entry = f"🔽 **{pet_name}**'s {buff_type} decreased by {abs(value)}!"
        self.add_entry(entry)
    
    def log_dodge(self, pet_name):
        """Log a dodge action"""
        entry = f"💨 **{pet_name}** dodged the attack!"
        self.add_entry(entry)
    
    def log_stun(self, pet_name, duration):
        """Log a stun effect"""
        entry = f"⚡ **{pet_name}** is stunned for {duration} turn(s)!"
        self.add_entry(entry)
    
    def log_burst_used(self, pet_name, move_name, cooldown):
        """Log when a burst skill is used"""
        entry = f"🌟 **{pet_name}** used burst skill **{move_name}**! (Cooldown: {cooldown} turns)"
        self.add_entry(entry)
    
    def log_throttled_skill(self, pet_name, skill_type, cooldown):
        """Log when a skill is on cooldown"""
        entry = f"⏳ **{pet_name}**'s {skill_type} skills are on cooldown for {cooldown} turns!"
        self.add_entry(entry)
    
    def log_skipped_turn(self, pet_name, reason):
        """Log when a turn is skipped"""
        entry = f"⏭️ **{pet_name}** skipped their turn ({reason})!"
        self.add_entry(entry)
    
    def get_log(self, num_entries=None):
        """Get the most recent log entries"""
        if num_entries is None:
            return self.log_entries
        return self.log_entries[-num_entries:]

# Load boss data
with open("./Structures/Bosses.json", "r") as f:
    bosses = json.load(f)

class BossBattle:
    def __init__(self):
        self.name = "bossbattle"
        self.category = "Battle"
        self.number_args = 0
        self.description = "Starts a boss battle! (very difficult)"
        self.user_permissions = []
        self.cooldown = 0 
        self.winner = None
        self.logger = BattleLogger()  # Initialize the battle logger
        
    def chooseBasicSkill(self):
        basicSkillList = [x for x in self.skillList if x["atktype"] == "Basic"]
        return random.choice(basicSkillList) if basicSkillList else None

    def chooseBurstSkill(self):
        burstSkillList = [x for x in self.skillList if x["atktype"] == "Burst"]
        return random.choice(burstSkillList) if burstSkillList else None

    def bossMove(self):
        # Fixed bug: basicCounter should be a class attribute
        if not hasattr(self, 'basicCounter'):
            self.basicCounter = 1
            
        if self.basicCounter < 3:
            skill = self.chooseBasicSkill()
            self.basicCounter += 1
        else:
            skill = self.chooseBurstSkill()
            self.basicCounter = 1
        
        if skill:
            return skill
        else:
            # Fallback if no skill is found
            return {"name": "No Available Move", "power": 0, "numInstances": 0, "atktype": "Basic", "skilltype": "Basic"}
    
    async def prompt_pet_selection(self):
        challenger_member = self.message.guild.get_member(self.challenger['_id'])

        embed1 = discord.Embed(
            title=f"{challenger_member.display_name}'s pets",
            color=discord.Color.green()
        )
        for i, pet in enumerate(self.pets, start=1):
            embed1.add_field(name=f"{i}. {pet['name']}", value=pet["rarity"], inline=True)

        await self.message.channel.send(embeds=[embed1])

        challenger_view = View(timeout=60)
        challenger_event = asyncio.Event()

        # Define the callback factory
        def make_callback(index, pet_name):
            async def callback(interaction):
                if interaction.user.id != self.challenger["_id"]:
                    return await interaction.response.send_message("⛔ Not your pet to select.", ephemeral=True)
                if self.challenger_pet is None:
                    self.challenger_pet = self.pets[index - 1]

                    self.pets = self.pets[:index - 1] + self.pets[index:]
                    await interaction.response.send_message(f"✅ You selected pet #{index}: **{pet_name}**", ephemeral=True)
                    challenger_event.set()
            return callback

        for i, pet in enumerate(self.pets, start=1):
            btn = Button(label=f"{i}", style=discord.ButtonStyle.green)
            btn.callback = make_callback(i, pet["name"])
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


    async def prompt_move_selection(self, user_id, pet, message):
        view = discord.ui.View(timeout=60)
        move_choice = {"value": None}
        event = asyncio.Event()

        pet_name = pet["name"]

        throttle_burst = self.battlestate["throttle"]["burst"].get(user_id, 0)
        throttle_dodge = self.battlestate["throttle"]["dodge"].get(user_id, 0)


        if throttle_burst > 0:
            self.logger.log_throttled_skill(pet_name, "Burst", throttle_burst)
        if throttle_dodge > 0:
            self.logger.log_throttled_skill(pet_name, "Dodge", throttle_dodge)

        available_moves = []

        for index, move in enumerate(pet["moves"], start=1):

            if move.get("atktype") == "Burst" and throttle_burst > 0:
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
            await message.channel.send(f"⏰ <@{user_id}> didn't pick a move in time!")
            if user_id == self.challenger["_id"]:
                return await self.battle_end(self.boss, self.challenger_pet, self.challenger)

        return move_choice["value"]

    def apply_move_effects(self, move, attacker_id, defender_id):
        attacker_pet = self.challenger_pet if attacker_id == self.challenger["_id"] else self.boss
        defender_pet = self.boss if attacker_id == self.challenger["_id"] else self.challenger_pet
        

        if "atkbuff" in move and move["atkbuff"] > 0:
            if self.battlestate["buffs"][attacker_id]["attack"]["nums"] > 1:
                atk = max(move["atkbuff"], self.battlestate["buffs"][attacker_id]["attack"]["value"])
                self.battlestate["buffs"][attacker_id]["attack"]["value"] = atk
                if atk == move["atkbuff"]:
                    self.battlestate["buffs"][attacker_id]["attack"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][attacker_id]["attack"]["nums"] -= 1
            else:
                self.battlestate["buffs"][attacker_id]["attack"]["value"] = move["atkbuff"]
                self.battlestate["buffs"][attacker_id]["attack"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(attacker_pet["name"], "attack", move["atkbuff"])

        if "atkreduction" in move and move["atkreduction"] > 0:

            if self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] > 1:
                atk = max(move["atkreduction"], self.battlestate["buffs"][defender_id]["atkreduction"]["value"])
                self.battlestate["buffs"][defender_id]["atkreduction"]["value"] = atk
                if atk == move["atkreduction"]:
                    self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] -= 1
            else:
                self.battlestate["buffs"][defender_id]["atkreduction"]["value"] = move["atkreduction"]
                self.battlestate["buffs"][defender_id]["atkreduction"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(defender_pet["name"], "attack", -move["atkreduction"])
            
        if "defbuff" in move and move["defbuff"] > 0:
            if self.battlestate["buffs"][attacker_id]["defense"]["nums"] > 1:
                defe = max(move["defbuff"], self.battlestate["buffs"][attacker_id]["defense"]["value"])
                self.battlestate["buffs"][attacker_id]["defense"]["value"] = defe
                if defe == move["defbuff"]:
                    self.battlestate["buffs"][attacker_id]["defense"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][attacker_id]["defense"]["nums"] -= 1
            else:
                self.battlestate["buffs"][attacker_id]["defense"]["value"] = move["defbuff"]
                self.battlestate["buffs"][attacker_id]["defense"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(attacker_pet["name"], "defense", move["defbuff"])
            
        if "defreduction" in move and move["defreduction"] > 0:

            if self.battlestate["buffs"][defender_id]["defreduction"]["nums"] > 1:
                defe = max(move["defreduction"], self.battlestate["buffs"][defender_id]["defreduction"]["value"])
                self.battlestate["buffs"][defender_id]["defreduction"]["value"] = defe
                if defe == move["defreduction"]:
                    self.battlestate["buffs"][defender_id]["defreduction"]["nums"] = move["numInstances"]
                else:
                    self.battlestate["buffs"][defender_id]["defreduction"]["nums"] -= 1
            else:
                self.battlestate["buffs"][defender_id]["defreduction"]["value"] = move["defreduction"]
                self.battlestate["buffs"][defender_id]["defreduction"]["nums"] = move["numInstances"]
            
            self.logger.log_buff(defender_pet["name"], "defense", -move["defreduction"])

    def draw_hp_bar(self, draw, x, y, width, height, current_hp, max_hp):

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
        hp2 = max(0, math.floor(self.battlestate["hp"]["boss"]))
        
        try:
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
            opponent_id = "boss"
            
            # Draw status indicators for challenger pet
            status_y = 290
                
            # Draw status indicators for opponent pet
            if self.battlestate["throttle"]["burst"].get(opponent_id, 0) > 0:
                draw.text((275, status_y), f"BURST CD ({self.battlestate['throttle']['burst'][opponent_id]})", font=font, fill="blue")

            canvas.save(self.output_path)
        except Exception as e:
            print(f"Error generating battle image: {e}")

    def process_ongoing_effects(self, defender):
        damage = 0
        remaining = []
        
        for effect in self.battlestate["ongoing_effects"][defender]:
            if effect.get("numInstances", 0) > 1:
                effect["numInstances"] -= 1
                remaining.append(effect)
                if effect.get("power", 0) > 0:
                    damage = max(damage, effect["power"])
        
        self.battlestate["ongoing_effects"][defender] = remaining
            
        if damage > 0:
            defender_pet = self.challenger_pet if defender == self.challenger["_id"] else self.boss
            self.logger.add_entry(f"🔄 **{defender_pet['name']}** takes {damage} ongoing damage from status effects!")

        return damage

    def calculate_damage(self, attacker, defender, move, chal, defen):
        self.apply_move_effects(move, chal, defen)

        attacker_attack = attacker["attack"] + self.battlestate["buffs"][chal]["attack"]["value"] - self.battlestate["buffs"][chal]["atkreduction"]["value"]
        defender_defense = defender["defense"] + self.battlestate["buffs"][defen]["defense"]["value"] - self.battlestate["buffs"][defen]["defreduction"]["value"]

        defender_defense = max(1, defender_defense)

        base_damage = (attacker_attack * move["power"]) 

        effect_damage = self.process_ongoing_effects(defen)

        final_damage = max(0, (base_damage + effect_damage) / defender_defense)
        
        return final_damage

            
    async def battling(self, message):
        pet1 = self.challenger_pet
        pet2 = self.boss
        challenger_id = self.challenger["_id"]
        opponent_id = "boss"
        
        self.battlestate["hp"][challenger_id] = pet1["base_hp"]
        self.battlestate["hp"][opponent_id] = pet2["base_hp"]
        
        priority = pet1 if pet1["speed"] > pet2["speed"] else pet2
        turn = 1
        
        self.generate_battle_image(pet1, pet2)
        
        self.logger.add_entry(f"🏁 Battle starts! **{priority['name']}** will go first due to higher speed ({priority['speed']})!")
        
        detail_embed = discord.Embed(title=f"Turn {turn} Begins", description="Waiting for move selection...", color=discord.Color.green())
        file = discord.File(self.output_path, filename="battle.png")
        image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
        image_embed.set_image(url="attachment://battle.png")
        await message.channel.send(embeds=[image_embed, detail_embed], file=file)
        
        move_challenger = None
        move_opponent = None
        
        while self.battlestate["hp"][challenger_id] > 0 and self.battlestate["hp"][opponent_id] > 0:
            self.logger.add_entry(f"\n📢 **Turn {turn} begins!**")
            
            move_challenger = {"name": "No Available Move", "power": 0, "numInstances": 0, "atktype": "Basic", "skilltype": "Basic"}
            move_opponent = {"name": "No Available Move", "power": 0, "numInstances": 0, "atktype": "Basic", "skilltype": "Basic"}
            
            throttle_types = ["burst", "dodge"]
            for throttle_type in throttle_types:
                if self.battlestate["throttle"][throttle_type].get(opponent_id, 0) > 0:
                    self.battlestate["throttle"][throttle_type][opponent_id] -= 1
                    if self.battlestate["throttle"][throttle_type][opponent_id] == 0:
                        self.logger.add_entry(f"✅ **{pet2['name']}**'s {throttle_type.capitalize()} skills are now available!")
                
                if self.battlestate["throttle"][throttle_type].get(challenger_id, 0) > 0:
                    self.battlestate["throttle"][throttle_type][challenger_id] -= 1
                    if self.battlestate["throttle"][throttle_type][challenger_id] == 0:
                        self.logger.add_entry(f"✅ **{pet1['name']}**'s {throttle_type.capitalize()} skills are now available!")
            
            await asyncio.sleep(1)
            
            move_challenger = await self.prompt_move_selection(challenger_id, pet1, message)
            if move_challenger == self.winner:
                return self.winner
            
            move_opponent = self.bossMove()
            if move_opponent == self.winner:
                return self.winner
            
            for throttle_type in throttle_types:
                if throttle_type == "burst":
                    if move_opponent.get("atktype") == "Burst":
                        self.battlestate["throttle"][throttle_type][opponent_id] = 3
                        self.logger.log_burst_used(pet2["name"], move_opponent["name"], 3)
                    if move_challenger.get("atktype") == "Burst":
                        self.battlestate["throttle"][throttle_type][challenger_id] = 3
                        self.logger.log_burst_used(pet1["name"], move_challenger["name"], 3)
                else:
                    if move_challenger.get("skilltype") == throttle_type.capitalize():
                        self.battlestate["throttle"][throttle_type][challenger_id] = 3
                        self.logger.log_throttled_skill(pet1["name"], throttle_type.capitalize(), 3)
                    if move_opponent.get("skilltype") == throttle_type.capitalize():
                        self.battlestate["throttle"][throttle_type][opponent_id] = 3
                        self.logger.log_throttled_skill(pet2["name"], throttle_type.capitalize(), 3)

            if move_challenger.get("skilltype") == "Heal":
                old_hp = self.battlestate["hp"][challenger_id]
                self.battlestate["hp"][challenger_id] = min(pet1["base_hp"], move_challenger.get("heal", 0) + self.battlestate["hp"][challenger_id])
                heal_amount = self.battlestate["hp"][challenger_id] - old_hp
                self.logger.log_heal(pet1["name"], heal_amount)
                
            if move_opponent.get("skilltype") == "Heal":
                old_hp = self.battlestate["hp"][opponent_id]
                self.battlestate["hp"][opponent_id] = min(pet2["base_hp"], move_opponent.get("heal", 0) + self.battlestate["hp"][opponent_id])
                heal_amount = self.battlestate["hp"][opponent_id] - old_hp
                self.logger.log_heal(pet2["name"], heal_amount)
                
            dmg1 = self.calculate_damage(pet1, pet2, move_challenger, challenger_id, opponent_id)
            dmg2 = self.calculate_damage(pet2, pet1, move_opponent, opponent_id, challenger_id)

            if move_challenger.get("skilltype") == "Stun":
                stun_duration = move_challenger.get("numInstances", 0) + 1
                if "stunned" not in self.battlestate:
                    self.battlestate["stunned"] = {opponent_id: 0, challenger_id: 0}
                self.battlestate["stunned"][opponent_id] = stun_duration
                self.logger.log_stun(pet2["name"], stun_duration - 1)
                
            if move_opponent.get("skilltype") == "Stun":
                stun_duration = move_opponent.get("numInstances", 0) + 1
                if "stunned" not in self.battlestate:
                    self.battlestate["stunned"] = {opponent_id: 0, challenger_id: 0}
                self.battlestate["stunned"][challenger_id] = stun_duration
                self.logger.log_stun(pet1["name"], stun_duration - 1)
                
            if priority == pet1:
                if move_opponent.get("skilltype") != "Dodge":
                    self.battlestate["hp"][opponent_id] -= dmg1
                    self.logger.log_attack(pet1["name"], pet2["name"], move_challenger["name"], dmg1)
                else:
                    self.logger.log_dodge(pet2["name"])
                    
                if self.battlestate["hp"][opponent_id] <= 0:
                    return await self.battle_end(pet1, pet2, self.challenger)
                    
                if move_challenger.get("skilltype") != "Dodge":
                    self.battlestate["hp"][challenger_id] -= dmg2
                    self.logger.log_attack(pet2["name"], pet1["name"], move_opponent["name"], dmg2)
                else:
                    self.logger.log_dodge(pet1["name"])
            else:
                if move_challenger.get("skilltype") != "Dodge":
                    self.battlestate["hp"][challenger_id] -= dmg2
                    self.logger.log_attack(pet2["name"], pet1["name"], move_opponent["name"], dmg2)
                else:
                    self.logger.log_dodge(pet1["name"])
                    
                if self.battlestate["hp"][challenger_id] <= 0:
                    return await self.battle_end(pet2, pet1, self.boss)
                    
                if move_opponent.get("skilltype") != "Dodge":
                    self.battlestate["hp"][opponent_id] -= dmg1
                    self.logger.log_attack(pet1["name"], pet2["name"], move_challenger["name"], dmg1)
                else:
                    self.logger.log_dodge(pet2["name"])
                    
            if self.battlestate["hp"][opponent_id] <= 0:
                return await self.battle_end(pet1, pet2, self.challenger)
            if self.battlestate["hp"][challenger_id] <= 0:
                return await self.battle_end(pet2, pet1, self.boss)
                
            self.generate_battle_image(pet1, pet2)
            file = discord.File(self.output_path, filename="battle.png")
            image_embed = discord.Embed(title=f"⚔ Battle: {pet1['name']} vs {pet2['name']}")
            image_embed.set_image(url="attachment://battle.png")
            
            recent_log = self.logger.get_log(5) 
            log_text = "\n".join(recent_log)
            
            status_text = (
                f"**Turn {turn}**\n\n"
                f"🟢 **{pet1['name']}**\n"
                f"HP: {max(0, math.floor(self.battlestate['hp'][challenger_id]))}/{pet1['base_hp']} | ATK Buff: {self.battlestate['buffs'][challenger_id]['attack']['value']} | DEF Buff: {self.battlestate['buffs'][challenger_id]['defense']['value']}\n"
                f"DEF Buff: {self.battlestate['buffs'][challenger_id]['defense']['value']}\n"
                f"Last Move: `{move_challenger['name']}`\n\n"
                f"🔵 **{pet2['name']}**\n"
                f"HP: {max(0, math.floor(self.battlestate['hp'][opponent_id]))}/{pet2['base_hp']} | ATK Buff: {self.battlestate['buffs'][opponent_id]['attack']['value']} | DEF Buff: {self.battlestate['buffs'][opponent_id]['defense']['value']}\n"
                f"Last Move: `{move_opponent['name']}`\n\n"
                f"**Battle Log:**\n{log_text}"
            )
            
            detail_embed = discord.Embed(title=f"Turn {turn}", description=status_text, color=discord.Color.green())
            await message.channel.send(file=file, embeds=[image_embed, detail_embed])
            
            turn += 1
        
    async def battle_end(self, winner_pet, loser_pet, winner_entity):
        self.winner = winner_entity
        self.logger.add_entry(f"🏆 **{winner_pet['name']}** has won the battle!")
        
        self.generate_battle_image(self.challenger_pet, self.boss)
        file = discord.File(self.output_path, filename="battle.png")
        image_embed = discord.Embed(title=f"⚔ Battle: {self.challenger_pet['name']} vs {self.boss['name']}")
        image_embed.set_image(url="attachment://battle.png")
        
        battle_summary = discord.Embed(title="Battle Summary", color=discord.Color.gold())
        battle_summary.description = "\n".join(self.logger.get_log(10))  # Show the last 10 log entries
        
        await self.message.channel.send(file=file, embeds=[image_embed, battle_summary])
    
        try:
            os.remove(self.output_path)
        except:
            pass
            
        return winner_entity

    async def run(self, message, args, client):
        self.message = message
        person = message.author.id
        self.challenger = client.usersCollection.find_one({"_id": person})
        self.output_path = f"PICTURES/battle_preview{self.challenger['_id']}.png"
        
        visiting_guild = self.challenger.get("visitingGuild")
        if not visiting_guild or visiting_guild not in bosses:
            return await message.channel.send(embed=discord.Embed(description="Coming Soon!"))
        
        self.boss = bosses[visiting_guild]
        self.skillList = self.boss["moves"]
        self.challenger_pet = None
        self.pets = self.challenger.get("pets", [])

        self.battlestate = {
            "hp": {
                self.challenger["_id"]: 0,  
                "boss": self.boss["base_hp"]
            },
            "buffs": {
                self.challenger["_id"]: {
                    "attack": {"value": 0, "nums": 0},
                    "defense": {"value": 0, "nums": 0},
                    "atkreduction": {"value": 0, "nums": 0},
                    "defreduction": {"value": 0, "nums": 0}
                },
                "boss": {
                    "attack": {"value": 0, "nums": 0},
                    "defense": {"value": 0, "nums": 0},
                    "atkreduction": {"value": 0, "nums": 0},
                    "defreduction": {"value": 0, "nums": 0}
                }
            },
            "ongoing_effects": {
                self.challenger["_id"]: [],
                "boss": []
            },
            "throttle": {
                "burst": {
                    "boss": 0,
                    self.challenger["_id"]: 0
                },
                "dodge": {
                    "boss": 0,
                    self.challenger["_id"]: 0
                }
            },
            "stunned": {
                "boss": 0,
                self.challenger["_id"]: 0
            }
        }
        
        self.winner = None
        self.logger.add_entry(f"🔥 Boss Battle against {self.boss['name']} has begun!")
        
        for attempt in range(1, 4):
            self.logger.add_entry(f"🏆 Attempt {attempt}/3")
            await self.prompt_pet_selection()
            
            if not self.challenger_pet:
                self.logger.add_entry("❌ No pet selected. Battle cancelled.")
                return
                
            self.battlestate["hp"][self.challenger["_id"]] = self.challenger_pet["base_hp"]
            self.battlestate["buffs"][self.challenger["_id"]] = {
                "attack": {"value": 0, "nums": 0},
                "defense": {"value": 0, "nums": 0},
                "atkreduction": {"value": 0, "nums": 0},
                "defreduction": {"value": 0, "nums": 0}
            }
            self.battlestate["ongoing_effects"][self.challenger["_id"]] = []
            self.battlestate["throttle"]["burst"][self.challenger["_id"]] = 0
            self.battlestate["throttle"]["dodge"][self.challenger["_id"]] = 0
            self.battlestate["stunned"][self.challenger["_id"]] = 0
            
            self.battlestate["buffs"]["boss"] = {
                "attack": {"value": 0, "nums": 0},
                "defense": {"value": 0, "nums": 0},
                "atkreduction": {"value": 0, "nums": 0},
                "defreduction": {"value": 0, "nums": 0}
            }

            
            await self.battling(message)
            
            if self.winner == self.challenger:
                self.logger.add_entry(f"🎉 Congratulations! You defeated {self.boss['name']} on attempt {attempt}!")
                return
                
            self.challenger_pet = None
            
        self.logger.add_entry(f"💔 You've used all 3 attempts and failed to defeat {self.boss['name']}. Better luck next time!")
        
        try:
            os.remove(self.output_path)
        except:
            pass
            
        return