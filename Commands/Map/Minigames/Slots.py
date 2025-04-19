from Structures.Message import Message
import discord
import asyncio
import random

in_game = set()

class Slots:
    def __init__(self):
        self.name = "slots"
        self.category = "Minigames"
        self.description = "Spin the slot machine and try your luck with rarities and diagonals!"
        self.number_args = 1
        self.user_permissions = []

        self.emoji_weights = {
            "🍒": 40,
            "🍋": 40,
            "🍇": 30,
            "🍉": 30,
            "🔔": 15,
            "⭐": 10,
            "7️⃣": 5
        }

        self.emojis = list(self.emoji_weights.keys())

    def spin_board(self):
        board = [[random.choices(self.emojis, weights=self.emoji_weights.values())[0] for _ in range(3)] for _ in range(3)]
        return board

    def check_win(self, board):
        lines = []
        lines.extend(board)
        for col in range(3):
            lines.append([board[row][col] for row in range(3)])

        lines.append([board[i][i] for i in range(3)])
        lines.append([board[i][2 - i] for i in range(3)])
        for line in lines:
            if line[0] == line[1] == line[2]:
                return True, line[0]
        return False, None

    def format_board(self, board):
        return "\n".join(" | ".join(row) for row in board)

    async def run(self, message, args, client):
        try:
            bet = int(args[0])
        except ValueError:
            return await message.channel.send("❌ Please enter a valid number to bet!")

        if message.author.id in in_game:
            return await message.channel.send("You're already playing a game!")

        user_id = message.author.id
        user = client.usersCollection.find_one({"_id": user_id})

        if not user:
            return await message.channel.send("❌ User data not found. Please register or try again.")

        money = user.get("money", 0)

        if money < bet:
            return await message.channel.send("💸 You don't have enough money to place that bet.")

        # Deduct the bet amount immediately
        client.usersCollection.update_one({"_id": user_id}, {"$inc": {"money": -bet}})

        in_game.add(user_id)
        await message.channel.send("🎰 Spinning the slot machine...")

        await asyncio.sleep(1.5)

        board = self.spin_board()
        result_str = self.format_board(board)

        win, symbol = self.check_win(board)

        await message.channel.send(f"**\n{result_str}\n**")

        if win:
            if symbol == "7️⃣":
                win_amount = bet * 10  # Jackpot multiplier
                await message.channel.send("💎 **JACKPOT! Triple 7s! You're rich now!**")
            elif symbol in ["🔔", "⭐"]:
                win_amount = bet * 5  # Rare multiplier
                await message.channel.send("🎉 **Rare win! Nicely done!**")
            else:
                win_amount = bet * 2  # Normal win
                await message.channel.send("✅ **You win! Matching line!**")

            client.usersCollection.update_one({"_id": user_id}, {"$inc": {"money": win_amount}})
            await message.channel.send(f"💰 You won {win_amount} coins!")
        else:
            await message.channel.send("😢 No matches. Better luck next time!")

        in_game.remove(user_id)

