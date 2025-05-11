from flask import Flask, render_template
from vk_api import vk_api

from config import LOGIN, PASSWORD

app = Flask(__name__)


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


@app.route("/vk_stat/<int:group_id>")
def get_activities(group_id):
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
    stats = vk.stats.get(group_id=group_id, intervals_count=10)
    result = {'likes': 0,
              'comments': 0,
              'subscribed': 0,
              'ages': {},
              'cities': set()}
    for period in stats:
        if 'activity' in period:
            result['likes'] += period['activity'].get('likes', 0)
            result['comments'] += period['activity'].get('comments', 0)
            result['subscribed'] += period['activity'].get('subscribed', 0)
        if 'reach' in period:
            for age in period['reach'].get('age', []):
                count, value = age['count'], age['value']
                result['ages'][value] = result['ages'].get(value, 0) + count
            for city in period['reach'].get('cities', []):
                result['cities'].add(city['name'])
    result['ages'] = sorted(list(result['ages'].items()))
    result['cities'] = list(result['cities'])
    return render_template('statistics.html', **result)


def main():
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
