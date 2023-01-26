import speech_recognition as sr
from telethon import TelegramClient
import asyncio
import os
from telethon.errors import SessionPasswordNeededError, PasswordHashInvalidError
import json


config_file = open("config.json", "r").read()
config = json.loads(config_file)
peoples = {"мне": "me", "какушу": "@kakushigoto"} # name must be lower
queries = ["отправь", "ответь", "напиши", "отправить", "ответить"]


r = sr.Recognizer()


async def telegram_login(phone=config['phone_num']):
    try:
        os.listdir('./sessions/')
    except:
        os.mkdir('./sessions/')
    fss = f"./sessions/{config['phone']}.session"
    client_tg = TelegramClient(fss, config['api_id'], config['api_hash'], device_model='Model')
    await client_tg.connect()
    await client_tg.send_code_request(phone)
    try:
        await client_tg.sign_in(config['phone'], input('Telegram code: '))
    except SessionPasswordNeededError:
        try:
            await client_tg.sign_in(password=input('2fa code: '))
        except PasswordHashInvalidError:
            await client_tg.sign_in(password=input('2fa code: '))


def get_speech():
    with sr.Microphone(device_index=1) as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            mic_text = r.recognize_google(audio, language="ru-RU")
            if any([x in mic_text.lower() for x in queries]):
                return mic_text
            return False
        except sr.UnknownValueError:
            return False


def do_something(query):
    lower_query = query.lower()
    text = query.lower().split(" ")
    if any([x in text for x in queries]):
        this_case = [x for x in queries if x in text]
        to_who = lower_query.split(this_case[0])[1].split(" ")[1]
    else:
        print("not found keys")
        return
    message_text = lower_query.split(to_who)[1]
    message_text = message_text.replace("луна", "🌝", (len(message_text.split("луна"))))
    message_text = message_text.replace(" скобка", ")", (len(message_text.split("скобка"))))
    client.loop.run_until_complete(client.send_message(peoples[to_who.lower()], message_text))


try: # Пробуем авторизоваться, если есть сессия, указанная в конфиге
    client = TelegramClient(f"./sessions/{config['phone_num']}.session", config['api_id'], config['api_hash'])
    client.start()
except: # Если сессии нет, идём в авторизацию
    loop = asyncio.get_event_loop()
    loop.run_until_complete(telegram_login())

while True:
    value = get_speech()
    if value:
        try:
            do_something(value)
        except Exception as e:
            print(e)
