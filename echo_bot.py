import telebot


access_token = '1046713222:AAEx3BF0VMVfpOfUJMVydxyGq7xJtx2230U'
bot = telebot.TeleBot(access_token)

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
    bot.polling(none_stop=True)

