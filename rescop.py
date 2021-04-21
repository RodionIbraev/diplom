import requests
import time
import json


TOKEN_VK_api = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'


class Backup_Data:

    def __init__(self, id, token, num):
        self.id = id
        self.token = token
        self.header = {'Content-Type': 'application/json',
                       'Accept': 'application/json',
                       'Authorization': f'OAuth {self.token}'}
        self.num = num

    def upload_photos(self):
        http_request = 'https://api.vk.com/method/photos.get?'
        params = {'owner_id': self.id,
                  'album_id': 'profile',
                  'extended': 1,
                  'access_token': TOKEN_VK_api,
                  'v': 5.77,
                  'count': self.num}
        response = requests.get(http_request, params=params)
        if response.status_code == 200:
            print('Photos uploaded successfully!')
        else:
            print('An error occurred while uploading photos.')
        response_json = response.json()
        self.photos = {}
        for item in response_json['response']['items']:
            num_likes = str(item['likes']['count'])
            max_size = max(item['sizes'], key=lambda elem: elem['height'])
            if num_likes not in self.photos.keys():
                self.photos[num_likes] = [{'name': num_likes,
                                     'date': time.strftime('%d-%m-%Y', time.localtime(item['date'])),
                                     'url': max_size['url'],
                                     'size': max_size['type']}]
            else:
                self.photos[num_likes].append({'name': num_likes,
                                     'date': time.strftime('%d-%m-%Y', time.localtime(item['date'])),
                                     'url': max_size['url'],
                                     'size': max_size['type']})


    def create_folder(self):
        url_request = "https://cloud-api.yandex.net:443/v1/disk/resources?path=%2F" + str(self.id)
        response = requests.put(url_request, headers=self.header)
        if response.status_code == 201:
            print('The folder is created!')
        else:
            print('An error occurred while creating the folder.')

    def load_photos(self):
        path = f'/{str(self.id)}/'
        data = []
        for key, value in self.photos.items():
            for elem in value:
                if len(value) > 1:
                    name = elem['name'] + f' {elem["date"]}.jpg'
                else:
                    name = elem['name'] + '.jpg'
                params = {'url': elem['url'], 'path': path + name}
                http_request = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
                response = requests.post(http_request, headers=self.header, params=params)
                if response.status_code == 202:
                    data.append({"file_name": name,
                                 "size": elem['size']})
                    print(f'"{name}" successfully uploaded!')
        self.writing_info(data)

    def writing_info(self, data):
        try:
            with open('data.json', 'a') as data_file:
                json.dump(data, data_file)
            print('The information with download results was successfully saved to a file "data.json".')
        except Exception as E:
            print('An error occurred while writing the download results.')

if __name__ == '__main__':
    user_id = input('Введите id пользователя:\n')
    token = input('Введите токен для REST API Я.Диска:\n')
    num = int(input('Введите количество загружаемых фотографий(Введите 0 для значения по умолчанию):\n'))
    if num == 0:
        num = 5
    bd = Backup_Data(user_id, token, num)
    bd.upload_photos()
    bd.create_folder()
    bd.load_photos()