from Structures.Message import Message
import discord
from Commands.Currency.Shop import shop_data_earth, shop_data_fire, shop_data_air, shop_data_water
import asyncio
import json
with open("./Structures/Skills.json", "r") as f:
    skills = json.load(f)
# Fire moves, water moves, air moves, and earth moves as per your provided data
fire_moves = {
    "Floor Is Lava": {"name": "Floor Is Lava",
            "skilltype": "Attack",
            "atktype": "Burst",
            "description": "Turns the floor to lava, which causes some damage every time the opponent attacks while heating up the user's attacks",
            "power": 5,
            "defreduction": 0,
            "defbuff": 0,
            "atkbuff": 3,
            "atkreduction": 0,
            "heal": 0,
            "dodge": False,
            "numInstances": 100,
            "skipNextTurn": False},
    "Fireball": {"name": "Fireball",
            "skilltype": "Attack",
            "atktype": "Burst",
            "description": "Throws a fireball at the enemy, dealing massive damage while igniting inner flames that enhance attack power",
            "power": 20,
            "defreduction": 0,
            "defbuff": 0,
            "atkbuff": 7,
            "atkreduction": 0,
            "heal": 0,
            "dodge": False,
            "numInstances": 1,
            "skipNextTurn": False},
    "Smokescreen": {"name": "Smokescreen",
            "skilltype": "Defense",
            "atktype": "Basic",
            "description": "Creates a smoke screen that has a chance of dodging next 2 incoming attacks, increases defense, and reduces enemy accuracy and attack power",
            "power": 0,
            "defreduction": 0,
            "defbuff": 7,
            "atkbuff": 0,
            "atkreduction": 5,
            "heal": 0,
            "dodge": False,
            "numInstances": 2,
            "skipNextTurn": False}
}

water_moves = {
    "Freeze": { "name": "Freeze",
            "skilltype": "Stun",
            "atktype": "Burst",
            "description": "Freezes the opponent for two turns, reducing their defense",
            "power": 16,
            "defreduction": 7,
            "defbuff": 0,
            "atkbuff": 0,
            "atkreduction": 6,
            "heal": 0,
            "dodge": False,
            "numInstances": 2,
            "skipNextTurn": True},
    "Liquid Mirror": {"name": "Liquid Mirror",
            "skilltype": "Attack",
            "atktype": "Basic",
            "description": "Generates a liquid mirror that reflects a portion of incoming damage for one turn",
            "power": 16,
            "defreduction": 0,
            "defbuff": 0,
            "atkbuff": 0,
            "atkreduction": 6,
            "heal": 0,
            "dodge": False,
            "numInstances": 1,
            "skipNextTurn": False},
    "Holy Water": { "name": "Holy Water",
            "skilltype": "Heal",
            "atktype": "Burst",
            "description": "Pet takes damage for two turns, and on the third, regains full HP",
            "power": -10,
            "defreduction": 0,
            "defbuff": 0,
            "atkbuff": 0,
            "atkreduction": 0,
            "heal": 100,
            "dodge": False,
            "numInstances": 3,
            "skipNextTurn": False}
}

air_moves = {
    "Whirlwind Maelstorm": { "name": "Whirlwind Maelstorm",
            "skilltype": "Stun",
            "atktype": "Burst",
            "description": "The pet uses a whirlwind to attack the opponent, dealing damage, and knocking them over. Stuns the opponent for one turn",
            "power": 20,
            "defreduction": 0,
            "defbuff": 0,
            "atkbuff": 0,
            "atkreduction": 0,
            "heal": 0,
            "dodge": False,
            "numInstances": 1,
            "skipNextTurn": True},
    "Aircutter": { "name": "Aircutter",
            "skilltype": "Attack",
            "atktype": "Burst",
            "description": "The pet cuts the opponent's armour by a small portion every turn",
            "power": 0,
            "defreduction": 3,
            "defbuff": 7,
            "atkbuff": 0,
            "atkreduction": 0,
            "heal": 0,
            "dodge": False,
            "numInstances": 100,
            "skipNextTurn": False},
    "Wind Shield": { "name": "Wind Shield",
            "skilltype": "Stun",
            "atktype": "Basic",
            "description": "The pet creates an armour of wind, and regenerates a small portion of its HP",
            "power": 0,
            "defreduction": 0,
            "defbuff": 15,
            "atkbuff": 0,
            "atkreduction": 0,
            "heal": 5,
            "dodge": False,
            "numInstances": 1,
            "skipNextTurn": True}
}

