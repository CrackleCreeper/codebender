from Structures.Message import Message
import discord
import asyncio
import aiohttp
import time

in_game = set()


class Fasttype:

    def __init__(self):
        self.name = "fasttype"
        self.category = "Minigames"
        self.description = "A game where we can see how fast you type! You have 15 seconds to type the given sentence!"
        self.number_args = 0
        self.user_permissions = []

    async def fetch_sentence(self):
        url = "https://dummyjson.com/quotes/random"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["quote"]
        except Exception:
            pass

        return "The quick brown fox jumps over the lazy dog"

    async def run(self, message, args, client):
        if message.author.id in in_game:
            return await message.channel.send("You're already in a game!")

        in_game.add(message.author.id)

        for round_num in range(25):


            original_sentence = await self.fetch_sentence()
            original_sentence = original_sentence.lower().replace('.', '').replace(',', '')
            displayed = " ".join(f"`{' '.join(word)}`" for word in original_sentence.split())

            loading_msg = await message.channel.send("Generating a sentence, please wait...")
            await asyncio.sleep(1)
            await loading_msg.edit(content=f"**Write the following message (You have 15 seconds!)**:\n{displayed}")
            start_time = time.time()

            def check(m):
                return m.author.id == message.author.id and m.channel.id == message.channel.id

            try:
                msg = await client.wait_for('message', check=check, timeout=15.0)
            except asyncio.TimeoutError:
                await message.channel.send("⏰ Time's up!")
                in_game.remove(message.author.id)
                break

            user_input = msg.content.strip().lower()
            if user_input in ["cancel", "end"]:
                await message.channel.send("Game ended by user!")
                in_game.remove(message.author.id)
                break

            if user_input == original_sentence:
                elapsed = round(time.time() - start_time, 2)
                await message.channel.send(f"✅ Good job!\nYou typed it in **{elapsed} seconds**!")
            else:
                await message.channel.send("❌ You failed!")
                in_game.remove(message.author.id)
                break

            if round_num == 24:
                await message.channel.send("🎉 GG! You win all 25 rounds!")
                in_game.remove(message.author.id)
                break
