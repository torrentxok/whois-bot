#from asyncio.windows_events import NULL
from datetime import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

import asyncio
import schedule
import time

import prettytable

from messages import start_message, help_message, commands_message, whois_info_msg
from sql_query import validation

import re

from keyboard import kb_whois, inline_kb_whois

import whois

import os

import psycopg2

bot = Bot(token = os.getenv('TOKEN'))
dp = Dispatcher(bot)

host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')
db_name = os.getenv('DB_NAME')


async def scheduled(wait_for):
  while True:
    await asyncio.sleep(wait_for)
    now_time = datetime.now()
    registration_time = datetime.now().strftime("%Y-%m-%d")
    now_time = now_time.strftime("%H:%M")
    if now_time == "14:01":
        try:
            conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
            print("[INFO] Connected to database")
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT domain_name, creation_date, expiration_date FROM domains")
            record = cursor.fetchall()
            if len(record) == 0:
                print("[INFO] База доменов пуста")
            else:
                for domain in record:
                    try:
                        whois_query = whois.query(domain[0])
                        print(whois_query.__dict__)
                        whois_query = whois_query.__dict__
                        if type(whois_query['creation_date']) == list:
                            creation_date = whois_query['creation_date'][0]
                        else:
                            creation_date = whois_query['creation_date']
                        
                        if type(whois_query['expiration_date']) == list:
                            expiration_date = whois_query['expiration_date'][0]
                        else:
                            expiration_date = whois_query['expiration_date']
                        # print(type(expiration_date))
                        # print("----------")
                        # print(type(domain[2]))

                        flag_creation_date = False
                        flag_expiration_date = False
                        if domain[1] != creation_date and domain[1] != None: flag_creation_date = True
                        if domain[2] != expiration_date: flag_expiration_date = True
                        print(flag_creation_date, flag_expiration_date)

                        if flag_creation_date or flag_expiration_date:
                            cursor.execute(f"UPDATE domains SET creation_date={validation(creation_date)}, expiration_date={validation(expiration_date)} WHERE domain_name={validation(domain[0])}")
                            conn.commit()
                            cursor.execute(f"SELECT id_user FROM user_domain WHERE domain_name = {validation(domain[0])}")
                            users = cursor.fetchall()
                            if len(users) != 0:
                                for i in users:
                                    try:
                                        await bot.send_message(i[0], f"Произошли изменения в домене: {domain[0]}\n\nCreation date:\n{creation_date}\n\nExpiration date:\n{expiration_date}")
                                        print("[INFO] Сообщение отправлено")
                                        time.sleep(1)
                                    except:
                                        print("[INFO] Error send_message")

                        if domain[1] != creation_date and domain[1] == None:
                            cursor.execute(f"UPDATE domains SET creation_date={validation(creation_date)}, expiration_date={validation(expiration_date)} WHERE domain_name={validation(domain[0])}")
                            conn.commit()
                            cursor.execute(f"SELECT id_user FROM user_domain WHERE domain_name = {validation(domain[0])}")
                            users = cursor.fetchall()
                            if len(users) != 0:
                                for i in users:
                                    try:
                                        await bot.send_message(i[0], f"Домен {domain[0]} зарегестрирован!\n\nCreation date:\n{creation_date}\n\nExpiration date:\n{expiration_date}")
                                        print("[INFO] Сообщение отправлено")
                                        time.sleep(1)
                                    except:
                                        print("[INFO] Error send_message")

                        if registration_time == domain[1].strftime("%Y-%m-%d"):
                            cursor.execute(f"SELECT id_user FROM user_domain WHERE domain_name = {validation(domain[0])}")
                            users = cursor.fetchall()
                            if len(users) != 0:
                                for i in users:
                                    try:
                                        await bot.send_message(i[0], f"Домен {domain[0]} сегодня должен освободиться!\n\nCreation date:\n{creation_date}\n\nExpiration date:\n{expiration_date}")
                                        print("[INFO] Сообщение отправлено")
                                        time.sleep(1)
                                    except:
                                        print("[INFO] Error send_message")

                    except Exception as ex:
                        print("[INFO] Ошибка whois запроса")
                        print(ex)
        except:
            print("[INFO] Ошибка соединения")


