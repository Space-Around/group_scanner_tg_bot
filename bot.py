import os
import sys
import config
import psutil
import signal
import telebot
import sqlite3
import subprocess

bot = telebot.TeleBot(config.TOKEN)

conn = sqlite3.connect(config.DB_NAME, check_same_thread = False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users_cmd (user_id TEXT, cmd TEXT, data TEXT, result TEXT, pid TEXT);")
conn.commit()


@bot.message_handler(commands = ['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hi! Send me user's name (@example) or id (100123123) on Telegram and you'll get list of user's groups in return")


@bot.message_handler(commands = ['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Send me the name (@example) or id (100123123) of the user on Telegram")


@bot.message_handler(commands = ['status'])
def send_status(message):
    cursor.execute("SELECT * FROM users_cmd WHERE user_id = ?;", (str(message.from_user.id), ))
    sql_result = cursor.fetchall()

    if sql_result:
        for row in sql_result:
            if row[3]:
                bot.send_message(message.chat.id, row[3])
                
            else:
                bot.send_message(message.chat.id, "No results, active search on request: " + row[2])
    else:
        bot.send_message(message.chat.id, "There is no search query. Use the command /start")
    
    
@bot.message_handler(commands = ['cancel'])
def cancel(message):
    cursor.execute("SELECT * FROM users_cmd WHERE user_id = ?;", (str(message.from_user.id), ))
    sql_result = cursor.fetchall()

    if sql_result:
        for proc in psutil.process_iter():
            if proc.pid == int(sql_result[0][4]):
                proc.kill()

        bot.send_message(message.chat.id, "The process has been successfully stopped")

        cursor.execute("DELETE FROM users_cmd WHERE user_id = ?;", (str(message.from_user.id), ))
        conn.commit()


@bot.message_handler(commands = ['search'])
def send_search(message):
    cursor.execute("SELECT * FROM users_cmd WHERE user_id = ?;", (str(message.from_user.id), ))
    sql_result = cursor.fetchall()

    if sql_result:
        if sql_result[0][2]:
            bot.send_message(message.chat.id, "You can have only one active search, you can use the command /cancle to cancel the search, after canceling you can make a new search with the command /search")
        else:
            bot.send_message(message.chat.id, "Send me the name (@example) or id (100123123) of the user on Telegram")
    else:
        bot.send_message(message.chat.id, "Send me the name (@example) or id (100123123) of the user on Telegram")
        cursor.execute("INSERT INTO users_cmd VALUES (?, ?, ?, ?, ?);", (str(message.from_user.id), "search", "", "", ""))
        conn.commit()


@bot.message_handler(func = lambda message: True)
def get_data(message):
    cursor.execute("SELECT * FROM users_cmd WHERE user_id = ?;", (str(message.from_user.id), ))
    sql_result = cursor.fetchall()

    if sql_result:
        cursor.execute("UPDATE users_cmd SET data = ? WHERE user_id = ?;", (message.text, str(message.from_user.id)))
        conn.commit()

        bot.send_message(message.chat.id, "Beginning a search...\nUse /status to find out the status of your search")

        subprocess.run(["python", "./scanner.py", str(message.from_user.id)])


bot.polling()