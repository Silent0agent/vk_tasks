import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config import LOGIN, PASSWORD, GROUP_ID, ALBUM_ID, TOKEN

import vk_api


def captcha_handler(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """

    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    # или код из приложения - генератора кодов
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def main():
    login, password = LOGIN, PASSWORD
    group_id, album_id = GROUP_ID, ALBUM_ID
    token = TOKEN
    vk_session = vk_api.VkApi(
        login, password,
        # функция для обработки двухфакторной аутентификации
        auth_handler=auth_handler,
        captcha_handler=captcha_handler
    )
    bot_session = vk_api.VkApi(token=token)
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    longpoll = VkBotLongPoll(bot_session, group_id)
    print('start polling')
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            bot = bot_session.get_api()
            user_id = event.obj.message['from_id']
            vk = vk_session.get_api()

            user_response = vk.users.get(user_id=user_id)
            first_name = user_response[0].get('first_name')
            msg = f"Привет, {first_name}!"

            photos_response = vk.photos.get(album_id=album_id, group_id=group_id)
            items = photos_response.get('items')
            if not items:
                random_photo = None
                msg = msg + ' Фотографий нет.'
            else:
                photos_list = []
                for photo in items:
                    photos_list.append(f"photo{photo['owner_id']}_{photo['id']}")
                random_photo = random.choice(photos_list)
            if random_photo:
                bot.messages.send(user_id=user_id,
                                  message=msg,
                                  random_id=random.randint(0, 2 ** 63 - 1),
                                  attachment=[random_photo]
                                  )
            else:
                bot.messages.send(user_id=user_id,
                                  message=msg,
                                  random_id=random.randint(0, 2 ** 63 - 1)
                                  )


if __name__ == '__main__':
    main()
