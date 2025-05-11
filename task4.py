import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

from config import TOKEN, GROUP_ID


def main():
    token, group_id = TOKEN, GROUP_ID
    vk_session = vk_api.VkApi(
        token=token)

    longpoll = VkBotLongPoll(vk_session, group_id)
    print('start polling')

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            user_id = event.obj.message['from_id']
            user_response = vk.users.get(user_id=user_id, fields="city")
            first_name = user_response[0].get('first_name')
            city = user_response[0].get('city')
            vk.messages.send(user_id=user_id,
                             message=f"Привет, {first_name}",
                             random_id=random.randint(0, 2 ** 63 - 1))
            if city:
                vk.messages.send(user_id=user_id,
                                 message=f"Как поживает {city['title']}?",
                                 random_id=random.randint(0, 2 ** 63 - 1))


if __name__ == '__main__':
    main()
