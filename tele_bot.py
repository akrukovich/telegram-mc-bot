import telebot, types
from telebot import types
import os
import logging
import parser
import db


parser = parser.ImdbParser()

logger = telebot.logger

telebot.logger.setLevel(logging.DEBUG)
TOKEN = '856121961:AAHax7gKb-iDJ9Pl-nNtZKV5VgrEjg5QcNE'

bot = telebot.TeleBot(TOKEN)

answers = ('Random 5 movies to watch', 'Add/Update/Delete/All a list of tv shows')


@bot.message_handler(commands=['start', 'help'])
@bot.edited_message_handler(commands=['start', 'help'])
def command_handler(message: types.Message):

    if message.text == '/start':
        db.add_user(message.from_user.id, message.from_user.first_name)

        bot.send_sticker(message.chat.id,
                         'CAACAgEAAxkBAAMaXjnCIjuhV6-wpLsKtDRksUHERd8AAn0AA8WInATR-Nr5m7ajfxgE'
                         )

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton(answers[0])
        item2 = types.KeyboardButton(answers[1])

        markup.add(item1, item2)
        bot.send_message(message.chat.id, 'Evil Morty bot wants to have some fun ...', reply_markup=markup)

    else:
        bot.send_message(message.chat.id, """If you don't know what you want to watch then pick on Random 5 movies to watch.
But if you need update your tv shows data then the right button is your choice.""" )


@bot.message_handler(content_types=['text'])
def reply_on_markup(message: types.Message):

    if message.text == answers[0]:
        reply = parser.get_movies_string(True)
        bot.send_message(message.chat.id, reply)

    elif message.text == answers[1]:
        murkup = types.InlineKeyboardMarkup(row_width=4)

        item1 = types.InlineKeyboardButton('Add tv show', callback_data='add')
        item2 = types.InlineKeyboardButton('Update', callback_data='update')
        item3 = types.InlineKeyboardButton('Delete', callback_data='delete')
        item4 = types.InlineKeyboardButton('All', callback_data='all')

        murkup.add(item1, item2, item3, item4)

        bot.send_message(message.chat.id, "Don't be like Rick ... ", reply_markup=murkup)

    else:
        bot.send_message(message.chat.id, 'I dunno bro, this looks like kek ...')


@bot.callback_query_handler(func=lambda call: True)
def add_show(call):
    try:
        if call.message:

            if call.data == 'add':
                msg = bot.send_message(call.message.chat.id,
                                       'add your tv show in this pattern "title-season-episode" .')
                bot.register_next_step_handler(msg, add_show)

            elif call.data == 'delete':
                msg = bot.send_message(call.message.chat.id, 'delete your tv show in this pattern "title" .')
                bot.register_next_step_handler(msg, delete_show)

            elif call.data == 'update':
                msg = bot.send_message(call.message.chat.id,
                                       'update your tv show in this pattern "title-season-episode" .')
                bot.register_next_step_handler(msg, update_show)

            elif call.data == 'all':
                reply = get_all_shows(call.from_user.id)
                bot.send_message(call.message.chat.id, reply, parse_mode='html')

    except Exception as e:
        bot.send_message(call.message.chat.id, e)


@bot.message_handler(content_types=['sticker'])
def say(message: types.Message):

    bot.send_sticker(message.chat.id, data='CAACAgEAAxkBAAMaXjnCIjuhV6-wpLsKtDRksUHERd8AAn0AA8WInATR-Nr5m7ajfxgE')


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def add_show(message: types.Message):

    reply = ''
    try:
        data = message.text.split('-')

        int(data[1])
        int(data[2])

        if len(data) > 3:
            raise ValueError

        db.add_show(data[0], message.from_user.id, data[1], data[2])

        reply =  f'Added {data[0]} ... '

    except Exception as e:
        reply = f'Not valid format! must bee title-season-episode'

    finally:
        bot.send_message(message.chat.id, reply)


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def update_show(message: types.Message):

    reply = ''

    try:
        data = message.text.split('-')

        int(data[1])
        int(data[2])

        if len(data) > 3 :
            raise ValueError

        db.update_show(data[0], message.from_user.id, data[1], data[2])

        reply = f'Updated {data[0]} ... '

    except Exception as e:
        reply = f'Not valid format! must bee title-season-episode'

    finally:
        bot.send_message(message.chat.id, reply)


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types=['text'])
def delete_show(message: types.Message):

    reply = ''
    data = message.text.strip()
    try:
        db.delete_show(data, message.from_user.id)
        reply = f'Deleted {data}'

    except Exception as e:
        reply = 'Not found or invalid format!'

    finally:
        bot.send_message(message.chat.id, reply)


def get_all_shows(user_id):

    reply = ''
    shows = db.get_all_shows(user_id)

    if not shows:
        reply = 'I am scared! It\'s empty.'

    else:
        for show in shows:
            string = f'''Show - {show[2]}\nSeason - {show[3]}\nEpisode - {show[4]}\n\n'''
            reply = ''.join([reply, string])

    return reply


bot.polling()
