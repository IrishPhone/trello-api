import sys
import requests

CELL = 25 # table cell width in chars



auth_params = {
    'key':"",
    'token':""
}
board_id = ""



base_url = "https://api.trello.com/1/{}"  

def spaces(task_name, cell): # добавить пробелы к названию задачи, чтобы получить строку длиной ровно CELL знаков (25)
    if len(task_name) >= cell:
        return task_name[:(cell - 2)] + "\u2026 "
    for x in range(0, cell - len(task_name)):
        task_name += ' '
    return task_name

def log(dup_name=''): # вывести таблицу. Если указан dup_name, искать и нумеровать его копии
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    cnt = 1
    dup_tasks = []
    head = ''
    cols = []
    max_tasks = 0;
    for column in column_data:
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        tmpstr = column['name'] + ' (' + str(len(task_data)) + ')'
        head += spaces(tmpstr, CELL)
        col = []
        for task in task_data:
            if task['name'] == dup_name:
                col.append( str(cnt) + '-' + task['name'])
                dup_tasks.append(task)
                cnt += 1
            else:
                col.append(task['name'])
        cols.append(col)
        if len(col) > max_tasks:
            max_tasks = len(col)
    print('\n' + head + '\n')
    for i in range(max_tasks):
        row_str = ''
        for c in cols:
            try:
                row_str += spaces(c[i], CELL)
            except IndexError:
                row_str += spaces('-', CELL)
        print(row_str)

def create(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    same_name = []
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
        break
    log()

def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # собрать в списке id всех задач с именем name
    task_ids = []
    for column in column_data:
        # Получить список задач
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                # если это название нужной нам задачи, добавить id задачи в список
                task_ids.append( task['id'] )
    # Если таких задач несколько
    if len(task_ids) > 1:
        # вывести таблицу с пронумерованными копиями нужной задачи
        log(name)
        inp = input('Задача имеет копии. Какую копию вы хотите перенести? Введите номер: ')
        # получить id выбранной копии задачи
        task_id = task_ids[int(inp) - 1]
    else:
        task_id = task_ids[0]
    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': column['id'], **auth_params})
            break
    log()

    #

if __name__ == "__main__":      
    if len(sys.argv) <= 2:    
        log()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])