from Structures.Message import Message
import discord
import chess
import chess.engine
import random
import os
import chess.svg
from wand.image import Image as WandImage
from wand.color import Color
from wand.image import Image as WandImage
from wand.color import Color
import asyncio

chess_games = {}
win_amount = 100
class Chess:
    def __init__(self):
        self.name = "chessguess"
        self.category = "Minigames"
        self.description = "Guess the best move in a random chess position!"
        self.description = "Guess the best move in a random chess position!"
        self.number_args = 0
        self.user_permissions = []

    def get_random_tactical_position(self, depth=12, min_cp_diff=100):
        stockfish_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")

        for _ in range(20):
            board = chess.Board()
            for _ in range(random.randint(8, 20)):
                if board.is_game_over():
                    break
                move = random.choice(list(board.legal_moves))
                board.push(move)

            try:
                engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
                analysis = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=2)
                engine.quit()

                top1 = analysis[0]["pv"][0]
                top2 = analysis[1]["pv"][0]
                score1 = analysis[0]["score"].relative.score(mate_score=10000) or 0
                score2 = analysis[1]["score"].relative.score(mate_score=10000) or 0

                if abs(score1 - score2) >= min_cp_diff:
                    return board

            except Exception as e:
                print("Error while analyzing board:", e)

        return chess.Board()

    def get_random_position(self):
        return self.get_random_tactical_position()



    def get_best_move(self, board):
        stockfish_path = os.path.join(os.path.dirname(__file__), "stockfish.exe")
        engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        result = engine.analyse(board, chess.engine.Limit(time=0.5))
        best_move = result["pv"][0]
        engine.quit()
        return best_move

    def save_board_as_png(self, board, filename="board.png"):
        svg_data = chess.svg.board(board=board, orientation=board.turn)
        with WandImage(blob=svg_data.encode('utf-8'), format='svg', background=Color("white")) as img:
            img.format = 'png'
            img.save(filename=filename)

    async def run(self, message, args, client):
        if message.author.id in chess_games:
            return await message.channel.send("You're already in a chess game!")

        board = self.get_random_position()
        best_move = self.get_best_move(board)
        chess_games[message.author.id] = (board, best_move)
        print(best_move)
        image_path = os.path.join(os.path.dirname(__file__), "board.png")
        self.save_board_as_png(board, filename=image_path)

        side = "White" if board.turn else "Black"

        file = discord.File(image_path, filename="board.png")
        await message.channel.send(
            content=f"♟ *{side} to move.* Guess the best move in this position (e.g. e4, Nf3, Qxe5). Type cancel to end.",
            file=file
        )

        def check(m):
            return m.author.id == message.author.id and m.channel.id == message.channel.id

        try:
            while True:
                try:
                    reply = await client.wait_for("message", check=check, timeout=60)
                except asyncio.TimeoutError:
                    await message.channel.send("⏰ Time's up! Game over.")
                    break

                user_input = reply.content.strip()

                if user_input in ("cancel", "stop", "exit"):
                    await message.channel.send("❌ Game cancelled.")
                    break

                try:
                    user_move = board.parse_san(user_input)
                except:
                    await message.channel.send("❌ Invalid move format. Try again (e.g. e4, Nf3, Qxe5).")
                    continue

                if user_move == best_move:
                    await message.channel.send(f"✅ Correct! That’s the best move! You got {win_amount} coins!")
                    client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": win_amount}})
                else:
                    await message.channel.send(f"❌ Not quite. That was a legal move, but the best move was *{board.san(best_move)}*")
                break

        finally:
            chess_games.pop(message.author.id, None)
            try:
                os.remove(image_path)
            except FileNotFoundError:
                pass