from Structures.Message import Message
import discord
from discord.ui import View, Button, Select, Modal, TextInput
import json
import asyncio
from datetime import datetime, timedelta
import os
import pymongo

class TradeListingModal(Modal):
    def __init__(self, pet_data, user_data):
        super().__init__(title="Create Trade Listing")
        self.pet_data = pet_data
        self.user_data = user_data
        
        self.price_input = TextInput(
            label="Price (coins)",
            placeholder="Enter the price for your pet",
            required=True,
            min_length=1,
            max_length=10
        )
        self.description_input = TextInput(
            label="Description (optional)",
            placeholder="Describe what makes your pet special",
            required=False,
            max_length=200,
            style=discord.TextStyle.paragraph
        )
        self.duration_input = TextInput(
            label="Duration (hours)",
            placeholder="How long to list (1-72 hours)",
            required=True,
            default="24"
        )
        
        self.add_item(self.price_input)
        self.add_item(self.description_input)
        self.add_item(self.duration_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = int(self.price_input.value)
            duration = int(self.duration_input.value)
            
            if price <= 0:
                return await interaction.response.send_message("Price must be greater than 0.", ephemeral=True)
            
            if duration < 1 or duration > 72:
                return await interaction.response.send_message("Duration must be between 1 and 72 hours.", ephemeral=True)
            
            # Create the listing
            expiry_time = datetime.now() + timedelta(hours=duration)
            
            listing = {
                "_id": f"trade_{interaction.user.id}_{int(datetime.now().timestamp())}",
                "seller_id": interaction.user.id,
                "seller_name": interaction.user.name,
                "pet": self.pet_data,
                "price": price,
                "description": self.description_input.value,
                "created_at": datetime.now().isoformat(),
                "expires_at": expiry_time.isoformat(),
                "status": "active"
            }
            
            # Add to database
            client = interaction.client
            client.trade_listings.insert_one(listing)
            
            # Remove pet from user's inventory
            client.usersCollection.update_one(
                {"_id": interaction.user.id},
                {"$pull": {"pets": {"name": self.pet_data["name"]}}}
            )
            
            embed = discord.Embed(
                title="🎉 Trade Listing Created!",
                description=f"Your {self.pet_data['name']} has been listed for {price} coins.",
                color=discord.Color.green()
            )
            embed.add_field(name="Duration", value=f"{duration} hours", inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(expiry_time.timestamp())}:R>", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Also send to trade channel if it exists
            trade_channel = discord.utils.get(interaction.guild.channels, name="trade-post")
            if trade_channel:
                trade_embed = create_trade_listing_embed(listing)
                view = TradeListingView(listing["_id"])
                await trade_channel.send(embed=trade_embed, view=view)
                
        except ValueError:
            await interaction.response.send_message("Please enter valid numbers for price and duration.", ephemeral=True)

class PetSelectView(View):
    def __init__(self, user_data):
        super().__init__(timeout=60)
        self.user_data = user_data
        
        # Create a select menu with user's pets
        self.pet_select = Select(
            placeholder="Choose a pet to trade",
            options=[
                discord.SelectOption(
                    label=f"{pet['name']} (Lvl {pet['level']})",
                    description=f"{pet['type']} | {pet['rarity']}",
                    value=i
                ) for i, pet in enumerate(user_data["pets"])
            ],
            max_values=1
        )
        
        self.pet_select.callback = self.pet_selected
        self.add_item(self.pet_select)
    
    async def pet_selected(self, interaction: discord.Interaction):
        pet_index = int(self.pet_select.values[0])
        selected_pet = self.user_data["pets"][pet_index]
        
        # Show confirmation
        embed = discord.Embed(
            title="Pet Trade Confirmation",
            description=f"You selected **{selected_pet['name']}** to trade.",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Type", value=selected_pet["type"], inline=True)
        embed.add_field(name="Rarity", value=selected_pet["rarity"], inline=True)
        embed.add_field(name="Level", value=selected_pet["level"], inline=True)
        
        # List skills
        skills_text = ""
        for move in selected_pet.get("moves", []):
            move_name = move.get("name", "Unknown")
            move_type = move.get("type", "Unknown")
            skills_text += f"• {move_name} ({move_type})\n"
        
        embed.add_field(name="Skills", value=skills_text or "No special skills", inline=False)
        
        # Create modal for price and description
        modal = TradeListingModal(selected_pet, self.user_data)
        await interaction.response.send_modal(modal)

class TradeListingView(View):
    def __init__(self, listing_id):
        super().__init__(timeout=None)
        self.listing_id = listing_id
    
    @discord.ui.button(label="Buy Pet", style=discord.ButtonStyle.success, emoji="💰")
    async def buy_button(self, interaction: discord.Interaction, button: Button):
        client = interaction.client
        
        # Get the listing
        listing = client.trade_listings.find_one({"_id": self.listing_id})
        if not listing:
            return await interaction.response.send_message("This listing no longer exists.", ephemeral=True)
        
        if listing["status"] != "active":
            return await interaction.response.send_message("This listing is no longer active.", ephemeral=True)
        
        # Check if user has enough money
        buyer_data = client.usersCollection.find_one({"_id": interaction.user.id})
        if not buyer_data:
            return await interaction.response.send_message("You need to join a guild first with !join", ephemeral=True)
        
        if buyer_data["_id"] == listing["seller_id"]:
            return await interaction.response.send_message("You cannot buy your own pet listing.", ephemeral=True)
        
        if buyer_data["money"] < listing["price"]:
            return await interaction.response.send_message(f"You don't have enough coins. You need {listing['price']} coins.", ephemeral=True)
        
        # Process the transaction
        # 1. Update listing status
        client.trade_listings.update_one(
            {"_id": self.listing_id},
            {"$set": {"status": "sold", "buyer_id": interaction.user.id, "buyer_name": interaction.user.name}}
        )
        
        # 2. Transfer money from buyer to seller
        client.usersCollection.update_one(
            {"_id": interaction.user.id},
            {"$inc": {"money": -listing["price"]}}
        )
        
        client.usersCollection.update_one(
            {"_id": listing["seller_id"]},
            {"$inc": {"money": listing["price"]}}
        )
        
        # 3. Add pet to buyer's inventory
        client.usersCollection.update_one(
            {"_id": interaction.user.id},
            {"$push": {"pets": listing["pet"]}}
        )
        
        # 4. Send confirmation messages
        buyer_embed = discord.Embed(
            title="🎉 Purchase Successful!",
            description=f"You purchased **{listing['pet']['name']}** for {listing['price']} coins.",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=buyer_embed, ephemeral=True)
        
        # Disable the button
        self.buy_button.disabled = True
        self.buy_button.label = "Sold!"
        await interaction.message.edit(view=self)
        
        # Notify seller if they're in the server
        seller = interaction.guild.get_member(listing["seller_id"])
        if seller:
            seller_embed = discord.Embed(
                title="💰 Pet Sold!",
                description=f"Your **{listing['pet']['name']}** was purchased by {interaction.user.name} for {listing['price']} coins.",
                color=discord.Color.gold()
            )
            try:
                await seller.send(embed=seller_embed)
            except:
                pass  # Can't DM the user
    
    @discord.ui.button(label="View Details", style=discord.ButtonStyle.secondary, emoji="🔍")
    async def details_button(self, interaction: discord.Interaction, button: Button):
        client = interaction.client
        
        # Get the listing
        listing = client.trade_listings.find_one({"_id": self.listing_id})
        if not listing:
            return await interaction.response.send_message("This listing no longer exists.", ephemeral=True)
        
        # Create detailed embed
        embed = create_detailed_listing_embed(listing)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class BrowseTradeView(View):
    def __init__(self, listings, page=0, filters=None):
        super().__init__(timeout=60)
        self.listings = listings
        self.page = page
        self.filters = filters or {}
        self.per_page = 5
        self.max_pages = (len(listings) - 1) // self.per_page + 1
        
        # Add filter button
        self.add_item(discord.ui.Button(label="Filter", style=discord.ButtonStyle.secondary, custom_id="filter"))
        
        # Add navigation buttons
        self.update_buttons()
    
    def update_buttons(self):
        # Clear existing buttons
        for item in self.children[:]:
            if item.custom_id not in ["filter"]:
                self.remove_item(item)
        
        # Add navigation buttons
        if self.page > 0:
            self.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="prev"))
        
        if self.page < self.max_pages - 1:
            self.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next"))
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "prev":
            self.page -= 1
        elif interaction.data["custom_id"] == "next":
            self.page += 1
        elif interaction.data["custom_id"] == "filter":
            # Show filter modal
            await interaction.response.send_modal(FilterModal(self.filters))
            return True
        
        self.update_buttons()
        
        # Get current page listings
        start_idx = self.page * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.listings))
        current_listings = self.listings[start_idx:end_idx]
        
        embed = discord.Embed(
            title="🏪 Pet Trade Post",
            description=f"Browse pets for sale (Page {self.page+1}/{self.max_pages})",
            color=discord.Color.blue()
        )
        
        for listing in current_listings:
            pet = listing["pet"]
            embed.add_field(
                name=f"{pet['name']} ({pet['rarity']})",
                value=f"💰 {listing['price']} coins | 🕒 Expires <t:{int(datetime.fromisoformat(listing['expires_at']).timestamp())}:R>\n"
                      f"👤 Seller: {listing['seller_name']} | 🆔 ID: `{listing['_id']}`",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
        return True

class FilterModal(Modal):
    def __init__(self, current_filters):
        super().__init__(title="Filter Trade Listings")
        
        self.type_input = TextInput(
            label="Element Type (Fire/Water/Air/Earth)",
            placeholder="Leave blank for any",
            required=False,
            default=current_filters.get("type", "")
        )
        
        self.rarity_input = TextInput(
            label="Rarity (common/rare/epic/legendary)",
            placeholder="Leave blank for any",
            required=False,
            default=current_filters.get("rarity", "")
        )
        
        self.max_price_input = TextInput(
            label="Maximum Price",
            placeholder="Leave blank for no limit",
            required=False,
            default=str(current_filters.get("max_price", ""))
        )
        
        self.add_item(self.type_input)
        self.add_item(self.rarity_input)
        self.add_item(self.max_price_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        filters = {}
        
        if self.type_input.value:
            filters["type"] = self.type_input.value.capitalize()
        
        if self.rarity_input.value:
            filters["rarity"] = self.rarity_input.value.lower()
        
        if self.max_price_input.value:
            try:
                filters["max_price"] = int(self.max_price_input.value)
            except ValueError:
                pass
        
        # Apply filters
        client = interaction.client
        query = {"status": "active"}
        
        if "type" in filters:
            query["pet.type"] = filters["type"]
        
        if "rarity" in filters:
            query["pet.rarity"] = filters["rarity"]
        
        if "max_price" in filters:
            query["price"] = {"$lte": filters["max_price"]}
        
        listings = list(client.trade_listings.find(query).sort("created_at", -1))
        
        if not listings:
            embed = discord.Embed(
                title="🏪 Pet Trade Post",
                description="No listings found with these filters.",
                color=discord.Color.red()
            )
            return await interaction.response.edit_message(embed=embed, view=None)
        
        view = BrowseTradeView(listings, filters=filters)
        
        embed = discord.Embed(
            title="🏪 Pet Trade Post",
            description=f"Found {len(listings)} listings with your filters",
            color=discord.Color.blue()
        )
        
        # Display first page
        start_idx = 0
        end_idx = min(start_idx + view.per_page, len(listings))
        current_listings = listings[start_idx:end_idx]
        
        for listing in current_listings:
            pet = listing["pet"]
            embed.add_field(
                name=f"{pet['name']} ({pet['rarity']})",
                value=f"💰 {listing['price']} coins | 🕒 Expires <t:{int(datetime.fromisoformat(listing['expires_at']).timestamp())}:R>\n"
                      f"👤 Seller: {listing['seller_name']} | 🆔 ID: `{listing['_id']}`",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=view)

def create_trade_listing_embed(listing):
    pet = listing["pet"]
    
    embed = discord.Embed(
        title=f"🔄 New Pet Trade: {pet['name']}",
        description=listing.get("description", "No description provided."),
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Price", value=f"💰 {listing['price']} coins", inline=True)
    embed.add_field(name="Type", value=pet["type"], inline=True)
    embed.add_field(name="Rarity", value=pet["rarity"], inline=True)
    embed.add_field(name="Level", value=pet["level"], inline=True)
    
    # Stats
    embed.add_field(name="HP", value=pet["base_hp"], inline=True)
    embed.add_field(name="Attack", value=pet["attack"], inline=True)
    embed.add_field(name="Defense", value=pet["defense"], inline=True)
    
    # Skills
    skills_text = ""
    for move in pet["moves"]:
        skills_text += f"• {move['name']} ({move['type']})\n"
    
    embed.add_field(name="Skills", value=skills_text or "No special skills", inline=False)
    
    # Seller and expiry
    embed.add_field(name="Seller", value=listing["seller_name"], inline=True)
    embed.add_field(name="Expires", value=f"<t:{int(datetime.fromisoformat(listing['expires_at']).timestamp())}:R>", inline=True)
    
    # Footer with ID
    embed.set_footer(text=f"Listing ID: {listing['_id']}")
    
    return embed

def create_detailed_listing_embed(listing):
    pet = listing["pet"]
    
    embed = discord.Embed(
        title=f"🔍 Pet Details: {pet['name']}",
        description=listing.get("description", "No description provided."),
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Price", value=f"💰 {listing['price']} coins", inline=True)
    embed.add_field(name="Type", value=pet["type"], inline=True)
    embed.add_field(name="Rarity", value=pet["rarity"], inline=True)
    embed.add_field(name="Level", value=pet["level"], inline=True)
    embed.add_field(name="XP", value=pet["xp"], inline=True)
    
    # Stats
    embed.add_field(name="HP", value=pet["base_hp"], inline=True)
    embed.add_field(name="Attack", value=pet["attack"], inline=True)
    embed.add_field(name="Defense", value=pet["defense"], inline=True)
    
    # Skills with detailed info
    embed.add_field(name="Skills", value="See below for detailed skills", inline=False)
    
    for move in pet["moves"]:
        move_name = move["name"]
        move_type = move["type"].lower()
        
        # Try to find detailed skill info
        skill_info = None
        with open("./Skills.json", "r") as f:
            skills_data = json.load(f)
            for skill in skills_data.get(move_type, []):
                if skill["name"] == move_name:
                    skill_info = skill
                    break
        
        if skill_info:
            skill_text = f"**Type:** {skill_info.get('skilltype', 'Unknown')}\n"
            skill_text += f"**Attack Type:** {skill_info.get('atktype', 'Unknown')}\n"
            skill_text += f"**Power:** {skill_info.get('power', 0)}\n"
            
            if skill_info.get('description'):
                skill_text += f"**Description:** {skill_info['description']}\n"
            
            # Add special effects
            effects = []
            if skill_info.get('defreduction', 0) > 0:
                effects.append(f"Defense reduction: {skill_info['defreduction']}")
            if skill_info.get('defbuff', 0) > 0:
                effects.append(f"Defense buff: {skill_info['defbuff']}")
            if skill_info.get('atkbuff', 0) > 0:
                effects.append(f"Attack buff: {skill_info['atkbuff']}")
            if skill_info.get('atkreduction', 0) > 0:
                effects.append(f"Attack reduction: {skill_info['atkreduction']}")
            if skill_info.get('heal', 0) > 0:
                effects.append(f"Healing: {skill_info['heal']}")
            if skill_info.get('dodge', False):
                effects.append("Can dodge attacks")
            if skill_info.get('skipNextTurn', False):
                effects.append("Stuns opponent")
            if skill_info.get('numInstances', 1) > 1:
                effects.append(f"Hits {skill_info['numInstances']} times")
            
            if effects:
                skill_text += "**Effects:** " + ", ".join(effects)
            
            embed.add_field(name=move_name, value=skill_text, inline=False)
        else:
            embed.add_field(name=move_name, value=f"Type: {move_type}", inline=False)
    
    # Seller and expiry
    embed.add_field(name="Seller", value=listing["seller_name"], inline=True)
    embed.add_field(name="Listed", value=f"<t:{int(datetime.fromisoformat(listing['created_at']).timestamp())}:R>", inline=True)
    embed.add_field(name="Expires", value=f"<t:{int(datetime.fromisoformat(listing['expires_at']).timestamp())}:R>", inline=True)
    
    return embed

class TradePost:
    def __init__(self):
        self.name = "tradepost"
        self.aliases = ["tp", "trade"]
        self.description = "Buy and sell pets with custom skills"
        self.number_args = 0
        self.category = "Currency"
        self.user_permissions = []

    async def ensure_db_connection(self, client):
        """Ensure database connection is active"""
        if not hasattr(client, 'DB') or client.DB is None:
            # Reconnect to MongoDB
            mongo_path = os.environ.get("MONGODB_URI", "mongodb+srv://shaivinandi:shaivi0812@botbender.xc5wwmc.mongodb.net/")
            myClient = pymongo.MongoClient(mongo_path)
            client.DB = myClient["BotBender"]
            client.usersCollection = client.DB["Users"]
            client.trade_listings = client.DB["trade_listings"]
            
            # Create indexes if they don't exist
            client.trade_listings.create_index("status")
            client.trade_listings.create_index("seller_id")
            client.trade_listings.create_index("expires_at")

    async def run(self, message, args, client):
        try:
            # Ensure database connection
            await self.ensure_db_connection(client)
            
            # Test database connection
            try:
                # Try a simple operation to verify connection
                # Don't use boolean evaluation on the DB object directly
                client.DB.command('ping')
            except Exception as e:
                print(f"Database connection error: {e}")
                return await message.channel.send("Unable to connect to the database. Please try again later.")

            # Check if user exists
            try:
                user_data = client.usersCollection.find_one({"_id": message.author.id})
                if not user_data:
                    return await message.channel.send("You need to join a guild first with !join")
            except Exception as e:
                print(f"Error checking user data: {e}")
                return await message.channel.send("Unable to access user data. Please try again later.")

            # Handle help command first as it doesn't need database access
            if args and args[0].lower() == "help":
                embed = discord.Embed(
                    title="🏪 Trade Post Commands",
                    description="Here are all the available trade post commands:",
                    color=discord.Color.blue()
                )
                embed.add_field(name="!tradepost", value="Browse all active listings", inline=False)
                embed.add_field(name="!tradepost sell", value="Create a new listing", inline=False)
                embed.add_field(name="!tradepost my", value="View your active listings", inline=False)
                embed.add_field(name="!tradepost buy <id>", value="Purchase a pet", inline=False)
                embed.add_field(name="!tradepost info <id>", value="View listing details", inline=False)
                embed.add_field(name="!tradepost help", value="See all commands", inline=False)
                return await message.channel.send(embed=embed)

            # Default: browse listings
            if not args:
                try:
                    listings = list(client.trade_listings.find({"status": "active"}).sort("created_at", -1))
                    if not listings:
                        return await message.channel.send("There are no active trade listings. Use `!tradepost sell` to create one!")

                    view = BrowseTradeView(listings)
                    embed = discord.Embed(
                        title="🏪 Pet Trade Post",
                        description=f"Browse pets for sale (Page 1/{view.max_pages})",
                        color=discord.Color.blue()
                    )

                    # Display first page
                    start_idx = 0
                    end_idx = min(start_idx + view.per_page, len(listings))
                    current_listings = listings[start_idx:end_idx]

                    for listing in current_listings:
                        pet = listing["pet"]
                        embed.add_field(
                            name=f"{pet['name']} ({pet['rarity']})",
                            value=f"💰 {listing['price']} coins | 🕒 Expires <t:{int(datetime.fromisoformat(listing['expires_at']).timestamp())}:R>\n"
                                  f"👤 Seller: {listing['seller_name']} | 🆔 ID: `{listing['_id']}`",
                            inline=False
                        )

                    return await message.channel.send(embed=embed, view=view)
                except Exception as e:
                    print(f"Error browsing listings: {e}")
                    return await message.channel.send("Unable to fetch listings. Please try again later.")

            # Handle other subcommands
            subcommand = args[0].lower()

            if subcommand == "sell":
                if not user_data.get("pets"):
                    return await message.channel.send("You don't have any pets to sell.")
                view = PetSelectView(user_data)
                return await message.channel.send("Select a pet to create a trade listing:", view=view)

            elif subcommand == "my":
                try:
                    listings = list(client.trade_listings.find({"seller_id": message.author.id, "status": "active"}).sort("created_at", -1))
                    if not listings:
                        return await message.channel.send("You don't have any active trade listings.")

                    embed = discord.Embed(
                        title="🏪 Your Trade Listings",
                        description=f"You have {len(listings)} active listings",
                        color=discord.Color.blue()
                    )

                    for listing in listings:
                        pet = listing["pet"]
                        embed.add_field(
                            name=f"{pet['name']} ({pet['rarity']})",
                            value=f"💰 {listing['price']} coins | 🕒 Expires <t:{int(datetime.fromisoformat(listing['expires_at']).timestamp())}:R>\n"
                                  f"🆔 ID: `{listing['_id']}`",
                            inline=False
                        )

                    return await message.channel.send(embed=embed)
                except Exception as e:
                    print(f"Error fetching user listings: {e}")
                    return await message.channel.send("Unable to fetch your listings. Please try again later.")

            elif subcommand == "buy":
                if len(args) < 2:
                    return await message.channel.send("Please provide a listing ID to buy.")

                try:
                    listing_id = args[1]
                    listing = client.trade_listings.find_one({"_id": listing_id, "status": "active"})

                    if not listing:
                        return await message.channel.send("Listing not found or not active.")

                    if listing["seller_id"] == message.author.id:
                        return await message.channel.send("You cannot buy your own pet listing.")

                    if user_data["money"] < listing["price"]:
                        return await message.channel.send(f"You don't have enough coins. You need {listing['price']} coins.")

                    # Process transaction
                    client.trade_listings.update_one(
                        {"_id": listing_id},
                        {"$set": {"status": "sold", "buyer_id": message.author.id, "buyer_name": message.author.name}}
                    )

                    client.usersCollection.update_one(
                        {"_id": message.author.id},
                        {"$inc": {"money": -listing["price"]}}
                    )

                    client.usersCollection.update_one(
                        {"_id": listing["seller_id"]},
                        {"$inc": {"money": listing["price"]}}
                    )

                    client.usersCollection.update_one(
                        {"_id": message.author.id},
                        {"$push": {"pets": listing["pet"]}}
                    )

                    embed = discord.Embed(
                        title="🎉 Purchase Successful!",
                        description=f"You purchased **{listing['pet']['name']}** for {listing['price']} coins.",
                        color=discord.Color.green()
                    )

                    await message.channel.send(embed=embed)

                    # Notify seller
                    seller = message.guild.get_member(listing["seller_id"])
                    if seller:
                        seller_embed = discord.Embed(
                            title="💰 Pet Sold!",
                            description=f"Your **{listing['pet']['name']}** was purchased by {message.author.name} for {listing['price']} coins.",
                            color=discord.Color.gold()
                        )
                        try:
                            await seller.send(embed=seller_embed)
                        except:
                            pass
                except Exception as e:
                    print(f"Error processing purchase: {e}")
                    return await message.channel.send("An error occurred while processing the purchase. Please try again later.")

            elif subcommand == "info":
                if len(args) < 2:
                    return await message.channel.send("Please provide a listing ID to view details.")

                try:
                    listing_id = args[1]
                    listing = client.trade_listings.find_one({"_id": listing_id})

                    if not listing:
                        return await message.channel.send("Listing not found.")

                    embed = create_detailed_listing_embed(listing)
                    return await message.channel.send(embed=embed)
                except Exception as e:
                    print(f"Error fetching listing details: {e}")
                    return await message.channel.send("Unable to fetch listing details. Please try again later.")

        except Exception as e:
            print(f"Error in tradepost command: {e}")
            return await message.channel.send("An error occurred. Please try again later.")
