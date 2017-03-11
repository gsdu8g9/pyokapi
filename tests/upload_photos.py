import json
import requests
import os

import pyokapi


def upload_photos(api, photos_path):
    def upload_photos_part(photos_list):
        upload_url = json.loads(api._call_method('photosV2.getUploadUrl', count=len(photos_list)))['upload_url']
        photos = {'pic' + str(i): open(photo_path, 'rb') for i, photo_path in enumerate(photos_list)}
        response = requests.post(upload_url, files=photos).json()
        photos = json.dumps([{'photo_id': photo_id, 'token': token['token']} for photo_id, token in response['photos'].items()])
        response = json.loads(api._call_method('photosV2.commit', photos=photos))

        for photo in response['photos']:
            if photo['status'] != 'SUCCESS':
                return False

        return True

    if photos_path[-1] != '/':
        photos_path += '/'

    photos_list = [photos_path + name for name in os.listdir(photos_path) if os.path.isfile(photos_path + name)]

    for i in range(0, len(photos_list), 20):
        if not upload_photos_part(photos_list[i:i + 20]):
            return False

    return True

application = pyokapi.Application(
    '',
    '',
    '',
    'https://api.ok.ru/blank.html'
)
session = pyokapi.AutoClientOAuthSession(
    application,
    pyokapi.Permissions.PHOTO_CONTENT,
    '',
    '',
    cookies_filename='cookies.txt'
)

api = pyokapi.API(session)
if upload_photos(api, 'photos'):
    print('Все фотографии загружены успешно')
else:
    print('При загрузке фотографий произошла ошибка')
