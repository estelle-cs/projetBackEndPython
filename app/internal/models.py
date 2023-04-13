#System imports

#Libs imports
from pydantic import BaseModel

#Local imports

class User(BaseModel): # we don't include password_hash in the definition of the class because we don't want to return it
    id: int
    name: str