def insert_new_user(message):
    try:
        conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
        print("[INFO] Connected to database")
        id_user = message.from_user.id
        is_bot = message.from_user.is_bot
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        language_code = message.from_user.language_code
        
        first_name = validation(first_name)
        last_name = validation(last_name)
        username = validation(username)
        language_code = validation(language_code)

        cursor = conn.cursor()
        print("[INFO] Cursor connected")
        cursor.execute(f"SELECT id_telegram FROM telegram_users WHERE id_telegram = {id_user}")
        record = cursor.fetchall()
        if len(record) == 0:
            cursor.execute(f"INSERT INTO telegram_users VALUES ({id_user}, {is_bot}, {first_name}, {last_name}, {username}, {language_code})")
            conn.commit()
            print("[INFO] Query commited")
        else:
            print("[INFO] Запись уже существует")
    except:
        print("[INFO] Error connection")
    finally:
        cursor.close()
        conn.close()


async def insert_user_domain(message, domain_name, whois_info):
    try:
        conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
        print("[INFO] Connected to database")
        id_user = message.from_user.id

        domain_name = validation(domain_name)

        cursor = conn.cursor()
        print("[INFO] Cursor connected")
        cursor.execute(f"SELECT * FROM user_domain WHERE id_user = {id_user} and domain_name = {domain_name}")
        record = cursor.fetchall()
        flag_insert_domain = False
        if len(record) == 0:
            cursor.execute(f"INSERT INTO user_domain(id_user, domain_name) VALUES ({id_user}, {domain_name})")
            flag_insert_domain = True
        else:
            print("[INFO] Запись уже существует")
            await bot.send_message(message.from_user.id, f"Домен {domain_name} был добавлен ранее!")
        insert_new_domain(domain_name, whois_info)
        conn.commit()
        if flag_insert_domain:
            await bot.send_message(message.from_user.id, f"Домен {domain_name} успешно добавлен!")
    except:
        print("[INFO] Error connection")
    finally:
        cursor.close()
        conn.close()


def insert_new_domain(domain_name, whois_info):
    try:
        connection = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
        print("[INFO] Connected to database")
        
        cursor = connection.cursor()
        print("[INFO] Cursor connected")
        cursor.execute(f"SELECT * FROM domains WHERE domain_name = {domain_name}")
        record = cursor.fetchall()
        if len(record) == 0:
            if whois_info == None:
                cursor.execute(f"INSERT INTO domains(domain_name, name_from_json, domain_info, creation_date, expiration_date) VALUES ({domain_name}, NULL, NULL, NULL, NULL)")
                connection.commit()
            else:
                if type(whois_info['name']) == list:
                    whois_domain_name = [i for i in whois_info['name']]
                    for i in range(len(whois_domain_name)):
                        whois_domain_name[i] = f'"{whois_domain_name[i]}"'
                    whois_domain_name = ', '.join(whois_domain_name)
                else:
                    whois_domain_name = whois_info['name']
                whois_domain_name = '{'+ whois_domain_name + '}'

                if type(whois_info['creation_date']) == list:
                    creation_date = str(whois_info['creation_date'][0])
                else:
                    creation_date = str(whois_info['creation_date'])
                
                if type(whois_info['expiration_date']) == list:
                    expiration_date = str(whois_info['expiration_date'][0])
                else:
                    expiration_date = str(whois_info['expiration_date'])

                whois_domain_name = validation(whois_domain_name)
                creation_date = validation(creation_date)
                expiration_date = validation(expiration_date)
                #whois_info = validation(whois_info)
                #whois_info = f'"{whois_info}"'
                whois_info = validation(str(whois_info).replace("'", '"'))
                print(whois_domain_name, creation_date, expiration_date, whois_info, sep='\n')
                cursor.execute(f"INSERT INTO domains(domain_name, name_from_json, domain_info, creation_date, expiration_date) VALUES ({domain_name}, {whois_domain_name}, {whois_info}, {creation_date}, {expiration_date})")
                connection.commit()
        else:
            print("[INFO] Домен уже существует в базе")
    except psycopg2.Error as e:
        print("[INFO] Error insert domain")
        print(e.pgerror)
    finally:
        cursor.close()
        connection.close()

