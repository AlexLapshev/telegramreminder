import telebot
from telebot.util import async_dec
from database import Event, session
from time import sleep
from datetime import datetime, timedelta
from settings import token, chat_id, bot_name


bot = telebot.TeleBot(token)

title = ''
date = ''
days = [
	'Пн',
	'Вт',
	'Ср',
	'Чт',
	'Пт',
	'Сб',
	'Вс',
	]


@bot.message_handler(commands=['start', 'remove', 'timetable', 'help', 'timetable_all', ])
@async_dec()
def get_text_message(message):
	if message.chat.id != chat_id:
		bot.send_message(message.chat.id, 'Вам недоступен этот бот.')
	else:
		start(message)


def start(message):
	if message.text == '/start' + bot_name:
		bot.send_message(chat_id, 'Введи событие')
		bot.register_next_step_handler(message, get_event)
	elif message.text == '/timetable' + bot_name:
		timetable()
	elif message.text == '/help' + bot_name:
		bot.send_message(chat_id, 'Напиши /start, /timetable, /timetable_all или /remove')
	elif message.text == '/timetable_all' + bot_name:
		timetable_all()
	elif message.text == '/remove' + bot_name:
		timetable_all()
		bot.register_next_step_handler(message, remove)
	else:
		bot.send_message(chat_id, 'Напиши /start, /timetable или /timetable_all')


def remove(message):
	try:
		event = session.query(Event).filter_by(id=int(message.text)).first()
		session.delete(event)
		session.commit()
		bot.send_message(chat_id, 'Событие успешно удалено.')
	except Exception as e:
		print(e)
		bot.send_message(chat_id, 'Что-то пошло не так.')


def timetable():
	for ev in Event.get_future():
		bot.send_message(chat_id, ev)


def timetable_all():
	for ev in Event.get_all():
		bot.send_message(chat_id, '{} {}'.format(ev.id, ev))


def get_event(message):
	global title
	title = message.text
	bot.send_message(chat_id, 'Введи дату в формате DD-MM-YYYY-HH-MM')
	bot.register_next_step_handler(message, get_date)


def get_date(message):
	global date
	date = message.text
	try:
		date = datetime.strptime(date, "%d-%m-%Y-%H-%M").replace(second=0)
		day = days[datetime.weekday(date)]
		new_event = Event(title, date)
		session.add(new_event)
		session.commit()
		bot.send_message(chat_id, 'Событие: {} \nВремя: {} {}'.format(title, day, str(date)[:-3]))
	except Exception as e:
		print(e)
		bot.send_message(chat_id, 'Неверный формат даты, введи /start или /timetable.')


@async_dec()
def cycle_db():
	while True:
		for elem in Event.get_all():
			now = datetime.now().replace(second=0, microsecond=0)

			try:
				date = datetime.strptime(elem.date, "%Y-%m-%d %H:%M:%S").replace(second=0)

				if (date - timedelta(hours=3)) == now:
					reminder(elem, date)
					sleep(60)

			except Exception as e:
				print(e)


def reminder(event, date):
	day = days[datetime.weekday(date)]
	bot.send_message(chat_id, 'Событие: {}\nВремя: {} {}'.format(event.title, day, event.date[:-3]))


if __name__ == '__main__':
	cycle_db()
	bot.polling(none_stop=True)
