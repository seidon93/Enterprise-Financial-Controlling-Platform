from dataclasses import dataclass

@dataclass(slots=True)
class Account:
    account_code: str
    account_name: str
