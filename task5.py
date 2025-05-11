from datetime import datetime
import pytz

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

from config import TOKEN, GROUP_ID

WEEKDAYS = {1: 'Понедельник',
            2: 'Вторник',
            3: 'Среда',
            4: 'Четверг',
            5: 'Пятница',
            6: 'Суббота',
            7: 'Воскресенье'}


def main():
    token, group_id = TOKEN, GROUP_ID
    commands = ["время", "число", "дата", "день"]
    vk_session = vk_api.VkApi(
        token=token)

    longpoll = VkBotLongPoll(vk_session, group_id)
    print('start polling')

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            user_id = event.obj.message['from_id']
            msg_text = event.obj.message["text"]
            if any(map(lambda x: x in msg_text.lower(), commands)):
                dt = datetime.now(pytz.timezone('Europe/Moscow'))
                msg = (f"Дата: {dt.day}.{dt.month}.{dt.year}\nМосковское время: {dt.hour}:{dt.minute}:{dt.second}\n"
                       f"День недели: {WEEKDAYS[dt.weekday()]}")
            else:
                commands_string = ', '.join(commands)
                msg = (
                    f"Вы можете узнать сегодняшнюю дату, московское время и день недели, "
                    f"указав в своём сообщении одно из"
                    f" следующих слов: {commands_string}.")
            vk.messages.send(user_id=user_id,
                             message=msg,
                             random_id=random.randint(0, 2 ** 63 - 1))


if __name__ == '__main__':
    main()
