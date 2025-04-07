from Structures.Message import Message
import discord
import asyncio

class Connect4:
    def __init__(self):
        self.name = "connect4"
        self.category = "Minigames"
        self.description = "Play connect 4 with your friend."
        self.number_args = 1
        self.user_permissions = []

    def make_msg(self, rows, columns, symbols, board):
        board_msg = ""
        for i in range(rows):
            print(rows)
            for j in range(columns):
                if board[i][j] == -1:
                    board_msg += "⚪"
                else:
                    board_msg += symbols[board[i][j]]
            board_msg += "\n"
        board_msg += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
        return board_msg

    async def make_move(self, rows, columns, symbols, board, num, player):
        for r in range(rows-1, -1, -1):
            print(r)
            print(num)
            if(board[r][num] == -1):
                board[r][num] = player
                return r
        return None

    def check_for_win(self, board, rows, columns, symbols, player, row, column):
        def count(dx, dy):
            cnt = 0
            x, y = row, column
            while 0 <= x < rows and 0 <= y < columns and board[x][y] == player:
                cnt += 1
                x += dx
                y += dy
            return cnt - 1

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            if 1 + count(dx, dy) + count(-dx, -dy) >= 4:
                return True
        return False

    async def run(self, message, args, client):
        if message.mentions == []:
            return await message.channel.send(embed=Message(description="Mention a user to play against."))
        opponent = message.mentions[0]
        player = message.author

        if opponent.id == player.id:
            return await message.channel.send(embed=Message(description="You can't play yourself!"))

        rows = 6
        columns = 7

        board = [[-1 for i in range(columns)] for j in range(rows)]
        turns = 0
        symbols = ["🔴", "🟡"]
        players = [player, opponent]

        while True:
            await message.channel.send(f"{players[turns].mention}'s turn! ({symbols[turns]})\n{self.make_msg(rows, columns, symbols, board)}")

            def check(m):
                return (
                        m.author.id == players[turns].id and
                        m.channel.id == message.channel.id and
                        m.content.isdigit() and
                        1 <= int(m.content) <= 7
                )

            try:
                msg = await client.wait_for("message", check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await message.channel.send(f"{players[turns].mention} took too long. Game over!")
                break

            col = int(msg.content) - 1
            row = await self.make_move(rows, columns, symbols, board, col, turns)
            if row is None:
                await message.channel.send("That column is full. Try another one.")
                continue

            if self.check_for_win(board, rows, columns, symbols, turns, row, col):
                await message.channel.send(f"{self.make_msg(rows, columns, symbols, board)}\n🎉 {players[turns].mention} wins!")
                break



            if all(board[0][c] != -1 for c in range(columns)):
                await message.channel.send(f"{self.make_msg(rows, columns, symbols, board)}\nIt's a draw!")
                break
            turns = 1 - turns