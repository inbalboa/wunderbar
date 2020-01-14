#!/usr/bin/env -S PATH="/usr/local/bin:${PATH}" python3

# <bitbar.title>Todobar</bitbar.title>
# <bitbar.version>v1.0.0</bitbar.version>
# <bitbar.author>Sergey Shlyapugin</bitbar.author>
# <bitbar.author.github>inbalboa</bitbar.author.github>
# <bitbar.desc>Microsoft To Do client.</bitbar.desc>
# <bitbar.image>https://i.imgur.com/rij855z.png</bitbar.image>
# <bitbar.dependencies>python3,pymtodo,keyring</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/inbalboa/todobar</bitbar.abouturl>

import json
import subprocess
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from pymtodo import ToDoConnection

APPNAME = 'todobar'
CMD = sys.argv[0]
LIST_DIR = '~/Library/Caches' if sys.platform == 'darwin' else '~/.cache'
LIST_PATH = f'{LIST_DIR}/{APPNAME}/list.json'


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    cmd: str

    def __str__(self):
        return (
            '{title}|bash={cmd} param1=--complete param2={id_} terminal=false refresh=true'
            '\n'
            '➖ {title}|alternate=true bash={cmd} param1=--delete param2={id_} terminal=false refresh=true'
        ).format(title=self.title.replace('|', '—').strip(), cmd=self.cmd, id_=self.id)


def get_secrets():
    mail = keyring.get_password(APPNAME, 'mail')
    password = keyring.get_password(APPNAME, 'password')
    return mail, password


def update_secrets():
    mail = get_input(
        '\"Enter your mail\"',
        hidden=True
    )
    if not mail:
        return None, None
    keyring.set_password(APPNAME, 'mail', mail)

    password = get_input(
        '\"Enter your password\"',
        hidden=True
    )
    if not password:
        return None, None
    keyring.set_password(APPNAME, 'password', password)


def parse_args():
    parser = ArgumentParser(description='Wunderbar')
    parser.add_argument('-a', '--add', type=str, help='add task to specified list')
    parser.add_argument('-c', '--complete', type=str, help='complete task')
    parser.add_argument('-d', '--delete', type=str, help='delete task')
    parser.add_argument('-l', '--switch', action='store_true', help='switch a list')
    parser.add_argument('-s', '--secrets', action='store_true', help='update secrets')
    args = parser.parse_args()
    return args


def wunder_icon():
    return wunder_icon_black() if sys.platform == 'darwin' else wunder_icon_white()


def wunder_icon_black():
    return 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAAAxUlEQVR42oXQMUtCYRQG4OdCNxMiXWyIoMEgkND6A0qDQ4NjFCj9j5ZoEewX1OQm2CCCS0uzODY0NmWQ0CBF0Oqgywe32/uM7+FwOCyTM3YuMXtisa4XBRQdB/Z5M3LjUxkMzAMjDjz5dbbal7cdyENGSeSfRJoO0wYavtSSq65TJTNXIrQ9Bm7p+PahLwYt14FLqLpfXpueLetpdcGzi+SqbEPG0EQOFSeBI16N3XlXBD3TwAO7en7UV/uyNgNZWLPz96sX8vI3zhZvPzkAAAAASUVORK5CYII='


