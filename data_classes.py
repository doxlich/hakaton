from dataclasses import dataclass
from enum import Enum
from json import JSONEncoder

@dataclass
class Product:
    category: str
    name: str
    consumption_week: str
    suppliers: list[str]

@dataclass
class Suppplier:
    product: str
    nomenclature: str
    supplier: str

class UserRole(Enum):
    SUPPLIER = 0  #Поставщик
    MANAGER = 1  #Менеджер
    DIRECTOR = 2  #Управляющий

@dataclass
class User:
    name: str
    email: str
    role: UserRole
    additional_data: dict[str, str]