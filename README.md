# BotBender

## Table of Contents
1. [Introduction](#introduction)
2. [Goal](#goal)
3. [Applications](#applications)
4. [Track and Theme](#track-and-theme)
5. [Contributors](#contributors)
6. [Features](#features)
7. [Tech Stack](#tech-stack)
8. [Further Improvements](#further-improvements)

## Introduction
BotBender is a Discord bot inspired by Avatar: The Last Airbender. It features arcade mini-games for earning currency, which can be used in a rich multiplayer turn-based battle game. The bot includes its own economy where users can purchase pets from the shop and trade them amongst each other at the tradepost!

## Goal
The goal of BotBender is to create an immersive Avatar-themed gaming experience within Discord servers. By combining mini-games, pet battles, and an economy system, BotBender aims to foster community engagement and provide entertainment while paying homage to the beloved Avatar universe. The bot seeks to transform standard Discord servers into interactive worlds where users can join elemental guilds, collect unique pets, and compete against friends.

## Applications
- **Community Building**: Fosters interaction between server members
- **Entertainment**: Provides various mini-games and battle systems
- **Role-Playing**: Immerses users in the Avatar universe through guilds and pets
- **Virtual Economy**: Simulates economic interactions with currency, shop, and trading
- **Server Engagement**: Increases activity with themed channels and gameplay

## Track and Theme
Discord Bot: Arcade

## Contributors
Shaivi Nandi (BT2024003)  
Rihan Doshi (BT2024122)  
Utkarsh Goyal (BT2024264)

## Features

* On the first join of the bot to any server, it *creates custom channels* for the bot to be used in! These include:
    - Channels for each of the four guilds - fire, water, earth and air, and a no man's land which everyone can access.
    - These can be cleaned up if the bot needs to be removed using ```!cleanup``` before the bot is kicked.
* *User-initialization* - Every new user who joins the system is assigned their own guild and starter pet, to go on an exciting journey across the Avatar world!
* 6 unique *mini-games* including 
    - **Fast-type** (```!fasttype```) - Type as fast as you can to complete the sentence within 20 seconds!
    - **Connect4** (```!connect4```) - Line-up your colour either vertically, horizontally or diagonally to win!
    - **Slots** (```!slots```)- The classic casino gamble with the slot machine!
    - **Blackjack** (```!bj```) - Play against the dealer to see if you have the upper hand!
    - **Chess Guess** (```!chessguess```) - Guess the next best chess move!
    - **Hangman** (```!hangman```) - Save the man from dying by guessing the write word, letter-by-letter!
* Our very own *map system* (```!map```) that helps you see which guild you are in. Other guilds can be accesssed using the ```!sneak``` and ```!travel``` commands in the chat. [If someone tries sneaking, they can be caught by someone of that guild and can be battled with to earn more coins!]
* An in-game *economy* which features its own *shop* (```!shop```) and *tradepost* (```!tradepost```) that can be used to spend the coins earned by playing the mini-games and battling other users.
    - The **shop** consists of three tiers of rarity, each with its own skills and pets that the user can purchase (```!buy <id>```), use and level-up!
    - The **tradepost** is a robust player-to-player marketplace that enables users to:
      - Create custom trade listings with their own pricing and descriptions (```!tradepost sell```)
      - Browse all active pet listings with pagination and filtering by type, rarity, and price (```!tradepost```)
      - View detailed information about specific listings including pet stats and skills (```!tradepost info <id>```)
      - Purchase pets directly from other players (```!tradepost buy <id>```)
      - Monitor their own active listings (```!tradepost my```)
      - Set custom durations for listings (1-72 hours)
      - Receive notifications when their pets are sold
      - Showcase and profit from leveled-up, uniquely skilled pets
    - Users can check the pets they own using the ```!inventory``` command and their balance of coins using ```!checkbalance```.
    - Users can pay each other money using ```!pay```.
* A *pet vault* consisting of 16 unique ATLA-inspired pets which have their own set of skills to be used in battle! They can be viewed using the commands ```!pets``` and ```!skills```.
* A rich *turn-based battle system* (```!battle <user>```) where users can pit their pets against each other for coins, using their skills!
* The bot stores data player information such as guild, pets, cosmetics etc in a MongoDB database, which is queried and updated globally.

## Tech Stack
* Discord.py
* MongoDB
* Python
* GitHub

## Further Improvements
1. Implement a single player battle system in #no-mans-forest, which includes a quest to unlock it and boss battles.
2. More minigames
3. AI arcade assistants
4. More pets and skills
5. Choice-based quests and story mode