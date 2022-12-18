import secrets
import requests
import json

''' В данном модуле расположен класс по работе с API AMO CRM, помимо работы с токенами реализован метод получения всех 
задач по текущему аккаунту'''


class ApiAmoManager():
	def __init__(self, client_id, client_secret, code, redirect_uri, client_link):
		self.client_id = client_id
		self.client_secret = client_secret
		self.code = code
		self.redirect_uri = redirect_uri
		self.client_link = client_link

	# получение первоначального токена, требуется актуальный код авторизации (действителен 20 минут)
	# код доступен в настройках интеграции
	def access_data(self):
		data = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'grant_type': 'authorization_code',
			'code': self.code,
			'redirect_uri': self.redirect_uri
		}
		url = self.client_link + '/oauth2/access_token'
		request = requests.post(url, data=data)
		return json.loads(request.text)

	# обновление связки токенов
	def refresh_access(self, refresh_token):
		data = {'client_id': self.client_id,
				'client_secret': self.client_secret,
				'grant_type': 'refresh_token',
				'redirect_uri': self.redirect_uri,
				'refresh_token': refresh_token
				}
		url = self.client_link + '/oauth2/access_token'
		request = requests.post(url, data=data)
		return json.loads(request.text)

	# получение списка задач по текущему аккаунту
	def get_tasks_data(self, token_data):
		api_call_headers = {'Authorization': token_data['token_type'] + ' ' + token_data['access_token']}
		url = secrets.client_link + '/api/v4/tasks'
		api_statuses_response = requests.get(url, headers=api_call_headers, verify=True)
		return api_statuses_response.json()

