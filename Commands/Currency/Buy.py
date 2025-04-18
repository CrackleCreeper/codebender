from Structures.Message import Message
import discord
from discord.ui import View, Button
from Commands.Currency.Shop import shop_data_earth, shop_data_fire, shop_data_air, shop_data_water

fire_moves = {
    "Floor Is Lava": {"name": "Floor Is Lava", "type": "Fire", "power": 0},  # FS2
    "Fireball": {"name": "Fireball", "type": "Fire", "power": 25},  # FS3
    "Smokescreen": {"name": "Smokescreen", "type": "Fire", "power": 0}  # FS1
}

water_moves = {
    "Freeze": {"name": "Freeze", "type": "Water", "power": 0}, # WS2
    "Liquid Mirror": {"name": "Liquid Mirror", "type": "Water", "power": 0}, # WS1
    "Holy Water": {"name": "Holy Water", "type": "Water","power":0} # WS3
}

air_moves = {
    "Whirlwind": {"name": "Whirlwind", "type": "Air", "power": 25}, # AS3
    "Aircutter": {"name": "Aircutter", "type": "Air", "power": 15}, # AS1
    "Gale Strike": {"name": "Gale Strike", "type": "Air","power":0} # AS2
}

earth_moves = {
    "Photosynthesis": {"name": "Photosynthesis", "type": "Earth", "power": 0}, # ES1
    "Earthquake": {"name": "Earthquake", "type": "Earth", "power": 15},  # ES2
    "Earthen Wall": {"name": "Earthen Wall", "type": "Earth", "power": 0} # ES3
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
        self.number_args = 2
        self.category = "Currency"
        self.user_permissions = []

    async def run(self, message, args, client):
        itemIDS = ["FD1", "FS1", "FP1", "WD1", "WS1", "WP1", "AD1", "AS1", "AP1", "ED1", "ES1", "EP1"]
        userData = client.usersCollection.find_one({"_id": message.author.id})
        user = userData
        if userData is None:
            return await message.channel.send(embed=Message(description="Use !join to join a guild before doing anything else."))
        
        if args[0] not in itemIDS:
            return await message.channel.send(embed=Message(description="Enter a valid ID"))

        # Identifying the cost and move to push based on the ID
        if args[0] == "FS2":
            cost = shop_data_fire["Epic"][0]["price"]
            move = all_moves["Smokescreen"]
        elif args[0] == "FS1":
            cost = shop_data_fire["Rare"][0]["price"]
            move = all_moves["Fireball"]
        elif args[0] == "FS3":
            cost = shop_data_fire["Legendary"][0]["price"]
            move = all_moves["Floor Is Lava"]
        elif args[0] == "WS2":
            cost = shop_data_water["Epic"][0]["price"]
            move = all_moves["Freeze"]
        elif args[0] == "WS1":
            cost = shop_data_water["Rare"][0]["price"]
            move = all_moves["Liquid Mirror"]
        elif args[0] == "WS3":
            cost = shop_data_water["Legendary"][0]["price"]
            move = all_moves["Holy Water"]
        elif args[0] == "AS2":
            cost = shop_data_air["Epic"][0]["price"]
            move = all_moves["Whirlwind"]
        elif args[0] == "AS1":
            cost = shop_data_air["Rare"][0]["price"]
            move = all_moves["Aircutter"]
        elif args[0] == "AS3":
            cost = shop_data_air["Legendary"][0]["price"]
            move = all_moves["Gale Strike"]
        elif args[0] == "ES2":
            cost = shop_data_earth["Epic"][0]["price"]
            move = all_moves["Photosynthesis"]
        elif args[0] == "ES1":
            cost = shop_data_earth["Rare"][0]["price"]
            move = all_moves["Earthen Wall"]
        elif args[0] == "ES3":
            cost = shop_data_earth["Legendary"][0]["price"]
            move = all_moves["Earthquake"]

        # Verifying if the user has enough money and the pet exists
        if len(args) < 2:
            return await message.channel.send(embed=Message(description="Enter a valid pet name to add this skill to."))
        
        pet_name = args[1]
        item = next((obj for obj in userData["pets"] if obj["name"] == pet_name), None)
        if item is None:
            return await message.channel.send(embed=Message(description="No pet with that name found, or you don't own that pet."))

        if userData["money"] < cost:
            return await message.channel.send(embed=Message(description="You don't have enough money to buy this skill."))

        # Update database: add skill to pet and deduct money
        client.usersCollection.update_one(
            {"_id": message.author.id, "pets.name": pet_name},  # Find the user and pet by name
            {
                "$push": {"pets.$.moves": move},  # Push skill to the correct pet
                "$inc": {"money": -cost}  # Deduct money
            }
        )

        return await message.channel.send(embed=Message(description=f"Successfully added {move['name']} to {item['name']}!"))


# from Structures.Message import Message
# import discord
# from discord.ui import View, Button
# from Commands.Currency.Shop import shop_data_earth, shop_data_fire, shop_data_air, shop_data_water

# # Assuming pets_data is imported or defined as per your pets.json
# pets_data = {
#     "fire": [
#         # ... (Fire pets data as provided)
#     ],
#     "water": [
#         # ... (Water pets data as provided)
#     ],
#     "air": [
#         # ... (Air pets data as provided)
#     ],
#     "earth": [
#         # ... (Earth pets data as provided)
#     ]
# }

# # ... (existing moves data and all_moves)

# class Buy:
#     def __init__(self):
#         self.name = "buy"
#         self.description = "Buy something from your guild shop."
#         self.number_args = 2  # Adjust based on pet/skill handling
#         self.category = "Currency"
#         self.user_permissions = []

#     async def run(self, message, args, client):
#         itemIDS = [
#             "FD1", "FS1", "FP1", "WD1", "WS1", "WP1", "AD1", "AS1", "AP1", "ED1", "ES1", "EP1",
#             "FD2", "FS2", "FP2", "WD2", "WS2", "WP2", "AD2", "AS2", "AP2", "ED2", "ES2", "EP2",
#             "FD3", "FS3", "FP3", "WD3", "WS3", "WP3", "AD3", "AS3", "AP3", "ED3", "ES3", "EP3"
#         ]
#         userData = client.usersCollection.find_one({"_id": message.author.id})
#         if userData is None:
#             return await message.channel.send(embed=Message(description="Use !join to join a guild before doing anything else."))
        
#         if len(args) < 1:
#             return await message.channel.send(embed=Message(description="Please provide an item ID."))
        
#         item_id = args[0]
#         if item_id not in itemIDS:
#             return await message.channel.send(embed=Message(description="Enter a valid ID"))
        
#         # Determine if it's a pet (P) or skill (S/D)
#         is_pet = len(item_id) >= 2 and item_id[1].upper() == 'P'
        
#         if is_pet:
#             # Handle pet purchase
#             if len(args) != 1:
#                 return await message.channel.send(embed=Message(description="Pet purchase requires only the item ID."))
            
#             # Parse element and tier from item_id
#             element_code = item_id[0].upper()
#             tier_number = item_id[2]
#             element_map = {'F': 'fire', 'W': 'water', 'A': 'air', 'E': 'earth'}
#             tier_map = {'1': 'Rare', '2': 'Epic', '3': 'Legendary'}
            
#             if element_code not in element_map or tier_number not in tier_map:
#                 return await message.channel.send(embed=Message(description="Invalid item ID."))
            
#             element = element_map[element_code]
#             tier = tier_map[tier_number]
            
#             # Get the correct shop data
#             shop_data = None
#             if element == 'fire':
#                 shop_data = shop_data_fire
#             elif element == 'water':
#                 shop_data = shop_data_water
#             elif element == 'air':
#                 shop_data = shop_data_air
#             elif element == 'earth':
#                 shop_data = shop_data_earth
            
#             # Find the item in shop_data
#             shop_items = shop_data.get(tier, [])
#             item = next((i for i in shop_items if i['itemID'] == item_id), None)
#             if not item:
#                 return await message.channel.send(embed=Message(description="Item not found in shop."))
            
#             cost = item['price']
#             pet_name = item['name']
            
#             # Find the pet in pets_data
#             pets_list = pets_data.get(element, [])
#             pet = next((p for p in pets_list if p['name'] == pet_name), None)
#             if not pet:
#                 return await message.channel.send(embed=Message(description="Pet data not found."))
            
#             # Check user's money
#             if userData['money'] < cost:
#                 return await message.channel.send(embed=Message(description="You don't have enough money."))
            
#             # Add pet to user's pets and deduct cost
#             client.usersCollection.update_one(
#                 {"_id": message.author.id},
#                 {
#                     "$push": {"pets": pet},
#                     "$inc": {"money": -cost}
#                 }
#             )
#             return await message.channel.send(embed=Message(description=f"Successfully purchased {pet['name']}!"))
        
#         else:
#             # Existing code for handling skills (FS, WS, etc.)
#             # ... (existing skill purchase code)
            
#             # Note: Ensure to fix indices in skill handling as they may be incorrect
#             # Example correction for FS2:
#             # elif args[0] == "FS2":
#             #     for item in shop_data_fire["Epic"]:
#             #         if item["itemID"] == "FS2":
#             #             cost = item["price"]
#             #             move = all_moves[item["name"]]
#             #             break
            
#             # ... (rest of the skill handling code)