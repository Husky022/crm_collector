from google_sheets import GoogleSheets
from api_manager import ApiAmoManager
import secrets
import os
import datetime
import json

'''Данная тестовая программа собирает данные по задачам из определнного аккаунта. 
 Функционально разделено на несколько модулей:
    api_manager.py - работа с определенным API
    goodle_sheets.py - работа с таблицами google
    run.py - текущий модуль с функционалом проверки наличия и работоспособности (срока действия) токенов
'''

class CrmCollector():
    def __init__(self):
        # передаем имя файла с параметрами и имя рабочей таблицы
        self.google_sheets = GoogleSheets(
            credentials='creds.json',
            work_table='test amo tasks'
        )
        # передаем данные из настроек интеграции
        self.api_manager = ApiAmoManager(
            client_id=secrets.client_id,
            client_secret=secrets.client_secret,
            code=secrets.auth_code,
            redirect_uri=secrets.redirect_url,
            client_link=secrets.client_link
        )


    def run(self):
        if not os.path.isfile('token_data.json'): #  проверяем наличие файла с токеном
            access_params = self.api_manager.access_data() #  если нет, то запрашиваем новые токены
            status = access_params.get('status', None)
            if not status: #  если без статусов ошибок, то добавляем файл с токеном...
                token_data = access_params
                token_data['expires_in'] = (datetime.datetime.today() + datetime.timedelta(seconds=token_data['expires_in'])).strftime('%d/%m/%Y %H:%M:%S')
                with open('token_data.json', 'w', encoding='utf-8') as f:
                    json.dump(token_data, f, ensure_ascii=False, indent=4)
                data = self.api_manager.get_tasks_data(access_params) #  ...и тут же запрашиваем данные, которые добавим в таблицу
                self.google_sheets.add_tasks(data)
        else:
            with open('token_data.json', 'r', encoding='utf-8') as f: #  считываем данные токена
                token_data = json.load(f)
            data_now = datetime.datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            date_expire = token_data['expires_in']
            if data_now < date_expire: #  тут проверяем, действительный ли еще токен доступ
                data = self.api_manager.get_tasks_data(token_data)  # если да, то запрашиваем данные, которые добавим в таблицу
                self.google_sheets.add_tasks(data)
            else:
                access_params = self.api_manager.refresh_access(token_data['refresh_token'])  # если нет, то запрашиваем новые токены
                status = access_params.get('status', None)
                if not status:  # если без статусов ошибок, то добавляем файл с токеном...
                    token_data = access_params
                    token_data['expires_in'] = (
                            datetime.datetime.today() + datetime.timedelta(seconds=token_data['expires_in'])).strftime(
                        '%d/%m/%Y %H:%M:%S')
                    with open('token_data.json', 'w', encoding='utf-8') as f:
                        json.dump(token_data, f, ensure_ascii=False, indent=4)
                    data = self.api_manager.get_tasks_data(
                        access_params)  # ...и тут же запрашиваем данные, которые добавим в таблицу
                    self.google_sheets.add_tasks(data)


if __name__ == '__main__':
    crm_collector = CrmCollector()
    crm_collector.run()