def wunder_icon_white():
    return 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAQAAAC1+jfqAAADXHpUWHRSYXcgcHJvZmlsZSB0eXBlIGV4aWYAAHjatZZtduMqDIb/axWzBEsgJJaDsTlndnCXPy+Euk2aj6bJNScGyyAJPUIO7f/9bfQHF2dPFNU85ZQWXDHHLAUDX07Xqecljvt8WD4GZ3I6XghEAX04PaZ9zi+Q6+cCi1O+nsvJ6tTjUxEfiscVuuU+nvN8KgpykvN8pjzXlfhlO/Mndaqdyi+foyEYm0JfEJI9cFhw924lwIOQQ0Hf7xKSdMmCcUBf8NPrsaNjeBG8Y3QRu6VMeTgPBS1pTkgXMZpy1gt5OMzIJbUPy2cvSj1MfItda5u3tp92V2JCpBLNTX1sZYwwcUUow1iW0Aw/xdhGy2iOLVYQ20BzRavEmQXRbBx548KN99FXrnAxyi6GXqRKGDIPJlnqgBJ74yYGMBsFB5sKagFiOXzhYTcPe5UdljfGTGEoY6z41uia8DftUNRaT13mxY9YwS/pOQ03Orl+xywA4TZjqiO+o9GXvFm+gA0gqCPMjg2WZT2pWJU/cysMzgHzdIm0nI4G2zYVIESwrXCGAwgsCcnMiRcTMWbE0cGnwHMJUVYQYFXZmBrYBJwEE5duG2uMx1xROYlRWgBCQwoGNDg6gBWjIn8sOnKoaNBIqprU1DVrSSHFpCklS71GFQsWTS2ZmVu24sGjqyc3d89esuSAEqY5ZaPsOedSYLRAdcHqghmlrLKGNa66ptVWX/NaKtKnxqo1Vatecy2bbGHD8d/SZrT5lrey845U2uOue9pt9z3vpSHXWmixaUvNmrfcykFtUj2nxhfk7lPjSa0Ti2OefVKD2OxDBfdyop0ZiElkELdOAAktndniHKN0cp3ZkgWHQgXUWDucjTsxEIw7izY+2H2Su8uNND7FTW6Ro47uHeSoo5vkvnO7Qm0r44sSBqB+CntMl9BQ2DBh9yJe+jfpvG/r7Vd+LqIrc57thzl6co3f8pb8DS49VHQZh3tRo/f4c6boiv0f0Pvo6fUwn3p66M0Pe3ote25Qe8Uves2PM2qvx6f39CzmWzTpd8vlFv5fZNPFLt5yaLt6er6E/STYb6N2h94jv+hNde0R/p8nK71+OO6U2ke15/8utc+U+DeU2me+tC8dXvpNmK8lBb0l0l8UNfxhyfQPCJO6tsE9m6sAAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfjCRoHHw82GhOMAAAAAmJLR0QA/4ePzL8AAADJSURBVHjahZADaDVgFEDvb8627azZirOy7dnM3tJLs+3cEMe8MNvK5yk9n5M+XIoWbNikWIyBDz9UKjjESYQA4nQMFE6YpZlbojXfJ3jUcVYIYZ1PCkUDtjjraKu+/EU4X8Q8fKGcSHMf8nkm0fiTgmzCuaJGXYYOlnTsEbp54ZJhfmi+V9CoY5X6MoE+bMUSWPPT3LMTu5QYf4rmN7+YYhsbEWJI1jFWOGKTXs4I0Hwf4FTHEcGTAd5IFw384b+Of9SX33E3vWolXFW/RlfIMvAAAAAASUVORK5CYII='


def get_input_linux(caption, hidden):
    zenity_args = [
        'zenity',
        '--entry',
        '--title=\"Todobar\"',
        f'--text={caption}'
    ]
    if hidden:
        zenity_args.append('--hide-text')
    task = subprocess.Popen(zenity_args, stdout=subprocess.PIPE)
    task.wait()
    answer_text, _ = task.communicate()

    return answer_text.decode().replace('\n', '').replace('\r', '').strip()


def get_input_darwin(caption, hidden):
    hidden_text = 'with hidden answer' if hidden else ''
    osa_args = (
        'osascript',
        '-e',
        f'Tell application \"System Events\" to display dialog {caption} default answer \"\" with title \"Todobar\" with icon 1 {hidden_text}',
        '-e',
        'text returned of result'
    )
    task = subprocess.Popen(osa_args, stdout=subprocess.PIPE)
    task.wait()
    answer_text, _ = task.communicate()

    return answer_text.decode().replace('\n', '').replace('\r', '').strip()


def get_input(caption, hidden=False):
    return (
        get_input_darwin(caption, hidden)
        if sys.platform == 'darwin'
        else get_input_linux(caption, hidden)
    )


def choose_list_linux(lists):
    lst = [f'\"{l.name}: {l.id}\"' for l in lists]
    zenity_args = [
        'zenity',
        '--list',
        '--title=\"Todobar\"',
        '--column="Lists"'
    ]
    zenity_args += lst
    task = subprocess.Popen(zenity_args, stdout=subprocess.PIPE)
    task.wait()
    answer_text, _ = task.communicate()
    answer = answer_text.decode().strip()
    if answer == 'false':
        return None
    else:
        list_id = answer.split(': ')[-1].strip()
        return list_id