earth_moves = {
    "Photosynthesis": { "name": "Photosynthesis",
            "skilltype": "Heal",
            "atktype": "Burst",
            "description": "Regains HP equal to 100% of the pet's defense stat",
            "power": 0,
            "defreduction": 0,
            "defbuff": 10,
            "atkbuff": 0,
            "atkreduction": 8,
            "heal": 0,
            "dodge": False,
            "numInstances": 3,
            "skipNextTurn": False},
    "Earthquake": { "name": "Earthen Wall",
            "skilltype": "Attack",
            "atktype": "Burst",
            "description": "Creates a wall of earth that absorbs certain amount of damage for next 3 turns and releases it multiplied onto the opponent",
            "power": 18,
            "defreduction": 0,
            "defbuff": 10,
            "atkbuff": 0,
            "atkreduction": 8,
            "heal": 0,
            "dodge": False,
            "numInstances": 3,
            "skipNextTurn": False},
    "Earthen Wall": {"name": "Earthquake",
            "skilltype": "Attack",
            "atktype": "Burst",
            "description": "Creates an earthquake, that damages the attacker and the opponent- for every unit of damage the attacker takes, the defender takes more.",
            "power": 18,
            "defreduction": 0,
            "defbuff": 10,
            "atkbuff": 0,
            "atkreduction": 0,
            "heal": 0,
            "dodge": False,
            "numInstances": 5,
            "skipNextTurn": False}
}

# Map item IDs to corresponding moves
skill_map = {
    "FS3": (fire_moves["Fireball"], "Fireball"),
    "FS2": (fire_moves["Floor Is Lava"], "Floor Is Lava"),
    "FS1": (fire_moves["Smokescreen"], "Smokescreen"),
    "WS1": (water_moves["Liquid Mirror"], "Liquid Mirror"),
    "WS2": (water_moves["Freeze"], "Freeze"),
    "WS3": (water_moves["Holy Water"], "Holy Water"),
    "AS1": (air_moves["Aircutter"], "Aircutter"),
    "AS2": (air_moves["Whirlwind Maelstorm"], "Whirlwind Maelstorm"),
    "AS3": (air_moves["Wind Shield"], "Wind Shield"),
    "ES1": (earth_moves["Photosynthesis"], "Photosynthesis"),
    "ES2": (earth_moves["Earthquake"], "Earthquake"),
    "ES3": (earth_moves["Earthen Wall"], "Earthen Wall")
}