async def startup_on(_):
    print('Бот в вышел в онлайн')





@dp.message_handler(commands='start')
@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/start\s*')
async def command_start(message : types.Message):
    try:
        insert_new_user(message)
        # print(type(id_user), type(is_bot), type(first_name), type(last_name), type(username), type(language_code))
        # print(id_user, is_bot, first_name, last_name, username, language_code)
    except:
        print("[INFO] User not added")
    try:
        await bot.send_message(message.from_user.id, start_message(), reply_markup=kb_whois)
    except:
        await message.reply(f'Ошибка! Напишите боту (@{(await bot.get_me()).username}) в личные сообщения')






@dp.message_handler(commands='help')
@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/help\s*')
async def command_list(message : types.Message):
    try:
        insert_new_user(message)
    except:
        print("[INFO] User not added")

    try:
        await bot.send_message(message.from_user.id, help_message(), reply_markup=kb_whois)
    except:
        await message.reply('Общение с ботом в ЛС!')







@dp.message_handler(commands='commands')
@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/commands\s*')
async def command_whois(message : types.Message):
    try:
        insert_new_user(message)
    except:
        print("[INFO] User not added")
    
    try:
        await bot.send_message(message.from_user.id, commands_message(), reply_markup=inline_kb_whois)
    except:
        await message.reply('Общение с ботом в ЛС!')






@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/find\s*\w*\s*') 
@dp.message_handler(regexp='\s*/find\s*\w*\s*')
async def find_domain(message : types.Message):
    domain_name = message.text[message.text.find('find')+4:].strip()
    if len(domain_name.split())!=1:
        await bot.send_message(message.from_user.id, 'Неверное имя домена!\nИнструкция по использованию бота:\n/help')
    else:
        try:
            insert_new_user(message)
        except:
            print("[INFO] User not added")

        try:
            #информация о домене
            domain_info = whois.query(domain_name).__dict__
            print(domain_info)
            if type(domain_info['name']) == list:
                whois_domain_name = '\n'.join([i for i in domain_info['name']])
            else:
                whois_domain_name = domain_info['name']
            
            if type(domain_info['creation_date']) == list:
                creation_date = str(domain_info['creation_date'][0])
            else:
                creation_date = str(domain_info['creation_date'])
            
            if type(domain_info['expiration_date']) == list:
                expiration_date = str(domain_info['expiration_date'][0])
            else:
                expiration_date = str(domain_info['expiration_date'])

            await bot.send_message(message.from_user.id, whois_info_msg(whois_domain_name, creation_date, expiration_date))
        except Exception as ex:
            print(ex)
            await bot.send_message(message.from_user.id, 'Произошла ошибка!\nПопробуйте еще раз или введите другое имя домена\n\nИнструкция доступна по запросу:\n/help' )





