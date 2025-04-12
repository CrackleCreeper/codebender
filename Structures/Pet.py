class Pet:
    def __init__(self, name, rarity, baseDefense, baseAttack, skills = [], accessories = [], level = 0, xp = 0):
        self.name = name
        self.rarity = rarity
        self.skills = skills
        self.accessories = accessories
        self.level = level
        self.xp = xp

        '''battle system stuff comes later'''
        # if self.rarity == "Common" : self.dmgMultiplier = 1
        # elif self.rarity == "Uncommon" : self.dmgMultiplier = 1.25  
        # elif self.rarity == "Rare" : self.dmgMultiplier = 1.3
        # elif self.rarity == "Legendary" : self.dmgMultiplier = 1.5

        # self.health = 100
        # self.attack = baseAttack
        # self.dmgReduction = baseDefense
