#System imports

#Libs imports
import datetime
import typing
from pydantic import BaseModel
from typing import List, Optional

#Local imports

class User(BaseModel): # we don't include password_hash in the definition of the class because we don't want to return it
    id: int
    name: str
    surname: str
    email: str
    idCompany: int
    role: str

class Company(BaseModel):
    id: int
    name: str

class Planning(BaseModel):
    id: int
    idCompany: int

class Activity(BaseModel):
    id: int
    idPlanning: int
    idOwner: int
    name: str
    day: datetime.date
    startTime: str
    endTime: str

