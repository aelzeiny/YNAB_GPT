import os
import requests
from models import Transaction, Category, UpdatedTransaction
import pickle


BUDGET_ID = 'last-used'
YNAB_API_KEY = os.environ['YNAB_API_KEY']
DEFAULT_HEADERS = {
    'accept': 'application/json',
    'Authorization': f'Bearer {YNAB_API_KEY}',
    'Content-Type': 'application/json',
}

def get_transactions(server_knowledge=None) -> tuple[list[Transaction], str]:
    url = f'https://api.ynab.com/v1/budgets/{BUDGET_ID}/transactions?type=uncategorized'
    if server_knowledge:
        url += f'&last_knowledge_of_server={server_knowledge}'
    resp = requests.get(url, headers=DEFAULT_HEADERS)
    resp.raise_for_status()
    data = resp.json()['data']
    return [Transaction.model_validate(t) for t in data['transactions']], data['server_knowledge']


def get_categories() -> list[Category]:
    resp = requests.get(
        f'https://api.ynab.com/v1/budgets/{BUDGET_ID}/categories',
        headers=DEFAULT_HEADERS,
    )
    resp.raise_for_status()
    categories_data = resp.json()
    return [
        Category(cg['name'], c['name'], c['id'])
        for cg in categories_data['data']['category_groups']
        for c in cg['categories']
        if cg['name'].startswith('[Auto]')
    ]


def patch_transactions(transactions: list[UpdatedTransaction]):
    resp = requests.patch(
        f'https://api.ynab.com/v1/budgets/{BUDGET_ID}/transactions',
        headers=DEFAULT_HEADERS,
        json=dict(transactions=[t.model_dump() for t in transactions]),
    )
    import pdb; pdb.set_trace()
    resp.raise_for_status()
