import random

class User:
    def __init__(self, userID, client, pets = [], visitingGuild= None, money=0, level= 0, cosmetics = []):
        self.userID = userID
        self.visitingGuild = visitingGuild
        self.money = money
        self.level = level
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
            self.pets = ["Crococat"]
        elif self.homeGuild == "Air" : 
            self.pets = ["RingtailLemur"]
        elif self.homeGuild == "Water" : 
            self.pets = ["Koalaotter"]
        elif self.homeGuild == "Fire" : 
            self.pets = ["BasiliskCentipede"]
        
        self.client.guildsCollection.update_one({"_id": self.homeGuild}, {"$push": {"members": self.userID}})

    def to_dict(self):
        return {
            "_id": self.userID,
            "homeGuild": self.homeGuild,
            "visitingGuild": self.visitingGuild,
            "money": self.money,
            "level": self.level,
            "cosmetics": self.cosmetics,
            "pets": self.pets
        }

        
    