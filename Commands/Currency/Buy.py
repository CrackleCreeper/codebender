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

# # Pets data (import this properly from your JSON file in actual implementation)
# pets_data = {
#     "fire": [
#         # ... (paste all fire pets data here)
#     ],
#     "water": [
#         # ... (paste all water pets data here)
#     ],
#     "air": [
#         # ... (paste all air pets data here)
#     ],
#     "earth": [
#         # ... (paste all earth pets data here)
#     ]
# }

# # Existing moves data
# fire_moves = { 
#     # ... (keep existing fire moves)
# }
# water_moves = {
#     # ... (keep existing water moves)
# }
# air_moves = {
#     # ... (keep existing air moves)
# }
# earth_moves = {
#     # ... (keep existing earth moves)
# }

# all_moves = {**fire_moves, **water_moves, **air_moves, **earth_moves}

# class Buy:
#     def __init__(self):
#         self.name = "buy"
#         self.description = "Buy something from your guild shop."
#         self.number_args = 1  # Will handle dynamically in code
#         self.category = "Currency"
#         self.user_permissions = []

#     async def run(self, message, args, client):
#         user_id = message.author.id
#         user_data = client.usersCollection.find_one({"_id": user_id})
        
#         if not user_data:
#             return await message.channel.send(embed=Message(description="Use !join to join a guild first."))
        
#         if not args:
#             return await message.channel.send(embed=Message(description="Please provide an item ID."))
        
#         item_id = args[0].upper()
#         is_pet = item_id[1] == 'P' if len(item_id) >= 2 else False

#         # Handle Pet Purchase
#         if is_pet:
#             return await self.handle_pet_purchase(message, item_id, user_data, client)
        
#         # Handle Skill/Decoration Purchase
#         return await self.handle_skill_purchase(message, args, item_id, user_data, client)

#     async def handle_pet_purchase(self, message, item_id, user_data, client):
#         # Validate item structure
#         if len(item_id) != 3 or item_id[1] != 'P':
#             return await message.channel.send(embed=Message(description="Invalid pet item ID."))

#         # Parse item ID components
#         element_code = item_id[0]
#         tier_number = item_id[2]
        
#         element_map = {'F': 'fire', 'W': 'water', 'A': 'air', 'E': 'earth'}
#         tier_map = {'1': 'Rare', '2': 'Epic', '3': 'Legendary'}
        
#         element = element_map.get(element_code)
#         tier = tier_map.get(tier_number)
        
#         if not element or not tier:
#             return await message.channel.send(embed=Message(description="Invalid item ID format."))

#         # Get shop data
#         shop_data = {
#             'fire': shop_data_fire,
#             'water': shop_data_water,
#             'air': shop_data_air,
#             'earth': shop_data_earth
#         }.get(element)

#         if not shop_data:
#             return await message.channel.send(embed=Message(description="Invalid guild shop."))

#         # Find shop item
#         shop_item = next(
#             (item for tier_items in shop_data[tier] 
#              for item in tier_items if item['itemID'] == item_id),
#             None
#         )
        
#         if not shop_item:
#             return await message.channel.send(embed=Message(description="Item not found in shop."))

#         # Find pet data
#         pet_name = shop_item['name']
#         pet_data = next(
#             (pet for pet in pets_data[element] 
#              if pet['name'] == pet_name),
#             None
#         )
        
#         if not pet_data:
#             return await message.channel.send(embed=Message(description="Pet data not found."))

#         # Check funds
#         if user_data['money'] < shop_item['price']:
#             return await message.channel.send(embed=Message(description="Insufficient funds."))

#         # Check if pet already owned
#         if any(p['name'] == pet_name for p in user_data.get('pets', [])):
#             return await message.channel.send(embed=Message(description="You already own this pet."))

#         # Update database
#         client.usersCollection.update_one(
#             {"_id": user_id},
#             {
#                 "$push": {"pets": pet_data},
#                 "$inc": {"money": -shop_item['price']}
#             }
#         )
#         return await message.channel.send(embed=Message(description=f"Purchased {pet_name}!"))

#     async def handle_skill_purchase(self, message, args, item_id, user_data, client):
#         if len(args) < 2:
#             return await message.channel.send(embed=Message(description="Please provide a pet name."))
        
#         # Determine element from item ID
#         element_map = {'F': 'fire', 'W': 'water', 'A': 'air', 'E': 'earth'}
#         element = element_map.get(item_id[0])
#         if not element:
#             return await message.channel.send(embed=Message(description="Invalid item ID."))

#         # Get correct shop data
#         shop_data = {
#             'fire': shop_data_fire,
#             'water': shop_data_water,
#             'air': shop_data_air,
#             'earth': shop_data_earth
#         }[element]

#         # Find item in shop data
#         shop_item = None
#         for tier in ["Rare", "Epic", "Legendary"]:
#             for item in shop_data.get(tier, []):
#                 if item['itemID'] == item_id:
#                     shop_item = item
#                     break
#             if shop_item:
#                 break
        
#         if not shop_item:
#             return await message.channel.send(embed=Message(description="Item not found in shop."))

#         # Check funds
#         if user_data['money'] < shop_item['price']:
#             return await message.channel.send(embed=Message(description="Insufficient funds."))

#         # Get move data
#         move_name = shop_item['name']
#         move_data = all_moves.get(move_name)
#         if not move_data:
#             return await message.channel.send(embed=Message(description="Skill data not found."))

#         # Find target pet
#         pet_name = args[1]
#         target_pet = next(
#             (pet for pet in user_data.get('pets', []) 
#              if pet['name'].lower() == pet_name.lower()),
#             None
#         )
        
#         if not target_pet:
#             return await message.channel.send(embed=Message(description="Pet not found."))

#         # Update database
#         client.usersCollection.update_one(
#             {"_id": user_id, "pets.name": target_pet['name']},
#             {
#                 "$push": {"pets.$.moves": move_data},
#                 "$inc": {"money": -shop_item['price']}
#             }
#         )
#         return await message.channel.send(
#             embed=Message(description=f"Added {move_name} to {target_pet['name']}!")
#         )