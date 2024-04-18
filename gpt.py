from openai import OpenAI


client = OpenAI()

usage_completion_tokens = 0
usage_prompt_tokens = 0
usage_total_tokens = 0


def categorize(category_names: list[str], name: str, retries: int) -> str:
    prompt = f'You are a financial assistant, and are tasked with categorizing expenditures. The categories are {category_names}. I give the title of a credit card purchase, and you respond with only the category. Do not add anything else to the response, just the category.'
    gpt_category = None
    for i in range(retries):
        if gpt_category not in category_names:
            gpt_category = _categorize(prompt, name)
    return gpt_category


def _categorize(prompt: str, name: str) -> str:
    global usage_completion_tokens, usage_prompt_tokens, usage_total_tokens
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": prompt},
        {"role": "user", "content": name},
      ]
    )
    if response.usage is not None:
        usage_completion_tokens += response.usage.completion_tokens
        usage_prompt_tokens += response.usage.prompt_tokens
        usage_total_tokens += response.usage.total_tokens
    return response.choices[0].message.content
