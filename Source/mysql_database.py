import os
import asyncio
import aiomysql
from aiomysql import Error
from dotenv import load_dotenv
import main

# Load secrets
load_dotenv()

# - - - - - - - - - - #
loop = asyncio.get_event_loop()


# Function to connect to the database with given credentials
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
        print(f'[!] There was an error in connecting to MySQL Server: {e}')


# Get database cursor
async def get_cursor():
    global mydb
    try:
        await mydb.ping(reconnect=True)
    except Error:
        mydb = loop.run_until_complete(connect_db())
    return mydb.cursor()


mydb = loop.run_until_complete(connect_db())


# - - - - - - - - - - #


# Function to add a new user to the database if he is not registered yet
async def add_new_user_to_database(user_id, first_name, last_name):
    user_name = first_name
    if last_name is not None:
        user_name += f" {last_name[0:1]}."

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
            print(f'[!] There was an error in getting cursor: {e}')
            pass


# Store user strikes in the database
async def motivation(correct_strike, mistakes_strike, user_id, amount):
    try:
        if amount < 0:
            new_correct_strike = 0
            new_mistakes_strike = mistakes_strike + 1
        else:
            new_mistakes_strike = 0
            new_correct_strike = correct_strike + 1

        if new_mistakes_strike % 3 == 0 and new_mistakes_strike != 0:
            await main.send_motivation(user_id, False, new_mistakes_strike)
        elif new_correct_strike % 5 == 0 and new_correct_strike != 0:
            await main.send_motivation(user_id, True, new_correct_strike)

        return new_correct_strike, new_mistakes_strike

    except Error as e:
        print(f'[!] There was an error in updating motivation strike: {e}')
        pass


# Update user score in the database
async def update_score(user_id, amount, is_game):
    async with await get_cursor() as cur:
        try:
            query = "SELECT Score, Strike, Mistakes_Strike FROM EgeBotUsers WHERE TelegramUserID = %s"
            data_query = (user_id,)
            await cur.execute(query, data_query)
            current_score_table = await cur.fetchall()  # Get current score
            current_score = list(current_score_table)[0][0]

            new_score = current_score + amount  # Calculate new score
            if new_score < 0:
                new_score = 0

            if is_game:
                correct_strike = list(current_score_table)[0][1]
                mistakes_strike = list(current_score_table)[0][2]
                new_correct_strike, new_mistakes_strike = await motivation(correct_strike, mistakes_strike, user_id, amount)

                sql = "UPDATE EgeBotUsers SET Score = %s, Strike  = %s, Mistakes_Strike = %s WHERE TelegramUserID = %s"
                val = (new_score, new_correct_strike, new_mistakes_strike, user_id)
                await cur.execute(sql, val)
                await mydb.commit()  # Update DB Score

            else:
                sql = "UPDATE EgeBotUsers SET Score = %s WHERE TelegramUserID = %s"
                val = (new_score, user_id)
                await cur.execute(sql, val)
                await mydb.commit()  # Update DB Score

            return new_score

        except Error as e:
            print(f'[!] There was an error in updating user score: {e}')
            pass


# Get charts (statistics) of top 5 best users from the database
async def get_stats(user_id):
    async with await get_cursor() as cur:
        try:
            sql = "SELECT Name, Score FROM EgeBotUsers ORDER BY Score DESC LIMIT 5"
            await cur.execute(sql)
            chart_stats = list(await cur.fetchall())

            query = "SELECT Name, Score FROM EgeBotUsers WHERE TelegramUserID = %s"
            data_query = (user_id,)
            await cur.execute(query, data_query)
            temp_proxy = (await cur.fetchall())[0]
            chart_stats.append(temp_proxy)

            my_result = \
                '🏆 Топ игроков по очкам:\n' \
                f'\n🥇*{chart_stats[0][0]}* — `{chart_stats[0][1]}`' \
                f'\n🥈*{chart_stats[1][0]}* — `{chart_stats[1][1]}`' \
                f'\n🥉*{chart_stats[2][0]}* — `{chart_stats[2][1]}`' \
                f'\n▫️*{chart_stats[3][0]}* — `{chart_stats[3][1]}`' \
                f'\n▫️*{chart_stats[4][0]}* — `{chart_stats[4][1]}`' \
                f'\n\n*{chart_stats[5][0]}* (я) — `{chart_stats[5][1]}`'

            return my_result

        except Error as e:
            print(f'[!] There was an error in getting stats: {e}')
            pass


# Function to check referral code usage
async def CheckReferral(args, uid):
    async with await get_cursor() as cur:
        try:
            if int(args) != int(uid):
                query = "SELECT ReferralActivated FROM EgeBotUsers WHERE TelegramUserID = %s"
                data_query = (uid,)
                await cur.execute(query, data_query)
                IsActivated = (await cur.fetchall())[0][0]
                if IsActivated == 0:
                    sql = "UPDATE EgeBotUsers SET ReferralActivated = %s WHERE TelegramUserID = %s"
                    val = (1, uid)
                    await cur.execute(sql, val)
                    await mydb.commit()  # Update DB Score
                    await update_score(uid, 50, False)
                    await update_score(args, 50, False)
                    print(f'[v] {args} invited {uid}')
                    return True
                else:
                    return False
            else:
                return False

        except Error as e:
            print(f'[!] There was an error in activating referral: {e}')
            pass
