# Accent bot

Source code for a Telegram bot built using Aiogram. This bot is designed to assist you in learning the challenging aspects of word accents. Compete with friends and earn points as you progress through your educational journey!

![](https://github.com/matt-novoselov/Accent-Telegram-Bot/blob/6667c31cb029512ae7d637f4c8426ca976f17706/Thumbnail.png)

[![Telegram Bot](https://github.com/matt-novoselov/matt-novoselov/blob/4fddb3cb2c7e952d38b8b09037040af183556a77/Files/telegram_button.svg)](https://t.me/AccentGameBot)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/ICY9k5?referralCode=RmyABJ)

## Requirements
- Python 3.8
- aiogram 2.25.1
- python-dotenv 1.0.0
- aiomysql 0.1.1
- cryptography 40.0.2

## Installation
1. Clone repository using the following URL: `https://github.com/matt-novoselov/Accent-Telegram-Bot.git`
2. Create Environment File:
   - Create a file named `.env` in the root directory of the source folder.
   - Use the provided `.env.example` file as a template.
3. Replace the placeholder values with your specific configuration:
   - TOKEN: Insert your Telegram Bot Token obtained from the [BotFather](https://t.me/botfather).
   - HOST: This is the host address for your MySQL database.
   - DB_USERNAME: The username used to access your MySQL database.
   - PASSWORD: The password associated with the provided username for accessing the MySQL database.
   - DATABASE: The name of the MySQL database your bot will use.
4. Build and run `main.py`

<br>

## Credits
Distributed under the MIT license. See **LICENSE** for more information.

Developed with ❤️ by Matt Novoselov
