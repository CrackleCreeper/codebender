from Structures.Message import Message

class Joke:

    def __init__(self):
        self.name = "test"
        self.category = "Test Category"
        self.description = "Example joke command."
        self.user_permissions = ["manage_messages"]

    async def run(self, message):
        await message.channel.send(embed=Message(description="Why did the bot cross the road?"))
