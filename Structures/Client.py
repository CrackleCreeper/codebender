import discord
import os
import importlib.util

path = os.path.join(os.path.dirname(__file__), "../Commands")
prefix = "!"

class HackniteClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.commands = dict()
        self.categories = dict()

    async def on_ready(self):
        await self.load(path)
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        await self.run_command(message)

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
            name = message.content[1:]
            if name.lower() in self.commands:
                instance = self.commands[name.lower()]
                if self.has_permissions(message.author, instance.user_permissions):
                    await instance.run(message)
                else:
                    await message.channel.send('You are not allowed to use this command.')

    def has_permissions(self, member, required_perms):
        perms = member.guild_permissions
        return all(getattr(perms, perm, False) for perm in required_perms)


