from Structures.Message import Message
import discord
from discord.ui import View, Button
from Commands.Currency.Shop import shop_data_earth, shop_data_fire, shop_data_air, shop_data_water

fire_moves = {
    "Floor Is Lava": {"name": "Floor Is Lava", "type": "Fire", "power": 0},
    "Fireball": {"name": "Fireball", "type": "Fire", "power": 25},
    "Smokescreen": {"name": "Smokescreen", "type": "Fire", "power": 0}
}

water_moves = {
    "Freeze": {"name": "Freeze", "type": "Water", "power": 0},
    "Liquid Mirror": {"name": "Liquid Mirror", "type": "Water", "power": 0},
    "Holy Water": {"name": "Holy Water", "type": "Water", "power": 0}
}

air_moves = {
    "Whirlwind": {"name": "Whirlwind", "type": "Air", "power": 25},
    "Aircutter": {"name": "Aircutter", "type": "Air", "power": 15},
    "Gale Strike": {"name": "Gale Strike", "type": "Air", "power": 0}
}

earth_moves = {
    "Photosynthesis": {"name": "Photosynthesis", "type": "Earth", "power": 0},
    "Earthquake": {"name": "Earthquake", "type": "Earth", "power": 15},
    "Earthen Wall": {"name": "Earthen Wall", "type": "Earth", "power": 0}
}

all_moves = {
    **fire_moves,
    **water_moves,
    **air_moves,
    **earth_moves
}

class Buy:
    def __init__(self):
        self.name = "buy"
        self.description = "Buy something from your guild shop."
        self.number_args = 1
        self.category = "Currency"
        self.user_permissions = []

    async def run(self, message, args, client):
        itemIDS = [
            "FD1", "FS1", "FP1", "WD1", "WS1", "WP1", "AD1", "AS1", "AP1", "ED1", "ES1", "EP1",
            "FD2", "FS2", "FP2", "WD2", "WS2", "WP2", "AD2", "AS2", "AP2", "ED2", "ES2", "EP2",
            "FD3", "FS3", "FP3", "WD3", "WS3", "WP3", "AD3", "AS3", "AP3", "ED3", "ES3", "EP3"
        ]

        userData = client.usersCollection.find_one({"_id": message.author.id})
        if userData is None:
            return await message.channel.send(embed=Message(description="Use !join to join a guild before doing anything else."))

        if len(args) < 1:
            return await message.channel.send(embed=Message(description="Please provide an item ID."))

        item_id = args[0]
        if item_id not in itemIDS:
            return await message.channel.send(embed=Message(description="Enter a valid ID"))

        is_pet = len(item_id) >= 2 and item_id[1].upper() == 'P'

        if is_pet:
            element_code = item_id[0].upper()
            tier_number = item_id[2]
            element_map = {'F': 'fire', 'W': 'water', 'A': 'air', 'E': 'earth'}
            tier_map = {'1': 'Rare', '2': 'Epic', '3': 'Legendary'}

            if element_code not in element_map or tier_number not in tier_map:
                return await message.channel.send(embed=Message(description="Invalid item ID."))

            element = element_map[element_code]
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

            client.usersCollection.update_one(
                {"_id": message.author.id},
                {
                    "$push": {"pets": pet_data},
                    "$inc": {"money": -cost}
                }
            )
            return await message.channel.send(embed=Message(description=f"Successfully purchased {pet_data['name']}!"))

        if len(args) < 2:
            return await message.channel.send(embed=Message(description="Enter a valid pet name to add this skill to."))

        skill_map = {
            "FS1": (shop_data_fire["Rare"], "Fireball"),
            "FS2": (shop_data_fire["Epic"], "Smokescreen"),
            "FS3": (shop_data_fire["Legendary"], "Floor Is Lava"),
            "WS1": (shop_data_water["Rare"], "Liquid Mirror"),
            "WS2": (shop_data_water["Epic"], "Freeze"),
            "WS3": (shop_data_water["Legendary"], "Holy Water"),
            "AS1": (shop_data_air["Rare"], "Aircutter"),
            "AS2": (shop_data_air["Epic"], "Whirlwind"),
            "AS3": (shop_data_air["Legendary"], "Gale Strike"),
            "ES1": (shop_data_earth["Rare"], "Earthen Wall"),
            "ES2": (shop_data_earth["Epic"], "Photosynthesis"),
            "ES3": (shop_data_earth["Legendary"], "Earthquake")
        }

        if item_id not in skill_map:
            return await message.channel.send(embed=Message(description="Skill ID not valid."))

        shop_items, move_name = skill_map[item_id]
        item = next((i for i in shop_items if i['itemID'] == item_id), None)
        if not item:
            return await message.channel.send(embed=Message(description="Skill not found in shop."))

        cost = item['price']
        move = all_moves[move_name]
        pet_name = args[1]
        user_pet = next((obj for obj in userData["pets"] if obj["name"].lower() == pet_name.lower()), None)
        if user_pet is None:
            return await message.channel.send(embed=Message(description="No pet with that name found, or you don't own that pet."))

        if userData["money"] < cost:
            return await message.channel.send(embed=Message(description="You don't have enough money to buy this skill."))

        client.usersCollection.update_one(
            {"_id": message.author.id, "pets.name": user_pet['name']},
            {
                "$push": {"pets.$.moves": move},
                "$inc": {"money": -cost}
            }
        )

        return await message.channel.send(embed=Message(description=f"Successfully added {move['name']} to {user_pet['name']}!"))