@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/add\s*\w*\s*') 
@dp.message_handler(regexp='\s*/add\s*\w*\s*')
async def add_domain(message : types.Message):
    domain_name = message.text[message.text.find('add')+3:].strip()
    if len(domain_name.split())!=1:
        await bot.send_message(message.from_user.id, 'Неверное имя домена!\nИнструкция по использованию бота:\n/help')
    else:
        insert_user_flag = True
        try:
            insert_new_user(message)
        except:
            print("[INFO] User not added")
            insert_user_flag = False
        
        if insert_user_flag:
            try:
                domain_info = whois.query(domain_name).__dict__
                if type(domain_info['name']) == list:
                    whois_domain_name = '\n'.join([i for i in domain_info['name']])
                else:
                    whois_domain_name = domain_info['name']
                
                if type(domain_info['creation_date']) == list:
                    creation_date = str(domain_info['creation_date'][0])
                else:
                    creation_date = str(domain_info['creation_date'])
                
                if type(domain_info['expiration_date']) == list:
                    expiration_date = str(domain_info['expiration_date'][0])
                else:
                    expiration_date = str(domain_info['expiration_date'])

                if domain_info['name'] != None:
                    await bot.send_message(message.from_user.id, f"По домену {domain_name} была найдена информация!")
                    await bot.send_message(message.from_user.id, whois_info_msg(whois_domain_name, creation_date, expiration_date))
                else:
                    await bot.send_message(message.from_user.id, f"Домен {domain_name} не зарегестрирован!")
                    domain_info = None
            except:
                await bot.send_message(message.from_user.id, f"Домен {domain_name} не зарегестрирован!")
                domain_info = None
            
            try:
                await insert_user_domain(message, domain_name, domain_info)
            except:
                print("[INFO] Domain not added")
                await bot.send_message(message.from_user.id, "Произошла ошибка!\nДомен не удалось добавить.")

        else:
            await bot.send_message(message.from_user.id, 'Произошла ошибка!\nПопробуйте снова или введите другое имя домена.')





@dp.message_handler(commands='list')
@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/list\s*')
async def command_start(message : types.Message):
    insert_flag = True
    id_user = message.from_user.id
    try:
        insert_new_user(message)
    except:
        print("[INFO] User not added")
        insert_flag = False
    if insert_flag:
        try:
            conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
            cursor = conn.cursor()
            print("[INFO] Cursor connected")
            #cursor.execute(f"SELECT domain_name FROM user_domain WHERE id_user = {id_user}")
            cursor.execute(f"SELECT domains.domain_name, expiration_date FROM user_domain INNER JOIN domains ON user_domain.domain_name = domains.domain_name WHERE id_user = {id_user} ORDER BY expiration_date DESC")
            record = cursor.fetchall()
            if len(record) == 0:
                await bot.send_message(message.from_user.id, "На данный момент добавленых доменов нет!")
            else:
                #list_message = '\n'.join([i[0] for i in record])
                
                table = prettytable.PrettyTable(['DOMAIN', 'EXPIRATION'])
                table.align['DOMAIN'] = 'l'
                table.align['EXPIRATION'] = 'l'


                for i in record:
                    table.add_row([f'{i[0]}', f'{str(i[1])[:10]}'])
                    
                await bot.send_message(message.from_user.id, f"Список добавленных доменов:\n<pre>{table}</pre>", parse_mode=types.ParseMode.HTML)
        except:
            print("[INFO] Error")
    else:
        await bot.send_message(message.from_user.id, 'Произошла ошибка!')






@dp.message_handler(regexp='\s*@torrentxok_testbot\s*/delete\s*\w*\s*') 
@dp.message_handler(regexp='\s*/delete\s*\w*\s*')
async def add_domain(message : types.Message):
    domain_name = message.text[message.text.find('delete')+6:].strip()
    insert_flag = True
    id_user = message.from_user.id
    try:
        insert_new_user(message)
    except:
        print("[INFO] User not added")
        insert_flag = False
    if insert_flag:
        try:
            conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
            cursor = conn.cursor()
            print("[INFO] Cursor connected")
            domain_name = validation(domain_name)
            cursor.execute(f"SELECT * FROM user_domain WHERE id_user = {id_user} AND domain_name = {domain_name}")
            record = cursor.fetchall()
            if len(record) == 0:
                await bot.send_message(message.from_user.id, f"Домен {domain_name} нет среди ваших доменов!")
            else:
                cursor.execute(f"DELETE FROM user_domain WHERE id_user = {id_user} AND domain_name = {domain_name}")
                conn.commit()
                print("[INFO] Domain deleted")
                await bot.send_message(message.from_user.id, f"Домен {domain_name} удален!")
        except:
            print("[INFO] Error delete domain")
    else:
        await bot.send_message(message.from_user.id, 'Произошла ошибка!')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(30))
    executor.start_polling(dp, skip_updates=True, on_startup=startup_on)


