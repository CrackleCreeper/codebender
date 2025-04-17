import random
import json
with open("./Structures/Pets.json", "r") as f:
    pets = json.load(f)
class User:
    def __init__(self, userID, client, visitingGuild= None, money=100, level= 0, cosmetics = []):
        self.userID = userID
        self.visitingGuild = visitingGuild
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
        print(pets)
        if self.homeGuild == "Earth" : 
            self.pets.append(pets["earth"][0])
        elif self.homeGuild == "Air" : 
            self.pets.append(pets["air"][0])
        elif self.homeGuild == "Water" : 
            self.pets.append(pets["water"][0])
        elif self.homeGuild == "Fire" : 
            self.pets.append(pets["fire"][0])
        
        self.client.guildsCollection.update_one({"_id": self.homeGuild}, {"$push": {"members": self.userID}})

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

        
    