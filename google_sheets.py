import gspread
import datetime


''' В данном модуле расположен класс по работе с гугл таблицами, в текущем исполнении лишь функция добавления id задач,
 т.е. в каждый столбец добавляются все id задач, с разбивкой на соответствующие даты'''


class GoogleSheets:
	def __init__(self, credentials, work_table):
		self.creds = gspread.service_account(filename=credentials)
		self.table = self.creds.open(work_table)
		self.worksheet = self.table.sheet1

	def add_tasks(self, data):
		tasks = data['_embedded']['tasks']
		for task in tasks:
			task_date = datetime.datetime.fromtimestamp(task['created_at']).strftime('%Y-%m-%d')
			task_id = task['id']
			cell = self.worksheet.find(task_date)  # здесь проверяем, есть ли ячейка с такой датой
			if not cell:
				date_row = self.worksheet.row_values(1)
				new_cell_col = len(date_row) + 1  # вставка в конце существующих дат
				self.worksheet.update_cell(1, new_cell_col, task_date)  # добавляем ячейку с текущей датой
				self.worksheet.update_cell(2, new_cell_col, task_id)  # и следом же добавляем запись
			if cell:
				date_column = self.worksheet.col_values(cell.col)  # определяем "высоту" текущего столбца с данной датой
				self.worksheet.update_cell(len(date_column) + 1, cell.col, task_id)  # вставка в низ столбца
