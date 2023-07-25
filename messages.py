
def start_message():
    start_message ='''
Привет)
Это бот, который отправляет Whois-запросы

Он позволяет отслеживать домены, которые вы добавите,
и выводить информацию о домене!

Обновление информации добавленных доменов происходит один раз в день

Инструкцию по командам, которые есть у бота,
можно просмотреть по запросу:
/help

Список команд доступен по запросу:
/commands'''
    return start_message

def help_message():
    help_message = '''Доступные команды :

/commands - просмотреть список доступных запросов

Шаблоны:

/find     { your domain } - Выполняет whois-запрос и выводит информацию о домене

/add    { your domain } - Добавляет домен для отслеживания

/delete    { your domain } - Удаляет ранее добавленный домен

/list - Просмотр добавленных доменов

Вместо { your domain } вставьте имя домена, который хотите проверить
(без {} и без http)'''
    return help_message

def commands_message():
    commands_message = '''Инструкция по доступным командым:
/help

Команды: '''
    return commands_message


def whois_info_msg(domain_name, creation_date, expiration_date):
    whois_info = f'''
Domain :
{domain_name}

Creation date :
{creation_date}

Expiration date :
{expiration_date}
'''
    return whois_info