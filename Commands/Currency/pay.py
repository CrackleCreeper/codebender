from Structures.Message import Message
import discord
from discord.ext import commands

class pay:
    def __init__(self):
        self.name = "pay"
        self.category = "Currency"
        self.number_args = 2
        self.description = "Command to pay another user money from your wallet. Use !pay <user> <amount>."
        self.user_permissions = []

    async def run(self, message,args,client):
        person = message.author.id 
        payer = client.usersCollection.find_one({"_id" : person})
        if message.mentions == []:
                return await message.channel.send(embed=discord.Embed(description="Please mention a user to pay!",color=discord.Color.red()))
        reciever = client.usersCollection.find_one({"_id" : message.mentions[0].id})
        if not reciever:
            return await message.channel.send(embed=Message(description="This person has not joined this bot yet!"))
        if int(args[1]) <= 0:
            return await message.channel.send(embed=Message(description="Please enter a positive integer value"))
        if reciever == payer:
            return await message.channel.send(embed=Message(description="You cant pay yourself"))
        if (int(args[1]) > payer["money"]):
            await message.channel.send(embed=Message(description="You dont have enough money!"))
        else:
            client.usersCollection.update_one({"_id" : person},{"$set":{"money": payer["money"]-int(args[1])}})
            client.usersCollection.update_one({"_id" : message.mentions[0].id},{"$set":{"money": reciever["money"] + int(args[1])}})
            await message.channel.send(embed=Message(description="Transaction Successful!"))