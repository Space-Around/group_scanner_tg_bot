import os
import sys
import config
import logging
import asyncio
import sqlite3
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsSearch


client = TelegramClient('anon', config.API_ID, config.API_HASH)

# conn = sqlite3.connect(config.DB_NAME, check_same_thread = False)
# cursor = conn.cursor()

# cursor.execute("CREATE TABLE IF NOT EXISTS users_cmd (user_id TEXT, cmd TEXT, data TEXT, result TEXT);")
# conn.commit()

async def check_user(client, user_ident):
    try:
        await client.start()
        return await client.get_entity(user_ident)        
    except:
        return None # None means that the user is not found in Telegram

async def find_user_in_group(client, user_ident, chat_id):
    try:
        await client.start()
        return await client.get_participants(chat_id, filter = ChannelParticipantsSearch(user_ident))
    except Exception as e:
        # print(e)
        return None # None means that the user is not found in group

async def iter_group(order, start_id, end_id, user_ident, tg_user_id):
    logging.info(str(order) + ": START")

    for i in range(start_id, end_id):
        if (-1001492565750 == i):
            print("here")
        result = await find_user_in_group(client, user_ident, i)
        # print(str(i) + ": " + str(result))
        if result:
            # cursor.execute("SELECT * FROM users_cmd WHERE user_id = ?;", (str(tg_user_id), ))
            # sql_result = cursor.fetchall()

            # if sql_result:
            #     if sql_result[0][3]:
            #         data = str(sql_result[0][3]) + ", " + str(i)
            #     else:
            #         data = str(i)

                # cursor.execute("UPDATE users_cmd SET data = ? WHERE user_id = ?;", (data , str(tg_user_id)))
                # conn.commit()

                logging.info(result)

        await asyncio.sleep(0.25)

    logging.info(str(order) + ": STOP")


if __name__ == '__main__':
    min_id = start_id = -1001600000000
    max_id = -1001300000000
    proccess_count = 8
    user_ident = ""
    # tg_user_id = int(sys.argv[1])
    tg_user_id = 503587779

    log_file = config.LOG_PATH + str(tg_user_id) + ".log"

    logging.basicConfig(filename = log_file, level = logging.INFO)

    # cursor.execute("UPDATE users_cmd SET pid = ? WHERE user_id = ?;", (str(os.getpid()), str(sys.argv[1])))
    # conn.commit()

    # cursor.execute("SELECT * FROM users_cmd WHERE user_id = ?;", (str(tg_user_id), ))
    # sql_result = cursor.fetchall()

    # user_ident = sql_result[0][2]

    step = int((max_id - min_id) / proccess_count)

    loop = asyncio.get_event_loop()

    for i in range(1, proccess_count + 1):
        end_id = start_id + step

        asyncio.ensure_future(iter_group(i, start_id,  end_id, "spacearound101", tg_user_id))

        start_id += step

    loop.run_forever()