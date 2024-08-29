# Accent bot

Source code for a Telegram bot built using Aiogram. This bot is designed to assist you in learning difficult cases of accents in words. Complete lessons, practice, earn points, and compete with your friends for the highest score!

![](https://github.com/matt-novoselov/Accent-Telegram-Bot/blob/6667c31cb029512ae7d637f4c8426ca976f17706/Thumbnail.png)

[![Telegram Bot](https://github.com/matt-novoselov/matt-novoselov/blob/4fddb3cb2c7e952d38b8b09037040af183556a77/Files/telegram_button.svg)](https://t.me/AccentGameBot)


## Requirements
- Python 3.8
- aiogram 3.12.0
- python-dotenv 1.0.1
- fastapi 0.112.1
- uvicorn 0.30.6
- aiomysql 0.2.0
- cryptography 43.0.0

## Installation
1. Clone repository using the following URL: `https://github.com/matt-novoselov/Accent-Telegram-Bot.git`
2. Create Environment File:
   - Create a file named `.env` in the root directory of the source folder.
   - Use the provided `.env.example` file as a template.
3. Replace the placeholder values with your specific configuration:
   - TELEGRAM_TOKEN: Insert your Telegram Bot Token obtained from the [BotFather](https://t.me/botfather).
   - WEBHOOK_DOMAIN: Public SSL domain that will be listening for webhooks request from Telegram.
   - DB_HOST: This is the host address for your MySQL database.
   - DB_USERNAME: The username used to access your MySQL database.
   - DB_PASSWORD: The password associated with the provided username for accessing the MySQL database.
   - DB_NAME: The name of the MySQL database your bot will use.
4. Build and run `main.py`

<br>

## Credits
Distributed under the MIT license. See **LICENSE** for more information.

Developed with ❤️ by Matt Novoselov
