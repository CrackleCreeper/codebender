import random
import json
with open("./Structures/Pets.json", "r") as f:
    pets = json.load(f)
with open("./Structures/Skills.json", "r") as f:
    skills = json.load(f)
class User:
    def __init__(self, userID, client, money=100, level= 0, cosmetics = []):
        self.userID = userID
        self.money = money
        self.pets = []
        self.level = level
        self.is_sneaking = False
        self.cosmetics = cosmetics
        self.client = client

        guildNo = random.randint(1, 4)
        if guildNo == 1 : 
            self.homeGuild = "Earth"
        elif guildNo == 2 : 
            self.homeGuild = "Air"
        elif guildNo == 3 : 
            self.homeGuild = "Water"
        elif guildNo == 4 : 
            self.homeGuild = "Fire"

        if self.homeGuild == "Earth" : 
            pet = pets["earth"][0]
            for i in range(3):
                move = pet["moves"][i]
                pet["moves"][i] = next(skill for skill in skills[move["type"].lower()] if skill["name"] == move["name"])
            self.pets.append(pet)
        elif self.homeGuild == "Air" : 
            pet = pets["air"][0]
            for i in range(3):
                move = pet["moves"][i]
                pet["moves"][i] = next(skill for skill in skills[move["type"].lower()] if skill["name"] == move["name"])
            self.pets.append(pet)
        elif self.homeGuild == "Water" : 
            pet = pets["water"][0]
            for i in range(3):
                move = pet["moves"][i]
                pet["moves"][i] = next(skill for skill in skills[move["type"].lower()] if skill["name"] == move["name"])
            self.pets.append(pet)
        elif self.homeGuild == "Fire" : 
            pet = pets["fire"][0]
            for i in range(3):
                move = pet["moves"][i]
                pet["moves"][i] = next(skill for skill in skills[move["type"].lower()] if skill["name"] == move["name"])
            self.pets.append(pet)

        self.client.guildsCollection.update_one({"_id": self.homeGuild}, {"$push": {"members": self.userID}})
        self.visitingGuild = self.homeGuild
    def to_dict(self):
        return {
            "_id": self.userID,
            "homeGuild": self.homeGuild,
            "visitingGuild": self.visitingGuild,
            "money": self.money,
            "level": self.level,
            "is_sneaking": self.is_sneaking,
            "cosmetics": self.cosmetics,
            "pets": self.pets
        }

        
    