import random

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import TOKEN, GROUP_ID
from datetime import datetime

WEEKDAYS = {0: 'Понедельник',
            1: 'Вторник',
            2: 'Среда',
            3: 'Четверг',
            4: 'Пятница',
            5: 'Суббота',
            6: 'Воскресенье'}


def main():
    token, group_id = TOKEN, GROUP_ID
    vk_session = vk_api.VkApi(
        token=token)

    longpoll = VkBotLongPoll(vk_session, group_id)
    print('start polling')
    started_bot_users = []

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            user_id = event.obj.message['from_id']
            if user_id not in started_bot_users:
                msg = 'Здравствуйте. Введите дату в формате YYYY-MM-DD и я скажу вам какой это день недели.'
                started_bot_users.append(user_id)
            else:
                msg_text = event.obj.message["text"]
                try:
                    date_obj = datetime.strptime(msg_text, "%Y-%m-%d")
                    day_of_week_num = date_obj.strftime("%w")
                    msg = WEEKDAYS[int(day_of_week_num)]
                except Exception:
                    msg = 'Введите дату в формате YYYY-MM-DD'
            vk.messages.send(user_id=user_id,
                             message=msg,
                             random_id=random.randint(0, 2 ** 63 - 1))


if __name__ == '__main__':
    main()
