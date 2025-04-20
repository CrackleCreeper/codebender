from Structures.Message import Message
import discord
import asyncio
import aiohttp
win_amount = 25
class Hangman:
    def __init__(self):
        self.name = "hangman"
        self.category = "Minigames"
        self.description = "Play hangman. Win 25 coins!"
        self.number_args = 0
        self.cooldown = 30
        self.user_permissions = []

        self.in_game = set()
        self.used_letters = []
        self.correct_letters = []
        self.stages = [
    """
    ```
     +---+
     |   |
         |
         |
         |
         |
    =========
    ```
    """,
    """
    ```
     +---+
     |   |
     O   |
         |
         |
         |
    =========
    ```
    """,
    """
    ```
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========
    ```
    """,
    """
    ```
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========
    ```
    """,
    """
    ```
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========
    ```
    """,
    """
    ```
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========
    ```
    """,
    """
    ```
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========
    ```
    """,
]



    async def get_word(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://random-word-api.herokuapp.com/word?number=1") as resp:
                data = await resp.json()
                return data[0]

    def get_display_word(self, word):
        return " ".join([c if c in self.correct_letters else "_" for c in word])

    async def display_message(self, stage, message, word):
        display_word = self.get_display_word(word)
        new_msg = self.stages[stage] + f"\n`{display_word}`\nUsed letters: {', '.join(self.used_letters)}"
        await message.channel.send(new_msg)

    async def run(self, message, args, client):
        if message.author.id in self.in_game:
            return await message.channel.send('You are already in a game.')
        else:
            self.in_game.add(message.author.id)
        word = await self.get_word()
        stage = 0
        print(word)
        self.correct_letters = ["_"] * len(word)

        while True:
            await self.display_message(stage, message, word)
            if stage == 6:
                await message.channel.send("You lost!")
                self.used_letters = []
                self.correct_letters = []
                break

            def check(m):
                return (
                        m.author == message.author and
                        m.channel == message.channel and
                        len(m.content) == 1 and
                        m.content.isalpha()
                )

            try:
                msg = await client.wait_for("message", check=check, timeout=20)
            except asyncio.TimeoutError:
                await message.channel.send("⏰ You took too long! Game over.")
                self.used_letters = []
                self.correct_letters = []
                break
            msg = msg.content.lower()
            found = 0
            for index, letter in enumerate(word):
                if letter == msg:
                    self.correct_letters[index] = letter
                    found = 1

            if found == 0:
                self.used_letters.append(msg)
                stage += 1


            if "_" not in self.correct_letters:
                await message.channel.send(f"You won! You got {win_amount} coins!")
                client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": win_amount}})
                self.used_letters = []
                self.correct_letters = []
                break

            found = 0


