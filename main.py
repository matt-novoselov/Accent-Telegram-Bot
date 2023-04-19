from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import AccentWord
import os
import mysql_database
from aiogram.utils.deep_linking import get_start_link

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

kb = [[types.KeyboardButton(text="🏆 Статистика"), types.KeyboardButton(text="🛠️ ТехПоддержка")],
      [types.KeyboardButton(text="👪 Пригласить друзей")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard


@dp.message_handler(text="🛠️ ТехПоддержка")  # Run action after pressing keyboard
async def get_support(message: types.Message):
    await message.reply("🛠️ Связаться с ТехПоддержкой можно здесь: @NoveSupportBot")


@dp.message_handler(text="🏆 Статистика")  # Run action after pressing keyboard
async def get_top(message: types.Message):
    await message.reply(await mysql_database.get_stats(message.from_user.id), parse_mode="Markdown")


@dp.message_handler(text="👪 Пригласить друзей")  # Run action after pressing keyboard
async def get_top(message: types.Message):
    link = await get_start_link(message.from_user.id)
    await message.reply(f'🎁 *Приглашай друзей и получай баллы!*\n\nОтправь эту ссылку своим знакомым. Если твой друг '
                        f'зарегистрируется по ссылке ниже, то каждому из вас начислится по *+50 баллов!*', parse_mode="Markdown")
    await message.answer(link)


@dp.message_handler(commands=['start'])  # Run on /start command.
async def send_welcome(message: types.Message):
    await mysql_database.add_new_user_to_database(message.from_user.id, message['from']["first_name"],
                                                  message['from']["last_name"])  # Add new user to database
    args = message.get_args()
    if len(args) > 0:
        check_bonus = await mysql_database.CheckReferral(args, message.from_user.id)
        if check_bonus:
            await bot.send_message(message.from_user.id, '🎁 Тебе начислено *50 баллов* за регистрацию!', parse_mode="Markdown")
            await bot.send_message(args, '🎁 Кто-то зарегистрировался по твоей ссылке. Тебе начислено *50 баллов!*', parse_mode="Markdown")

    await bot.send_message(message.from_user.id, f"Привет, *{message.from_user.full_name}!*" +
                           '\n\nЯ - бот для повторения сложных случаев 4-го задания на ЕГЭ.' +
                           "\n\nНажми на слово, в котором верно поставлено ударение: ", parse_mode="Markdown",
                           reply_markup=keyboard)
    await send_game(message)


@dp.message_handler()
async def send_game(message: types.Message):
    try:
        await bot.send_message(message.chat.id, "💬 На какую букву ставится ударение в этом слове?", parse_mode="Markdown",
                           reply_markup=await AccentWord.GenerateAccents())
    except:
        print("[!] Failed to send a new game. Trying again...")
        await send_game(message)
        pass


@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    data_set = callback_query.data.split("#")
    if data_set[0] == data_set[1]:
        user_score = await mysql_database.update_score(callback_query["message"]["chat"]["id"], +10)
        await callback_query["message"].edit_text(text=f"✅ *{data_set[1]}*\n\n`+10` | Ваш счёт: `{user_score}`",
                                                  parse_mode="Markdown")
    else:
        print(
            f'[x] User {callback_query["message"]["chat"]["id"]} answered wrong {data_set[0]}. The correct answer is {data_set[1]}')
        user_score = await mysql_database.update_score(callback_query["message"]["chat"]["id"], -50)
        await callback_query["message"].edit_text(
            text=f"❌ Запомни: *{data_set[1]}*\n\n`-50` | Ваш счёт: `{user_score}`",
            parse_mode="Markdown")
    await send_game(callback_query["message"])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