def choose_list_darwin(lists):
    lst = [f'\"{l.name}: {l.id}\"' for l in lists]
    lst_str = ','.join(lst)
    osa_args = (
        'osascript',
        '-e',
        f'Tell application \"System Events\" to choose from list {{{lst_str}}} with prompt \"Select your To Do list:\"'
    )
    task = subprocess.Popen(osa_args, stdout=subprocess.PIPE)
    task.wait()
    answer_text, _ = task.communicate()
    answer = answer_text.decode().strip()
    if answer == 'false':
        return None
    else:
        list_id = answer.split(': ')[-1].strip()
        return list_id


def choose_list(lists):
    return (
        choose_list_darwin(lists)
        if sys.platform == 'darwin'
        else choose_list_linux(lists)
    )


def print_error(error):
    print('!|color=#ECB935')
    print('---')
    print(f'Exception: {error}')


def print_refresh():
    print('---')
    print('Refresh|refresh=true')
    print('---')
    print('Open To Do|href="https://to-do.microsoft.com" refresh=false')
    print(
        f'Re-authorize...|alternate=true bash={CMD} param1=--secrets terminal=false refresh=true'
    )


def print_secrets_error():
    print('---')
    print(f'Authorize...|bash={CMD} param1=--secrets terminal=false refresh=true')


def print_import_error():
    print('!|color=#ECB935')
    print('---')
    print('Need to install pymtodo and/or keyring packages')
    print('---')
    print(
        'Install (with PIP)...|bash=pip3 param1=install param2=-U param3=--user param4=pymtodo param5=keyring terminal=true refresh=true'
    )


def get_list(file_path):
    try:
        with open(Path(file_path).expanduser()) as f:
            return json.load(f)
    except IOError:
        return {}


def set_list(file_path, json_data):
    expanded_file_path = Path(file_path).expanduser()
    expanded_file_path.parent.mkdir(exist_ok=True)
    with open(expanded_file_path, 'w+') as f:
        json.dump(json_data, f)


def get_list_by_id(todo_client, list_id):
    for l in todo_client.lists:
        if l.id == list_id:
            return l

def main():
    parsed_args = parse_args()

    try:
        global keyring, ToDoConnection
        import keyring
        from pymtodo import ToDoConnection        
    except ImportError:
        print_import_error()
        print_refresh()
        return

    todo_client = ToDoConnection()

    if parsed_args.switch:
        set_list(LIST_PATH, {})
        return
    elif parsed_args.secrets:
        update_secrets()
        return

    mail, password = get_secrets()
    try:
        todo_client.connect(email=mail, password=password)
    except Exception as e:
        print_error(e)
        print_secrets_error()
        print_refresh()
        return

    if parsed_args.add:
        new_task = get_input('\"Create new task to To Do:\"')
        if new_task:
            get_list_by_id(todo_client, parsed_args.add).create_task(new_task)
        return
    elif parsed_args.complete:
        # todo_client._complete_task(parsed_args.complete)
        todo_client._delete_task(parsed_args.complete)
        return
    elif parsed_args.delete:
        todo_client._delete_task(parsed_args.delete)
        return

    list_id = get_list(LIST_PATH).get('id')
    try:
        if not list_id:
            raw_lists = todo_client.lists
            if not raw_lists:
                return
            list_id = choose_list(raw_lists)
            if not list_id:
                print_error('Please, choose a list')
                print_refresh()
                return
        set_list(LIST_PATH, {'id': list_id})
        # raw_list = todo_client.lists(list_id)
        raw_tasks = todo_client._get_tasks(list_id)
    except Exception as e:
        print_error(e)
        print_secrets_error()
        print_refresh()
        return

    adapted_tasks = [
        Task(id=t.id, title=t.subject, cmd=CMD)
        for t in raw_tasks
        if not t.completed_date_time
    ]
    print(f'|templateImage={wunder_icon()}')
    print('---')
    curr_list = get_list_by_id(todo_client, list_id)
    print(
        f'{curr_list.name}: {len(adapted_tasks) or "no"} {"task" if len(adapted_tasks) == 1 else "tasks"} | href=https://wunderlist.com/#/lists/{list_id}'
    )
    print('---')
    print(*adapted_tasks, sep='\n')
    print('---')
    print(
        f'New task|bash={CMD} param1=--add param2={list_id} terminal=false refresh=true'
    )
    print(
        f'Switch to another list|alternate=true bash={CMD} param1=--switch terminal=false refresh=true'
    )
    print_refresh()


if __name__ == '__main__':
    main()
