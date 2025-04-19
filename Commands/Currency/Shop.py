from Structures.Message import Message
import discord
from discord.ui import View, Button

shop_data_fire = {
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

shop_data_water = {
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

shop_data_air = {
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

shop_data_earth = {
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

def create_shop_embed(tier, shop_data, userShop):
    embed = discord.Embed(
        title=f"{tier} Shop Tier | {userShop}",
        description=f"Items available in the {tier} tier.\nUse the Item ID to purchase items using the command: !buy <itemID>",
        color=discord.Color.gold() if tier == "Legendary" else discord.Color.blue()
    )
    for item in shop_data[tier]:
        embed.add_field(
            name=item["name"],
            value=f"💰 {item['price']} coins\n🆔 Item ID: {item['itemID']}",
            inline=False
        )    
    return embed

# Custom view with buttons to navigate tiers
class ShopView(View):
    def __init__(self, shop_data, userShop):
        super().__init__(timeout=None)
        self.current_tier = "Rare"
        self.shop_data = shop_data
        self.userShop = userShop

    @discord.ui.button(label="Rare", style=discord.ButtonStyle.secondary)
    async def common_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Rare", self.shop_data, self.userShop), view=self)

    @discord.ui.button(label="Epic", style=discord.ButtonStyle.secondary)
    async def rare_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Epic", self.shop_data, self.userShop), view=self)

    @discord.ui.button(label="Legendary", style=discord.ButtonStyle.secondary)
    async def legendary_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(embed=create_shop_embed("Legendary", self.shop_data, self.userShop), view=self)

# Your command class
class Shop:

    def __init__(self):
        # The command name. In this case this command will run when you type !test
        self.name = "shop"

        # Category of the command. Preferably the name of the folder this file is in.
        self.category = "Currency"

        # What this command is used for. This description will be later used in the help command.
        self.description = "shop to view and buy items"

        # The min number of arguments needed. In this case we need 1. So the command must be !test <argument>.
        self.number_args = 0

        # The permissions user must have to execute command. If anyone can, then keep this as an empty list.
        self.user_permissions = []

    # The run function. Put your code in this.
    # Here args is a list of arguments. Access them by their index as shown.
    async def run(self, message, args, client):
        userID = message.author.id
        user = client.usersCollection.find_one({"_id": userID})
        
        if (user['visitingGuild'] == "Fire"):
            userShop = "Fire Shop"
            view = ShopView(shop_data_fire, userShop)
            embed = create_shop_embed("Rare", shop_data_fire, userShop)
        elif (user['visitingGuild'] == "Water"):
            userShop = "Water Shop"
            view = ShopView(shop_data_water, userShop)
            embed = create_shop_embed("Rare", shop_data_water, userShop)
        elif (user['visitingGuild'] == "Air"):
            userShop = "Air Shop"
            view = ShopView(shop_data_air, userShop)
            embed = create_shop_embed("Rare", shop_data_air, userShop)
        elif (user['visitingGuild'] == "Earth" ):
            userShop = "Earth Shop"
            view = ShopView(shop_data_earth, userShop)
            embed = create_shop_embed("Rare", shop_data_earth, userShop)

        await message.channel.send(embed=embed,view = view)
