import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import wikipedia

from config import TOKEN, GROUP_ID


def main():
    token, group_id = TOKEN, GROUP_ID
    wikipedia.set_lang('ru')
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
                msg = 'Здравствуйте. Что вы хотите узнать?'
                started_bot_users.append(user_id)
            else:
                msg_text = event.obj.message["text"]
                try:
                    summary = wikipedia.summary(msg_text)
                    msg = summary
                except Exception:
                    msg = 'Ничего не найдено'
            vk.messages.send(user_id=user_id,
                             message=msg,
                             random_id=random.randint(0, 2 ** 63 - 1))


if __name__ == '__main__':
    main()
