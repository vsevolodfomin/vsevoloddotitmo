import requests
import config
import telebot
import datetime 
import html5lib
from bs4 import BeautifulSoup


bot = telebot.TeleBot(config.access_token)
web_pages = {}
week_list = ['/monday', '/tuesday', '/wednesday', '/thursday', '/friday', '/saturday']
visual_list = ['понедельник', 'вторник', 'среду', 'четверг', 'пятницу', 'субботу']


def get_page(group, week=''):
    if week:
        week = str(week) + '/'
    url = '{domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'.format(
        domain=config.domain,
        week=week,
        group=group)
    response = requests.get(url)
    web_page = response.text
    return web_page



def parse_schedule(web_page, day):
    day = f"{day}day"
    soup = BeautifulSoup(web_page, "html5lib")

    # Получаем таблицу с расписанием
    schedule_table = soup.find("table", attrs={"id": day})

    # Время проведения занятий
    times_list = schedule_table.find_all("td", attrs={"class": "time"})
    times_list = [time.span.text for time in times_list]

    # Место проведения занятий
    locations_list = schedule_table.find_all("td", attrs={"class": "room"})
    locations_list = [room.span.text for room in locations_list]

    # Аудитория
    rooms_list = schedule_table.find_all("td", attrs={"class": "room"})
    rooms_list = [room.dd.text for room in rooms_list]

    # Название дисциплин и имена преподавателей
    lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
    lessons_list = [lesson.text.split('\n') for lesson in lessons_list]
    lessons_list = [''.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list, rooms_list


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def get_schedule(message):
    """ Получить расписание на указанный день """
    try:
        weekday, week_number, group = message.text.split()
        if 0 <= int(week_number) <= 2:
            
            # Определяем день недели
            if weekday in week_list:
                day = week_list.index(weekday) + 1
            else:
                day = 1

            web_page = get_page(group, week_number)
            
            times_lst, locations_lst, lessons_lst, rooms_lst = \
                parse_schedule(web_page, day)
            
            resp = '<b> Расписание на '+ visual_list[day - 1] + ':\n\n</b>'
            for time, location, lession, rooms in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
                resp += '<b>{}</b>, {}, {} {}\n'.format(time, location, lession, rooms)
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Неделя может быть от 0 до 2")
    except AttributeError:
        bot.send_message(message.chat.id, "Такой группы нет")
    except ValueError:
        bot.send_message(message.chat.id, "Данные введены неверно или не полностью.")


@bot.message_handler(commands=['near'])
def get_near_lesson(message):
    """ Получить ближайшее занятие """
    try:
        _, group = message.text.split()
        
        today = datetime.datetime.now()
        day = today.isoweekday()
        now = datetime.datetime.now()
        #week_number = get_week()


        if int(datetime.datetime.today().strftime('%U')) % 2 == 1:
            week = 1
        else:
            week = 2
        web_page = get_page(group, str(week))


        times_lst, locations_lst, lessons_lst, rooms_lst = \
            parse_schedule(web_page, day)
        resp = ''
        
        for time, location, lession, rooms in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
            hour, minute = time[:5].split(":")
            lesson_time = datetime.time(int(hour), int(minute))
            if lesson_time >= today.time():
                resp += '<b>{}</b>, {}, {} {}\n'.format(time, location, lession, rooms)
                break
        if len(resp) != 0:
            bot.send_message(message.chat.id, resp, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Нет занятий на сегодня")

    except AttributeError:
        bot.send_message(message.chat.id, "Такой группы нет")
    except ValueError:
        bot.send_message(message.chat.id, "Данные введены неверно или не полностью.")


@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
    """ Получить расписание на следующий день """
    try:
        _, group = message.text.split()
        
        if int(datetime.datetime.today().strftime('%U')) % 2 == 1:
            week = 1
        else:
            week = 2
       
        web_page = get_page(group, str(week))
        
        today = datetime.datetime.now()
        day = today.isoweekday() + 1
        if day == 7 or day == 8:
            day = 1

        schedule = parse_schedule(web_page, day)

        if not schedule:
            bot.send_message(message.chat.id, 'Данные введены неверно или завтра у группы нет занятий')
            return None
        
        times_lst, locations_lst, lessons_lst, rooms_lst = schedule
        resp = '<b>Расписание на завтра:\n\n</b>'
        for time, location, lession, rooms in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
            resp += '<b>{}</b>, {}, {}, {}\n'.format(time, location, lession, rooms)

        bot.send_message(message.chat.id, resp, parse_mode='HTML')
    except AttributeError:
        bot.send_message(message.chat.id, "Такой группы нет")
    except:
        bot.send_message(message.chat.id, 'Данные введены неверно или не полностью.')
        return None


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
    """ Получить расписание на всю неделю для указанной группы """
    try:
        _, week_number, group = message.text.split()
        if 0 <= int(week_number) <= 2:
            
            web_page = get_page(group, week_number)
            
            for day in range(1, 7):
                try:
                    times_lst, locations_lst, lessons_lst, rooms_lst = \
                        parse_schedule(web_page, day)
                    
                    resp = '<b>  Расписание на '+ visual_list[day - 1] + ':\n\n</b>'
                    for time, location, lession, rooms in zip(times_lst, locations_lst, lessons_lst, rooms_lst):
                        resp += '<b>{}</b>, {}, {}, {}\n'.format(time, location, lession, rooms)
                    bot.send_message(message.chat.id, resp, parse_mode='HTML')
                except AttributeError:
                    bot.send_message(message.chat.id, '<b>Расписание на '+ visual_list[day - 1] + ':\n\n</b>' + 'Занятий нет', parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Неделя может быть от 0 до 2")
    except ValueError:
        bot.send_message(message.chat.id, "Данные введены неверно или не полностью.")


if __name__ == '__main__':
    bot.polling(none_stop=True) 