import app.AccentWord as AccentWord
import app.mysql_database as mysql_database
import app.Motivation as Motivation
from app.config import TELEGRAM_TOKEN
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, CommandObject


# Load bot API token
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Setup keyboard actions
kb = [[types.KeyboardButton(text="🏆 Статистика")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard


# Get statistics after pressing keyboard
@dp.message(F.text == "🏆 Статистика")
async def get_top(message: types.Message):
    await message.reply(await mysql_database.get_stats(message.from_user.id), parse_mode="Markdown")


# Run on /start command.
@dp.message(CommandStart(deep_link=True))
async def handler(message: types.Message, command: CommandObject):
    # Add new user to database, if he is not registered yet
    await mysql_database.add_new_user_to_database(message.from_user.id, message.from_user.first_name,
                                                  message.from_user.last_name)

    # Send welcome message
    await bot.send_message(message.from_user.id, f"Привет, *{message.from_user.full_name}!*" +
                           '\n\nЯ - бот для повторения сложных случаев 4-го задания на ЕГЭ.' +
                           "\n\nНажми на слово, в котором верно поставлено ударение: ", parse_mode="Markdown",
                           reply_markup=keyboard)
    # Send first riddle
    await send_game(message)


# Send new riddle
@dp.message()
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
@dp.callback_query()
async def process_callback_button1(callback_query: types.CallbackQuery):
    data_set = callback_query.data.split("#")
    if data_set[0] == data_set[1]:
        # Define reward for correct answer
        fine = 10
        # Update user score
        user_score = await mysql_database.update_score(callback_query.message.chat.id, fine, True)
        try:
            word = data_set[1]
            await callback_query.message.edit_text(
                text=f"✅ {await Motivation.Compliment()} *{word[:1].upper()}{word[1:]}*\n\n`+{fine}` | Ваш счёт: `{user_score}`",
                parse_mode="Markdown")
        except Exception as e:
            print(f'[!] There was an error in editing message after response: {e}')
            pass
    else:
        # Define fine for wrong answer
        fine = -30
        # Debug message
        print(f'[x] User {callback_query.message.chat.id} answered wrong {data_set[0]}. The correct answer is {data_set[1]}')
        # Update user score
        user_score = await mysql_database.update_score(callback_query.message.chat.id, fine, True)
        try:
            await callback_query.message.edit_text(
                text=f"❌ Неверно, запомни: *{data_set[1]}*\n\n`{fine}` | Ваш счёт: `{user_score}`",
                parse_mode="Markdown")
        except Exception as e:
            print(f'[!] There was an error in editing message after response: {e}')
            pass
    await send_game(callback_query.message)
