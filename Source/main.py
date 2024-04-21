from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import AccentWord
import os
import mysql_database
from aiogram.utils.deep_linking import get_start_link
import Motivation

# Load secrets
load_dotenv()

# Load bot API token
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

# Setup keyboard actions
kb = [[types.KeyboardButton(text="🏆 Статистика"), types.KeyboardButton(text="🛠️ ТехПоддержка")],
      [types.KeyboardButton(text="👪 Пригласить друзей")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard


# Get support after pressing keyboard
@dp.message_handler(text="🛠️ ТехПоддержка")
async def get_support(message: types.Message):
    await message.reply("🛠️ Связаться с ТехПоддержкой можно здесь: @NoveSupportBot")


# Get statistics after pressing keyboard
@dp.message_handler(text="🏆 Статистика")
async def get_top(message: types.Message):
    await message.reply(await mysql_database.get_stats(message.from_user.id), parse_mode="Markdown")


# Invite friends after pressing keyboard
@dp.message_handler(text="👪 Пригласить друзей")
async def get_top(message: types.Message):
    link = await get_start_link(message.from_user.id)
    await message.reply(f'🎁 *Приглашай друзей и получай баллы!*\n\nОтправь эту ссылку своим знакомым. Если твой друг '
                        f'зарегистрируется по ссылке ниже, то каждому из вас начислится по *+50 баллов!*',
                        parse_mode="Markdown")
    await message.answer(link)


# Run on /start command.
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Add new user to database, if he is not registered yet
    await mysql_database.add_new_user_to_database(message.from_user.id, message['from']["first_name"],
                                                  message['from']["last_name"])

    # Get arguments from the message to check refferal code
    args = message.get_args()
    if len(args) > 0:
        check_bonus = await mysql_database.CheckReferral(args, message.from_user.id)
        if check_bonus:
            # Send message to the registered user
            await bot.send_message(message.from_user.id, '🎁 Тебе начислено *50 баллов* за регистрацию!',
                                   parse_mode="Markdown")
            # Send message to the friend who invited him
            await bot.send_message(args, '🎁 Кто-то зарегистрировался по твоей ссылке. Тебе начислено *50 баллов!*',
                                   parse_mode="Markdown")

    # Send welcome message
    await bot.send_message(message.from_user.id, f"Привет, *{message.from_user.full_name}!*" +
                           '\n\nЯ - бот для повторения сложных случаев 4-го задания на ЕГЭ.' +
                           "\n\nНажми на слово, в котором верно поставлено ударение: ", parse_mode="Markdown",
                           reply_markup=keyboard)
    # Send first riddle
    await send_game(message)


# Send new riddle
@dp.message_handler()
async def send_game(message: types.Message):
    # Generate all possible answers to the riddle
    button_data = await AccentWord.GenerateAccents()
    try:
        await bot.send_message(message.chat.id, "💬 На какую букву ставится ударение в этом слове?",
                               parse_mode="Markdown",
                               reply_markup=button_data)
    except Exception as e:
        print(f"[!] Failed to send a new game. Trying again... Reason: {e}")
        print(f"[!] Button data: {button_data}")
        await send_game(message)


# Send motivation message
async def send_motivation(user_id, is_positive, score):
    try:
        if is_positive:
            # Send positive motivation in case user answers correctly X times in a row
            await bot.send_message(user_id, f'🔥 {(await Motivation.GoodStrikes()).format(count=score)}', parse_mode="Markdown")
        else:
            # Send positive motivation in case user answers wrong X times in a row
            await bot.send_message(user_id, f'😌 {await Motivation.DontGiveUp()}', parse_mode="Markdown")
    except Exception as e:
        print(f"[!] Failed to send motivation. Reason: {e}")


# Function that processes results of the callback buttons (buttons to select answer to the question)
@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    data_set = callback_query.data.split("#")
    if data_set[0] == data_set[1]:
        # Define reward for correct answer
        fine = 10
        # Update user score
        user_score = await mysql_database.update_score(callback_query["message"]["chat"]["id"], fine, True)
        try:
            word = data_set[1]
            await callback_query["message"].edit_text(
                text=f"✅ {await Motivation.Compliment()} *{word[:1].upper()}{word[1:]}*\n\n`+{fine}` | Ваш счёт: `{user_score}`",
                parse_mode="Markdown")
        except Exception as e:
            print(f'[!] There was an error in editing message after response: {e}')
            pass
    else:
        # Define fine for wrong answer
        fine = -30
        # Debug message
        print(f'[x] User {callback_query["message"]["chat"]["id"]} answered wrong {data_set[0]}. The correct answer is {data_set[1]}')
        # Update user score
        user_score = await mysql_database.update_score(callback_query["message"]["chat"]["id"], fine, True)
        try:
            await callback_query["message"].edit_text(
                text=f"❌ Неверно, запомни: *{data_set[1]}*\n\n`{fine}` | Ваш счёт: `{user_score}`",
                parse_mode="Markdown")
        except Exception as e:
            print(f'[!] There was an error in editing message after response: {e}')
            pass
    await send_game(callback_query["message"])


# Run the file
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
