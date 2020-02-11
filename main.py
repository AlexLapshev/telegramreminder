import telebot
from telebot.util import async_dec
from database import Event, session
from time import sleep
from datetime import datetime, timedelta

token = '1009398022:AAE3YgCc_nDJkDF1__RWfiic6ak8IldaYa0'
bot = telebot.TeleBot(token)


# user_list = [@lapsha666 , @Сак, @Mrachek, @Boris_Rasierklinge]
title = ''
date = ''
chat_id = 382210467


@bot.message_handler(commands=['start', 'timetable', 'help', 'timetable_all'])
@async_dec()
def get_text_message(message):
	if message.text == '/start':
		bot.send_message(message.from_user.id, "Введи событие")
		bot.register_next_step_handler(message, get_event)
	elif message.text == '/timetable':
		timetable(message)
	elif message.text == '/help':
		bot.send_message(message.from_user.id, 'Напиши /start, /timetable или /timetable_all')
	elif message.text == '/timetable_all':
		timetable_all(message)

	else:
		bot.send_message(message.from_user.id, 'Напиши /start, /timetable или /timetable_all')


def timetable(message):
	for ev in Event.get_future():
		bot.send_message(message.from_user.id, ev)


def timetable_all(message):
	for ev in Event.get_all():
		bot.send_message(message.from_user.id, ev)


def get_event(message):
	global title
	title = message.text
	bot.send_message(message.from_user.id, 'Введи дату в формате DD-MM-YYYY-HH-MM')
	bot.register_next_step_handler(message, get_date)


def get_date(message):
	global date
	date = message.text
	try:
		date = datetime.strptime(date, "%d-%m-%Y-%H-%M").replace(second=0)
		new_event = Event(title, date)
		session.add(new_event)
		session.commit()
		bot.send_message(message.from_user.id, 'Событие: {} \nВремя: {}'.format(title, str(date)[:-3]))
	except Exception as e:
		print(e)
		bot.send_message(message.from_user.id, 'Неверный формат даты, введи /start или /timetable.')


@async_dec()
def cycle_db():
	while True:
		for elem in Event.get_all():
			now = datetime.now().replace(second=0, microsecond=0)
			try:
				date = datetime.strptime(elem.date, "%Y-%m-%d %H:%M:%S").replace(second=0)
				if (date - timedelta(hours=3)) == now:
					reminder(elem)
					sleep(60)

			except Exception as e:
				print(e)


def reminder(event):
	bot.send_message(382210467, 'Событие: {}\nДата: {}'.format(event.title, event.date[:-3]))


if __name__ == '__main__':
	cycle_db()
	bot.polling(none_stop=True)
