import discord
import os
import importlib.util
import pymongo

path = os.path.join(os.path.dirname(__file__), "../Commands")
prefix = "!"

class HackniteClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(intents=intents)
        self.commands = dict()
        self.users_dict = dict()
        self.guilds_dict = dict()
        self.categories = dict()

    async def on_ready(self):
        await self.load(path)
        print(f'Logged in as {self.user}')
        mongo_path = "mongodb+srv://shaivinandi:shaivi0812@botbender.xc5wwmc.mongodb.net/"
        myClient = pymongo.MongoClient(mongo_path)
        self.DB = myClient["BotBender"]
        self.usersCollection = self.DB["Users"]
        self.guildsCollection = self.DB["Guilds"]


    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        await self.run_command(message)


    async def on_guild_join(self, guild):
        # === Create Visitor Roles ===
        visitor_water = await guild.create_role(name="Visitor: Water", colour=discord.Colour.blue())
        visitor_fire = await guild.create_role(name="Visitor: Fire", colour=discord.Colour.red())
        visitor_earth = await guild.create_role(name="Visitor: Earth", colour=discord.Colour.green())
        visitor_air = await guild.create_role(name="Visitor: Air", colour=discord.Colour.yellow())

        # === Create Nation Roles ===
        water_role = await guild.create_role(name="Water", colour=discord.Colour.dark_blue())
        fire_role = await guild.create_role(name="Fire", colour=discord.Colour.dark_red())
        earth_role = await guild.create_role(name="Earth", colour=discord.Colour.dark_green())
        air_role = await guild.create_role(name="Air", colour=discord.Colour.dark_gold())

        # === Create Categories ===
        water_cat = await guild.create_category(name="Water Nation")
        fire_cat = await guild.create_category(name="Fire Nation")
        earth_cat = await guild.create_category(name="Earth Nation")
        air_cat = await guild.create_category(name="Air Nation")
        nomans_cat = await guild.create_category(name="No Man's Land")

        def overwrites(roles_to_overwrite = []):
            overwrites_dict = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                self.user: discord.PermissionOverwrite(view_channel=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
            for role in roles_to_overwrite:
                overwrites_dict[role] = discord.PermissionOverwrite(view_channel=True)
            return overwrites_dict
        
        # === Create Channels ===
        fire_general   = await guild.create_text_channel(name="fire-general", category=fire_cat)
        water_general  = await guild.create_text_channel(name="water-general", category=water_cat)
        earth_general  = await guild.create_text_channel(name="earth-general", category=earth_cat)
        air_general    = await guild.create_text_channel(name="air-general", category=air_cat)

        fire_battle    = await guild.create_text_channel(name="fire-battle", category=fire_cat, topic="Fire Nation battle grounds", overwrites=overwrites([fire_role, visitor_fire]))
        water_battle   = await guild.create_text_channel(name="water-battle", category=water_cat, topic="Water Nation battle grounds", overwrites=overwrites([water_role, visitor_water]))
        earth_battle   = await guild.create_text_channel(name="earth-battle", category=earth_cat, topic="Earth Nation battle grounds", overwrites=overwrites([earth_role, visitor_earth]))
        air_battle     = await guild.create_text_channel(name="air-battle", category=air_cat, topic="Air Nation battle grounds", overwrites=overwrites([air_role, visitor_air]))
        no_mans        = await guild.create_text_channel(name="no-mans-forest", category=nomans_cat, topic="No Man's Land battle grounds")

        await guild.create_text_channel("water-private-channel", category=water_cat, overwrites=overwrites([water_role]))
        await guild.create_text_channel("fire-private-channel", category=fire_cat, overwrites=overwrites([fire_role]))
        await guild.create_text_channel("earth-private-channel", category=earth_cat, overwrites=overwrites([earth_role]))
        await guild.create_text_channel("air-private-channel", category=air_cat, overwrites=overwrites([air_role]))  



    async def load(self, path):
        print('Loading commands from: ' + path)

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.py'):
                    module_path = os.path.join(root, file)

                    rel_path = os.path.relpath(module_path, path).replace(os.sep, '.')
                    module_name = rel_path[:-3]

                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    class_name = file[:-3]
                    command_class = getattr(module, class_name, None)

                    if command_class:
                        instance = command_class()
                        self.commands[instance.name.lower()] = instance
                        category = os.path.basename(root)
                        if category not in self.categories:
                            self.categories[category] = []
                        self.categories[category].append(instance)

                        print(f'Loaded command: {class_name} in category: {category}')
                    else:
                        print(f'Failed to load class {class_name} from {file}')




    async def run_command(self, message):
        if(message.content.startswith(prefix)):
            parts = message.content[len(prefix):].split()
            if not parts:
                return

            name = parts[0].lower()
            args = parts[1:]
            if name.lower() in self.commands:
                instance = self.commands[name.lower()]
                if self.has_permissions(message.author, instance.user_permissions):
                    expected_args = getattr(instance, 'number_args', 0)
                    if len(args) == expected_args:
                        await instance.run(message, args, self)
                    else:
                        await message.channel.send('Please enter all the arguments.')
                else:
                    await message.channel.send('You are not allowed to use this command.')

    def has_permissions(self, member, required_perms):
        perms = member.guild_permissions
        return all(getattr(perms, perm, False) for perm in required_perms)
