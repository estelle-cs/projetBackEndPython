#System imports

#Libs imports
import datetime
import typing
from pydantic import BaseModel

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
    day: datetime.date
    startTime: datetime.time
    endTime: datetime.time
    concernedUsers: typing.List
    activities: typing.List

class Activity(BaseModel):
    id: int
    name: str
    idPlanning: typing.List

