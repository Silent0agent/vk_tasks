from config import LOGIN, PASSWORD

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
    vk_session = vk_api.VkApi(
        login, password,
        # функция для обработки двухфакторной аутентификации
        auth_handler=auth_handler,
        captcha_handler=captcha_handler
    )

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    # Используем метод wall.get
    response = vk.friends.get()
    friends_ids = response['items']
    friends_list = []
    for friend_id in friends_ids:
        friend_response = vk.users.get(user_id=friend_id, fields="bdate")
        if friend_response:
            friends_list.append({'first_name': friend_response[0].get('first_name'),
                                 'last_name': friend_response[0].get('last_name'),
                                 'bdate': friend_response[0].get('bdate')})
    for friend in sorted(friends_list, key=lambda x: x['last_name']):
        print(f"{friend['first_name']} {friend['last_name']} {friend['bdate']}")


if __name__ == '__main__':
    main()
