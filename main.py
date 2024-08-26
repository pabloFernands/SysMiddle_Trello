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
    return requests.get(url, params=params).json()

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
    asana_project = create_asana_project(board['name'])
    #print(asana_project)
    print(board)
    
    for trello_list in get_trello_lists(trello_board_id):
        asana_section = create_asana_section(asana_project['gid'], trello_list['name'])
        
        for card in get_trello_cards(trello_list['id']):
            create_asana_task(
                asana_section['gid'],
                card['name'],
                description=card.get('desc'),
                due_on=card.get('due')
            )
    
    print(f"Projeto Asana criado com ID: {asana_project['gid']}")

trello_board_id = "cIgCzsKd"
sync_trello_to_asana(trello_board_id)

