import re
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel


class UpdatedTransaction(BaseModel):
    id: str
    category_id: Optional[str]
    flag_color: Optional[str]


class Transaction(UpdatedTransaction):
    import_payee_name_original: Optional[str]


# God help me
# https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
EMOJI_PATTERN = re.compile("["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002500-\U00002BEF"  # chinese char
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u"\U00010000-\U0010ffff"
    u"\u2640-\u2642" 
    u"\u2600-\u2B55"
    u"\u200d"
    u"\u23cf"
    u"\u23e9"
    u"\u231a"
    u"\ufe0f"  # dingbats
    u"\u3030"
    "]+", re.UNICODE)


@dataclass
class Category:
    group: str
    name: str
    category_id: str

    def full_name(self) -> str:
        return f'{self.group}/{self.get_name()}'

    def get_name(self) -> str:
        return EMOJI_PATTERN.sub('', self.name).strip()
