import datetime as dt
from contextlib import closing
from tqdm import tqdm

from models import Category, Transaction, UpdatedTransaction
import ynab
import gpt
import db


NUM_GPT_RETRIES = 2
DB_PATH = './db.sqlite'
TransactionId = str


def categorize_transactions(transactions: list[Transaction], categories: list[Category]) -> dict[TransactionId, Category]:
    """Given a list of transactions and categories, categorize as many transactions as possible.
    Returns: a dictionary of Transaction.id => Category. Not all given transactions can be paired.
    """
    category_map = {c.get_name().lower(): c for c in categories}
    categorized_transactions = {}
    other = 'other'
    category_names = [c.get_name().lower() for c in categories] + [other]

    for transaction in tqdm(transactions):
        if transaction.import_payee_name_original:
            gpt_category = gpt.categorize(category_names, transaction.import_payee_name_original, retries=NUM_GPT_RETRIES)

            if gpt_category == other:
                continue

            categorized_transactions[transaction.id] = category_map[gpt_category]
    return categorized_transactions


def main():
    with closing(db.RunStore(DB_PATH)) as store:
        last_run = store.get_last_run()
        server_knowledge = None
        if last_run is not None:
            server_knowledge = last_run.server_knowledge
        transactions, server_knowledge = ynab.get_transactions(server_knowledge)
        categories = ynab.get_categories()
        categorized_transactions = categorize_transactions(transactions, categories)
        updated_transactions = [
            UpdatedTransaction.model_validate(t.model_dump()) 
            for t in transactions if t.id in categorized_transactions
        ]
        for t in updated_transactions:
            t.category_id = categorized_transactions[t.id].category_id
            t.flag_color = 'blue'
        
        if updated_transactions:
            ynab.patch_transactions(updated_transactions)
        print('updated', len(updated_transactions), 'transactions')
        print('ChatGPT Usage:')
        from gpt import usage_completion_tokens, usage_prompt_tokens, usage_total_tokens
        print('\tCompletion Tokens:', usage_completion_tokens)
        print('\tPrompt Tokens:', usage_prompt_tokens)
        print('\tTotal Tokens:', usage_total_tokens)
        store.add_run(db.Run(
            id=None,
            dttm=dt.datetime.now(),
            completion_token_usage=usage_completion_tokens,
            prompt_token_usage=usage_prompt_tokens,
            server_knowledge=server_knowledge
        ))


if __name__ == '__main__':
    main()
