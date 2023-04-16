import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import aiomysql
from aiomysql import Error
import AccentWord
import os

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)


# - - - - - - - - - - #
loop = asyncio.get_event_loop()


async def connect_db():
    try:
        connection = await aiomysql.connect(
            host=os.getenv("HOST"),
            port=24021,
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DATABASE"),
            loop=loop,
        )

        if connection:
            return connection
        else:
            raise Exception("Database is not connected")

    except Error as e:
        print("Error while connecting to MySQL", e)


async def get_cursor():
    global mydb
    await mydb.ping()
    if mydb.closed:
        mydb = loop.run_until_complete(connect_db())

    return mydb.cursor()


mydb = loop.run_until_complete(connect_db())
# - - - - - - - - - - #


async def add_new_user_to_database(user_id, user_name):
    async with await get_cursor() as cur:
        try:
            # Check if user exists
            data_query = (user_id,)
            query = "select if( exists(select* from EgeBotUsers where TelegramUserID=%s), 1, 0)"
            await cur.execute(query, data_query)
            user_exist = await cur.fetchone()
            user_exist = user_exist[0]

            # Add new user if he doesn't exist
            if not user_exist:
                query = "insert into EgeBotUsers (TelegramUserID, Name) values (%s, %s)"
                data_query = (user_id, user_name)
                await cur.execute(query, data_query)
                await mydb.commit()

        except Error as e:
            print(e)


async def update_score(user_id, amount):
    async with await get_cursor() as cur:
        try:
            query = "SELECT Score FROM EgeBotUsers WHERE TelegramUserID = %s"
            data_query = (user_id,)
            await cur.execute(query, data_query)
            current_score = await cur.fetchall()  # Get current score
            current_score = list(current_score)[0][0]
            new_score = current_score + amount  # Calculate new score

            sql = "UPDATE EgeBotUsers SET Score = %s WHERE TelegramUserID = %s"
            val = (new_score, user_id)
            await cur.execute(sql, val)
            await mydb.commit()  # Update DB Score

            return new_score

        except Error as e:
            print(e)


kb = [[types.KeyboardButton(text="🏆 Статистика"), types.KeyboardButton(text="🛠️ ТехПоддержка")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard


@dp.message_handler(text="🛠️ ТехПоддержка")  # Run action after pressing keyboard
async def get_support(message: types.Message):
    await message.reply("🛠️ Связаться с ТехПоддержкой можно здесь: @NoveSupportBot")


async def get_stats(user_id):
    async with await get_cursor() as cur:
        try:
            sql = "SELECT * FROM EgeBotUsers ORDER BY Score DESC LIMIT 3"
            await cur.execute(sql)
            chart_stats = list(await cur.fetchall())

            query = "SELECT Score, Name FROM EgeBotUsers WHERE TelegramUserID = %s"
            data_query = (user_id,)
            await cur.execute(query, data_query)
            temp_proxy = await cur.fetchall()
            temp_proxy = temp_proxy[0]
            chart_stats.append(temp_proxy)

            return chart_stats

        except Error as e:
            print(e)


@dp.message_handler(text="🏆 Статистика")  # Run action after pressing keyboard
async def get_top(message: types.Message):
    my_result = await get_stats(message.from_user.id)

    await message.reply('🏆 Топ игроков по очкам:\n'
                        f'\n🥇*{my_result[0][1]}* - `{my_result[0][3]}`'
                        f'\n🥈*{my_result[1][1]}* - `{my_result[1][3]}`'
                        f'\n🥉*{my_result[2][1]}* - `{my_result[2][3]}`'
                        f'\n\n*{my_result[3][1]}* (я) - `{my_result[3][0]}`'
                        , parse_mode="Markdown")


@dp.message_handler(commands=['start'])  # Run on /start command.
async def send_welcome(message: types.Message):
    dbname = message['from']["first_name"]
    if message['from']["last_name"] is not None:
        dbname += f" {message['from']['last_name'][0:1]}."

    await add_new_user_to_database(message.from_user.id, dbname)  # Add new user to database

    await bot.send_message(message.from_user.id, f"Привет, *{message.from_user.full_name}!*" +
                           '\n\nЯ - бот для повторения сложных случаев 4-го задания на ЕГЭ.' +
                           "\n\nНажми на слово, в котором верно поставлено ударение: ", parse_mode="Markdown",
                           reply_markup=keyboard)
    await send_game(message)


@dp.message_handler()
async def send_game(message: types.Message):
    dictionary = AccentWord.GenerateAccents()

    inline_kb_full = InlineKeyboardMarkup(row_width=2)
    i = len(dictionary['VariationsArray'])
    while i > 0:
        if i % 2 == 0:
            inline_kb_full.add(
                InlineKeyboardButton(dictionary['VariationsArray'][i - 1],
                                     callback_data=f"{dictionary['VariationsArray'][i - 1]}#{dictionary['CorrectWord']}"),
                InlineKeyboardButton(dictionary['VariationsArray'][i - 2],
                                     callback_data=f"{dictionary['VariationsArray'][i - 2]}#{dictionary['CorrectWord']}"),
            )
            i -= 2
        else:
            inline_kb_full.add(
                InlineKeyboardButton(dictionary['VariationsArray'][i - 1],
                                     callback_data=f"{dictionary['VariationsArray'][i - 1]}#{dictionary['CorrectWord']}"),
            )
            i -= 1

    await bot.send_message(message.chat.id, "💬 На какую букву ставится ударение в этом слове?", parse_mode="Markdown",
                           reply_markup=inline_kb_full)


@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    M = callback_query.data.split("#")
    if M[0] == M[1]:
        user_score = await update_score(callback_query["message"]["chat"]["id"], +10)

        await callback_query["message"].edit_text(text=f"✅ *{M[1]}*\n\n`+10` | Ваш счёт: `{user_score}`",
                                                  parse_mode="Markdown")
    else:
        user_score = await update_score(callback_query["message"]["chat"]["id"], -50)

        await callback_query["message"].edit_text(text=f"❌ Запомни: *{M[1]}*\n\n`-50` | Ваш счёт: `{user_score}`",
                                                  parse_mode="Markdown")
    try:
        await send_game(callback_query["message"])
    except:
        print("[!] Failed to send a new game. Trying again...")
        await send_game(callback_query["message"])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
