import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
ASANA_TOKEN = os.getenv('ASANA_TOKEN')
ASANA_WORKSPACE_ID = os.getenv('ASANA_WORKSPACE_ID')

TRELLO_BASE_URL = 'https://api.trello.com/1'
ASANA_BASE_URL = 'https://app.asana.com/api/1.0'

trello_headers = {
    'Accept': 'application/json'
}

asana_headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {ASANA_TOKEN}'
}

def trello_request(endpoint, params=None):
    url = f"{TRELLO_BASE_URL}/{endpoint}"
    params = params or {}
    params.update({'key': TRELLO_API_KEY, 'token': TRELLO_TOKEN})
    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Response content: {response.text}")
    return None

def asana_request(method, endpoint, data=None):
    url = f"{ASANA_BASE_URL}/{endpoint}"
    response = getattr(requests, method)(url, headers=asana_headers, json={'data': data})
    try:
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
        print(f"Response content: {response.text}")
    return None

def asana_request(method, endpoint, data=None):
    url = f"{ASANA_BASE_URL}/{endpoint}"
    return getattr(requests, method)(url, headers=asana_headers, json={'data': data}).json()['data']

def get_trello_board(board_id):
    return trello_request(f"boards/{board_id}")

def get_trello_lists(board_id):
    return trello_request(f"boards/{board_id}/lists")

def get_trello_cards(list_id):
    return trello_request(f"lists/{list_id}/cards")

def create_asana_project(name):
    return asana_request('post', 'projects', {'name': name, 'workspace': ASANA_WORKSPACE_ID})

def create_asana_section(project_id, name):
    return asana_request('post', 'sections', {'name': name, 'project': project_id})

def create_asana_task(section_id, name, description=None, due_on=None):
    """Criar projeto Asana"""
    data = {
        'name': name,
        'projects': [section_id.split('/')[0]],
        'section': section_id,
        'description': description,
        'due_on': due_on
    }
    return asana_request('post', 'tasks', data)

def sync_trello_to_asana(trello_board_id):
    board = get_trello_board(trello_board_id)
    if not board:
        print("Falha ao obter informações do quadro do Trello")
        return

    asana_project = create_asana_project(board['name'])
    if not asana_project:
        print("Falha ao criar projeto no Asana")
        return

    trello_lists = get_trello_lists(trello_board_id)
    if not trello_lists:
        print("Falha ao obter listas do Trello")
        return

    for trello_list in trello_lists:
        asana_section = create_asana_section(asana_project['gid'], trello_list['name'])
        if not asana_section:
            print(f"Falha ao criar seção no Asana para a lista: {trello_list['name']}")
            continue

        cards = get_trello_cards(trello_list['id'])
        if not cards:
            print(f"Falha ao obter cards da lista do Trello: {trello_list['name']}")
            continue

        for card in cards:
            task = create_asana_task(
                asana_section['gid'],
                card['name'],
                description=card.get('desc'),
                due_on=card.get('due')
            )
            if not task:
                print(f"Falha ao criar tarefa no Asana para o card: {card['name']}")

    print(f"Sincronização concluída. Projeto Asana criado com ID: {asana_project['gid']}")


trello_board_id = "cIgCzsKd"
sync_trello_to_asana(trello_board_id)