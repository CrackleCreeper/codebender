from Structures.Message import Message
import discord
from Commands.Currency.Shop import shop_data_earth, shop_data_fire, shop_data_air, shop_data_water
import asyncio
import json
with open("./Structures/Skills.json", "r") as f:
    skills = json.load(f)
fired = {
    "Rare": [
        {"name": "Deco1", "price": 20, "itemID": 'FD1'},
        {"name": "Smokescreen", "price": 50, "itemID": 'FS1'},
        {"name": "Komodo Rhino", "price": 40, "itemID": 'FP1'}
    ],
    "Epic": [
        {"name": "Deco2", "price": 100, "itemID": 'FD2'},
        {"name": "Floor Is Lava", "price": 250, "itemID": 'FS2'},
        {"name": "Phoenix", "price": 200, "itemID": 'FP2'}
    ],
    "Legendary": [
        {"name": "Deco3", "price": 1000, "itemID": 'FD3'},
        {"name": "Fireball", "price": 2000, "itemID": 'FS3'},
        {"name": "Dragon", "price": 1800, "itemID": 'FP3'}
    ]
}

waterd = {
    "Rare": [
        {"name": "Deco1", "price": 20, "itemID": 'WD1'},
        {"name": "Liquid Mirror", "price": 50, "itemID": 'WS1'},
        {"name": "Dolphin Piranha", "price": 40, "itemID": 'WP1'}
    ],
    "Epic": [
        {"name": "Deco2", "price": 100, "itemID": 'WD2'},
        {"name": "Freeze", "price": 250, "itemID": 'WS2'},
        {"name": "Tiger Shark", "price": 200, "itemID": 'WP2'}
    ],
    "Legendary": [
        {"name": "Deco3", "price": 1000, "itemID": 'WD3'},
        {"name": "Holy Water", "price": 2000, "itemID": 'WS3'},
        {"name": "Kraken", "price": 1800, "itemID": 'WP3'}
    ]
}

aird = {
    "Rare": [
        {"name": "Deco1", "price": 20, "itemID": 'AD1'},
        {"name": "Aircutter", "price": 50, "itemID": 'AS1'},
        {"name": "Ring -Tailed Winged Lemur", "price": 40, "itemID": 'AP1'}
    ],
    "Epic": [
        {"name": "Deco2", "price": 100, "itemID": 'AD2'},
        {"name": "Gale Strike", "price": 250, "itemID": 'AS2'},
        {"name": "Spider Bat", "price": 200, "itemID": 'AP2'}
    ],
    "Legendary": [
        {"name": "Deco3", "price": 1000, "itemID": 'AD3'},
        {"name": "Whirlwind", "price": 2000, "itemID": 'AS3'},
        {"name": "Flying Bison", "price": 1800, "itemID": 'AP3'}
    ]
}

earthd = {
    "Rare": [
        {"name": "Deco1", "price": 20, "itemID": 'ED1'},
        {"name": "Photosynthesis", "price": 50, "itemID": 'ES1'},
        {"name": "Eel Sand Shark", "price": 40, "itemID": 'EP1'}
    ],
    "Epic": [
        {"name": "Deco2", "price": 100, "itemID": 'ED2'},
        {"name": "Earthquake", "price": 250, "itemID": 'ES2'},
        {"name": "Spider Snake", "price": 200, "itemID": 'EP2'}
    ],
    "Legendary": [
        {"name": "Deco3", "price": 1000, "itemID": 'ED3'},
        {"name": "Earthen Wall", "price": 2000, "itemID": 'ES3'},
        {"name": "Shirshu", "price": 1800, "itemID": 'EP3'}
    ]
}

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
        self.number_args = 1
        self.category = "Currency"
        self.user_permissions = []

    def find_price_by_itemID(self, itemID):
        shop_data = {
            'fire': fired,
            'water': waterd,
            'air': aird,
            'earth': earthd
        }

        for element, data in shop_data.items():
            for tier, items in data.items():
                for item in items:
                    if item['itemID'] == itemID:
                        return item['price']

        return None

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
            if item_id not in skill_map:
                return await message.channel.send(embed=Message(description="Skill ID not valid."))

            skill, move_name = skill_map[item_id]
            cost = self.find_price_by_itemID(item_id)
            user_pet = next(
                    (obj for obj in userData["pets"] if obj["name"].lower().strip() == pet_name.lower().strip()), None)
            l = list()
            for moves in user_pet["moves"]:
                l.append(moves["name"])

            
            if userData["money"] < cost:
                return await message.channel.send(embed=Message(description="You don't have enough money to buy this skill."))

            # Ask user which skill to replace
            await message.channel.send(embed=Message(description=f"Which skill would you like to replace on {pet_name}? Please type the skill's name."))

            await message.channel.send(embed=Message(description=f"Your pet has the following moves: \n {", ".join(l)}"))
            def check(m):
                return m.author == message.author and isinstance(m.channel, discord.TextChannel)

            try:
                move_to_replace_msg = await client.wait_for('message', timeout=60.0, check=check)

                move_to_replace = move_to_replace_msg.content.strip()

                

                if user_pet is None:
                    return await message.channel.send(embed=Message(description=f"No pet named {pet_name} found."))

                if not user_pet.get('moves'):
                    return await message.channel.send(embed=Message(description=f"{pet_name} has no moves to replace."))

                if not any(m['name'].lower() == move_to_replace.lower() for m in user_pet['moves']):
                    return await message.channel.send(
                        embed=Message(description=f"{move_to_replace} not found on {user_pet['name']}."))

                # Remove the old move
                client.usersCollection.update_one(
                    {"_id": message.author.id, "pets.name": user_pet['name']},
                    {
                        "$pull": {"pets.$.moves": {"name": move_to_replace}}  # Remove the old move
                    }
                )

                # Add the new skill to the pet and deduct money
                client.usersCollection.update_one(
                    {"_id": message.author.id, "pets.name": user_pet['name']},
                    {
                        "$push": {"pets.$.moves": skill}  # Add the new skill
                    }
                )

                # Deduct the cost only once after the transaction is confirmed
                client.usersCollection.update_one(
                    {"_id": message.author.id},
                    {
                        "$inc": {"money": -cost}  # Deduct the cost
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
                'fire': fired,
                'water': waterd,
                'air': aird,
                'earth': earthd
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
            already_has_pet = next((i for i in userData["pets"] if i['name'] == pet_data["name"]), None)

            def check(m):
                return m.author == message.author and m.channel == message.channel
            if already_has_pet:
                await message.channel.send(embed=Message(description=f"You already have {pet_data['name']}!, hence enter a name to rename the new pet."))
                try:
                    msg = await client.wait_for('message', timeout=60.0, check=check)
                    pet_data["name"] = msg.content
                except asyncio.TimeoutError:
                    return await message.channel.send(embed=Message(description="You took too long."))

            # Add the new pet to the user's collection and deduct money
            client.usersCollection.update_one(
                {"_id": message.author.id},
                {
                    "$push": {"pets": pet_data}  # Add the new pet
                }
            )

            # Deduct the cost of the pet purchase
            client.usersCollection.update_one(
                {"_id": message.author.id},
                {
                    "$inc": {"money": -cost}  # Deduct the cost once
                }
            )

            return await message.channel.send(embed=Message(description=f"Successfully purchased {pet_data['name']}!"))
