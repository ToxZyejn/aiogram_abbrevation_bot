import json
import aiogram
import asyncio
from aiogram import Bot, Dispatcher, F
import aioschedule
from aiogram.filters import Command
from aiogram.types import Message, Sticker, ReplyKeyboardMarkup
import logging
import datetime
from keyboards import markup_daily

logging.basicConfig(level=logging.INFO)
bot = Bot('TOKEN')
dp = Dispatcher()

with open('abbreviaturka.json', 'r') as file:
    abbreviations = json.load(file)

user_state = {}


def set_user_state(user_id, state):
    user_state[user_id] = state


def get_user_state(user_id):
    return user_state.get(user_id, None)


# Константы для состояний
STATE_WAITING_FOR_DAILY = "waiting_for_daily"


@dp.message(Command('start'))  # декоратор, который обрабатывает команды и выдает какой-либо заданный ответ
async def start_bot(message):
    await bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}! Я могу помочь тебе с расшифровкой аббревиатур.')


@dp.message(Command('help'))
async def helper(message: Message):
    await bot.send_message(message.chat.id,
                     'Я могу помочь тебе расшифровать аббревиатуру. Если я ее не знаю, то скоро выучу!')


@dp.message(Command('daily'))
async def send_calls(message: Message):
    await bot.send_message(message.chat.id, f'Прошу, {message.from_user.first_name}, выбери свое СПО', reply_markup=markup_daily())


# Декоратор для обработки нажатия кнопки "Дейли ПАИП"
@dp.message(F.text == "Дейли DAILY")
async def request_daily_info(message):
    set_user_state(message.chat.id, STATE_WAITING_FOR_DAILY)
    await bot.send_message(message.chat.id,
                     f"Пожалуйста, {message.from_user.first_name}, отправьте номера задач для Daily отчета в формате: \nВчера: TTT-xxxx, TTT-zzzz \nСегодня: TTT-yyyy, TTT-tttt")

MyFilter = func = lambda message: get_user_state(message.chat.id) == STATE_WAITING_FOR_DAILY


# Создание утреннего отчета на основе введенного пользователем сообщения
@dp.message(MyFilter)
async def create_daily_report(message: Message):
    set_user_state(message.chat.id, None)
    try:
        today_date = datetime.date.today().strftime("%d%m%Y")
        tasks = message.text.strip().split("\n")

        if len(tasks) >= 2:
            yesterday_tasks = tasks[0].split(": ")[1].split(",")  # Разделяем задачи по запятой
            today_tasks = tasks[1].split(": ")[1].split(",")

            daily_report = f"#daily_{today_date}\nа) Вчера в работе было: \n"
            daily_report += ''.join([f"<a href='https://YOUR_JIRA_URL/browse/{task.strip()}'>задача {task.strip()}</a>\n" for task in yesterday_tasks if task])

            daily_report += f"б) Сегодня буду заниматься: \n"
            daily_report += ''.join([f"<a href='https://YOUR_JIRA_URL/browse/{task.strip()}'>задача {task.strip()}</a>\n" for task in today_tasks if task])

            daily_report += "в) Проблем нет\n"

            await bot.send_message(message.chat.id, daily_report, parse_mode='HTML', disable_web_page_preview=True)
    except (IndexError, ValueError):
        await bot.send_message(message.chat.id, "Произошла ошибка при обработке введенных данных. Убедитесь, что вы ввели информацию корректно и использовали запятые для разделения задач.")


@dp.message()
async def echo(message):
    text = message.text.lower()  # Приводим введенный текст к нижнему регистру

    found = False
    for abbreviation, decryption in abbreviations.items():
        if text.lower() == abbreviation.lower():  # Сравниваем введенный текст и аббревиатуру в нижнем регистре
            sticker_message = await bot.send_sticker(message.from_user.id, sticker='CAACAgQAAxkBAAELUOxlv7BqNmVG5YVIDIqFcXwzAAG_7FgAAlABAAKoISEGsb3xtc3phKI0BA')
            await asyncio.sleep(2)
            await bot.delete_message(chat_id=message.chat.id, message_id=sticker_message.message_id)
            await bot.send_message(message.chat.id, decryption)
            found = True
            break

    if not found:
        await bot.send_message(message.chat.id, 'К сожалению, я не знаю расшифровки этой аббревиатуры.')


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
