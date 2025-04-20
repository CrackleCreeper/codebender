import math
import random
import asyncio

ingame = {}

class BlackJack:
    def __init__(self):
        self.name = "bj"
        self.category = "Minigames"
        self.description = "Play blackjack to earn coins. Use !bj <bet amount>."
        self.number_args = 1
        self.cooldown = 30
        self.user_permissions = []

    def draw_card(self):
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return random.choice(cards)

    def value(self, hand):
        total = 0
        ace_count = 0
        for card in hand:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                ace_count += 1
                total += 11
            else:
                total += int(card)
        while ace_count > 0 and total > 21:
            total -= 10
            ace_count -= 1
        return total

    def format_hand(self, dealer_hand, player_hand, reveal_dealer=False):
        dealer_display = f"{dealer_hand[0]}, ❓" if not reveal_dealer else ', '.join(dealer_hand)
        dealer_total = "??" if not reveal_dealer else str(self.value(dealer_hand))
        player_display = ', '.join(player_hand)
        player_total = self.value(player_hand)

        return (
            f"🎲 **Blackjack Game**\n\n"
            f"🃏 **Dealer's Hand:** {dealer_display} (Total: {dealer_total})\n"
            f"🙋 **Your Hand:** {player_display} (Total: {player_total})"
        )

    async def run(self, message, args, client):
        try:
            bet = int(args[0])
        except ValueError:
            return await message.channel.send(":x: Enter a valid number.")

        user = client.usersCollection.find_one({"_id": message.author.id})
        if user["money"] < bet:
            return await message.channel.send(":x: You don't have enough money.")

        win_amount = 2 * bet
        user_id = message.author.id

        if ingame.get(user_id) == 1:
            await message.channel.send("⚠️ You're already in a game.")
            return

        ingame[user_id] = 1

        player_hand = [self.draw_card(), self.draw_card()]
        dealer_hand = [self.draw_card(), self.draw_card()]

        await message.channel.send(self.format_hand(dealer_hand, player_hand, reveal_dealer=False))

        while self.value(player_hand) < 21:
            await message.channel.send(f"{message.author.mention}, type `hit` to draw or `stand` to hold.")

            def check(m):
                return m.author.id == user_id and m.channel.id == message.channel.id and m.content.lower() in ['hit', 'stand']

            try:
                msg = await client.wait_for('message', check=check, timeout=30.0)
            except asyncio.TimeoutError:
                await message.channel.send("⏰ You took too long! Game over.")
                client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": -win_amount}})
                ingame[user_id] = 0
                return

            if msg.content.lower() == 'hit':
                player_hand.append(self.draw_card())
                await message.channel.send(self.format_hand(dealer_hand, player_hand, reveal_dealer=False))
                if self.value(player_hand) > 21:
                    await message.channel.send("💥 You busted! Dealer wins.")
                    ingame[user_id] = 0
                    client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": -win_amount}})
                    return
            else:
                break

        # Dealer's turn
        await message.channel.send("🃏 Revealing dealer's hand...")
        await asyncio.sleep(1)

        while self.value(dealer_hand) < 17:
            dealer_hand.append(self.draw_card())
            await asyncio.sleep(1)

        await message.channel.send(self.format_hand(dealer_hand, player_hand, reveal_dealer=True))

        player_total = self.value(player_hand)
        dealer_total = self.value(dealer_hand)

        if dealer_total > 21:
            result = f"💥 Dealer busted! You win {win_amount} coins!"
            client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": win_amount}})
        elif dealer_total > player_total:
            result = f"😞 Dealer wins! You lost {win_amount / 2} coins!"
            client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": -win_amount}})
        elif dealer_total < player_total:
            result = f"🎉 You win {win_amount} coins!"
            client.usersCollection.update_one({"_id": message.author.id}, {"$inc": {"money": win_amount}})
        else:
            result = "🤝 It's a tie!"

        await message.channel.send(f"**Result:** {result}")
        ingame[user_id] = 0
