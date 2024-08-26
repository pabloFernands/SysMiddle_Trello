import requests
from dotenv import load_dotenv
import os


load_dotenv('keys.env')

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
ASANA_TOKEN = f"Bearer {os.getenv('ASANA_TOKEN')}"
ASANA_WORKSPACE_ID = os.getenv('ASANA_WORKSPACE_ID')


def get_trello_board_name(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}"
    query = {'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=query)
    return response.json()['name']

def get_trello_lists(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    query = {'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=query)
    return response.json()

def get_trello_cards(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    query = {'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN}
    response = requests.get(url, params=query)
    return response.json()


# Função para criar um projeto no Asana
def create_asana_project(project_name):
    url = "https://app.asana.com/api/1.0/projects"
    headers = {
        'Authorization': ASANA_TOKEN,
        'Accept': 'application/json'
    }
    data = {
        'data': {
            'name': project_name,
            'workspace': ASANA_WORKSPACE_ID
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def create_asana_task(project_id, task_name, task_notes):
    url = "https://app.asana.com/api/1.0/tasks"
    headers = {
        'Authorization': ASANA_TOKEN,
        'Accept': 'application/json'
    }
    data = {
        'data': {
            'name': task_name,
            'notes': task_notes,
            'projects': [project_id]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


def copy_trello_to_asana(trello_board_id, asana_project_name):
    asana_project = create_asana_project(asana_project_name)
    asana_project_id = asana_project['data']['gid']
    
    lists = get_trello_lists(trello_board_id)
    for trello_list in lists:
        cards = get_trello_cards(trello_list['id'])
        for card in cards:
            create_asana_task(asana_project_id, card['name'], card['desc'])


# O ID do meu projeto Trello
trello_board_id = 'cIgCzsKd'
asana_project_name = 'Copia Projeto do Trello'
copy_trello_to_asana(trello_board_id, asana_project_name)