class Buy:
    def __init__(self):
        self.name = "buy"
        self.description = "Buy something from your guild shop. Use !buy <itemID> <petName> to buy a skill. Afterward, you will be prompted to replace an existing skill."
        self.number_args = 1  # Expecting 2 arguments (itemID and petName)
        self.category = "Currency"
        self.user_permissions = []

    async def run(self, message, args, client):
        itemIDS = [
            "FS1", "FS2", "FS3", "WS1", "WS2", "WS3", "AS1", "AS2", "AS3", "ES1", "ES2", "ES3"
        ]

        userData = client.usersCollection.find_one({"_id": message.author.id})
        if userData is None:
            return await message.channel.send(embed=Message(description="Use !join to join a guild before doing anything else."))
        if args[0] in itemIDS:
            if len(args) < 2:
                return await message.channel.send(embed=Message(description="Please provide an item ID and pet name."))

            item_id = args[0]
            pet_name = " ".join(args[1:])
            element_code = item_id[0].upper()
            tier_number = item_id[2]
            element_map = {'F': 'fire', 'W': 'water', 'A': 'air', 'E': 'earth'}
            tier_map = {'1': 'Rare', '2': 'Epic', '3': 'Legendary'}


            if element_code not in element_map or tier_number not in tier_map:
                return await message.channel.send(embed=Message(description="Invalid item ID."))

            element = element_map[element_code]

            if item_id not in itemIDS:
                return await message.channel.send(embed=Message(description="Enter a valid ID"))
            if not element.lower() == userData["visitingGuild"].lower():
                return await message.channel.send(embed=Message(description="You can only buy something from the guild you are visiting in."))
            # Check if item is a skill purchase
            if item_id not in skill_map:
                return await message.channel.send(embed=Message(description="Skill ID not valid."))

            # Fetch the skill and cost from the skill map
            skill, move_name = skill_map[item_id]
            cost = 100

            if userData["money"] < cost:
                return await message.channel.send(embed=Message(description="You don't have enough money to buy this skill."))

            client.usersCollection.update_one(
                {"_id": message.author.id},
                {
                    "$inc": {"money": -cost}
                }
            )

            # Ask user which move they want to replace
            await message.channel.send(embed=Message(description=f"Which skill would you like to replace on {pet_name}? Please type the skill's name."))

            def check(m):
                return m.author == message.author and isinstance(m.channel, discord.TextChannel)

            try:
                move_to_replace_msg = await client.wait_for('message', timeout=60.0, check=check)

                move_to_replace = move_to_replace_msg.content.strip()

                # Check if the move exists on the pet
                user_pet = next(
                    (obj for obj in userData["pets"] if obj["name"].lower().strip() == pet_name.lower().strip()), None)

                if user_pet is None:
                    return await message.channel.send(embed=Message(description=f"No pet named {pet_name} found."))

                # Ensure the pet has moves
                if not user_pet.get('moves'):
                    return await message.channel.send(embed=Message(description=f"{pet_name} has no moves to replace."))

                # Check if the move to replace exists in the pet's moves
                if not any(m['name'].lower() == move_to_replace.lower() for m in user_pet['moves']):
                    return await message.channel.send(
                        embed=Message(description=f"{move_to_replace} not found on {user_pet['name']}."))

                # Replace the move in the database
                client.usersCollection.update_one(
                    {"_id": message.author.id, "pets.name": user_pet['name']},
                    {
                        "$pull": {"pets.$.moves": {"name": move_to_replace}},  # Remove the old move
                        "$inc": {"money": -cost}  # Deduct the cost of the skill
                    }
                )
                client.usersCollection.update_one(
                    {"_id": message.author.id, "pets.name": user_pet['name']},
                    {
                        "$push": {"pets.$.moves": skill},  # Remove the old move
                        "$inc": {"money": -cost}  # Deduct the cost of the skill
                    }
                )

                return await message.channel.send(embed=Message(description=f"Successfully replaced {move_to_replace} with {skill['name']} on {user_pet['name']}!"))

            except asyncio.TimeoutError:
                return await message.channel.send(embed=Message(description="You took too long to respond. The move replacement has been cancelled."))
        else:
            if len(args) < 1:
                return await message.channel.send(embed=Message(description="Please provide an item ID."))
            item_id = args[0]
            element_code = item_id[0].upper()
            tier_number = item_id[2]
            element_map = {'F': 'fire', 'W': 'water', 'A': 'air', 'E': 'earth'}
            tier_map = {'1': 'Rare', '2': 'Epic', '3': 'Legendary'}

            if element_code not in element_map or tier_number not in tier_map:
                return await message.channel.send(embed=Message(description="Invalid item ID."))

            element = element_map[element_code]
            if not element.lower() == userData["visitingGuild"].lower():
                return await message.channel.send(embed=Message(description="You can only buy something from the guild you are visiting in."))
            tier = tier_map[tier_number]

            shop_data = {
                'fire': shop_data_fire,
                'water': shop_data_water,
                'air': shop_data_air,
                'earth': shop_data_earth
            }[element]


            shop_items = shop_data.get(tier, [])
            item = next((i for i in shop_items if i['itemID'] == item_id), None)
            if not item:
                return await message.channel.send(embed=Message(description="Item not found in shop."))

            cost = item['price']
            pet_data = next((p for p in client.pets_data[element] if p['name'] == item['name']), None)
            if not pet_data:
                return await message.channel.send(embed=Message(description="Pet data not found in pets.json."))

            if userData['money'] < cost:
                return await message.channel.send(embed=Message(description="You don't have enough money."))


            for i in range(3):
                move = pet_data["moves"][i]
                pet_data["moves"][i] = next(skill for skill in skills[element] if skill["name"] == move["name"])

            client.usersCollection.update_one(
                {"_id": message.author.id},
                {
                    "$push": {"pets": pet_data},
                    "$inc": {"money": -cost}
                }
            )
            return await message.channel.send(embed=Message(description=f"Successfully purchased {pet_data['name']}!"))