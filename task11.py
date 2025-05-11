# В данный момент map api не поддерживает типы карт, поэтому я заменил их на тему карты
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import requests

from config import TOKEN, GROUP_ID

# map_types = {'Базовая карта': 'map',
#              'Карта для автомобильной навигации': 'sat',
#              'Карта общественного транспорта': 'sat,skl',
#              'Административная карта': 'admin'}
map_themes = {'Светлая карта': 'light',
              'Тёмная карта': 'dark'}
user_dict = {}
GEOCODER_SERVER = 'https://geocode-maps.yandex.ru/1.x'
GEOCODER_APIKEY = '8013b162-6b42-4997-9691-77b7074026e0'
MAP_SERVER = 'http://static-maps.yandex.ru/1.x'
MAP_APIKEY = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'


def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    upload = vk_api.VkUpload(vk_session)
    print('start_polling')
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            sender_id = event.obj.message['from_id']
            text = event.obj.message['text']
            if sender_id not in user_dict:
                user_dict[sender_id] = {}
                user_dict[sender_id]['stage'] = 1

            if user_dict[sender_id]['stage'] == 1:
                response = 'Введи название места, которое хочешь увидеть'
                vk = vk_session.get_api()
                vk.messages.send(user_id=sender_id,
                                 message=response,
                                 random_id=random.randint(0, 2 ** 63 - 1))
                user_dict[sender_id]['stage'] = 2
            elif user_dict[sender_id]['stage'] == 2:
                user_dict[sender_id]['request'] = text
                vk = vk_session.get_api()
                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button('Светлая карта', color=VkKeyboardColor.POSITIVE)
                keyboard.add_button('Тёмная карта', color=VkKeyboardColor.POSITIVE)
                # keyboard.add_button('Базовая карта', color=VkKeyboardColor.POSITIVE)
                # keyboard.add_button(
                #     'Карта для автомобильной навигации', color=VkKeyboardColor.POSITIVE)
                # keyboard.add_button(
                #     'Карта общественного транспорта', color=VkKeyboardColor.POSITIVE)
                # keyboard.add_button(
                #     'Административная карта', color=VkKeyboardColor.POSITIVE)
                vk.messages.send(user_id=sender_id,
                                 message=f'Выбери тип карты',
                                 random_id=random.randint(0, 2 ** 63 - 1),
                                 keyboard=keyboard.get_keyboard())
                user_dict[sender_id]['stage'] = 3
            elif user_dict[sender_id]['stage'] == 3:
                # map_type = map_types[text]
                map_theme = map_themes[text]
                request = user_dict[sender_id]['request']
                geocoder_params = {'geocode': request,
                                   'apikey': GEOCODER_APIKEY,
                                   'format': 'json'}
                geocoder_response = requests.get(GEOCODER_SERVER, params=geocoder_params)
                if not geocoder_response:
                    print("Ошибка выполнения запроса:")
                    print(geocoder_response.url)
                    print("Http статус:", geocoder_response.status_code, "(", geocoder_response.reason, ")")
                    continue

                pos = \
                    geocoder_response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
                        'Point'][
                        'pos']
                lon, lat = [float(el) for el in pos.split()]
                map_params = {'ll': f'{lon},{lat}',
                              'spn': '0.02,0.02',
                              'theme': map_theme,
                              # 'l': map_type,
                              'l': 'map',
                              'apikey': MAP_APIKEY}
                map_response = requests.get(MAP_SERVER, map_params)
                if not map_response:
                    print("Ошибка выполнения запроса:")
                    print(map_response.url)
                    print("Http статус:", map_response.status_code, "(", map_response.reason, ")")
                    continue
                map_filename = 'map.png'
                with open(map_filename, 'wb') as file:
                    file.write(map_response.content)
                photo = upload.photo_messages([map_filename])
                vk_photo_id = f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'
                vk = vk_session.get_api()
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Это {request}. Что Вы еще хотите увидеть?',
                                 attachment=vk_photo_id,
                                 random_id=random.randint(0, 2 ** 63 - 1))
                user_dict[sender_id]['stage'] = 2


if __name__ == '__main__':
    main()
