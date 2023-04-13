#System imports
from typing import Annotated
import hashlib

#Libs imports
from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

#Local imports

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users = [
    {
        "username": "test",
        "password": "pwd"
    },{
        "username": "john",
        "password": "doe"
    }
]

class User(BaseModel):
    username: str

JWT_KEY = "kajshkdalasjjlhgkjguifoudhsfkxahdsf"

async def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_data = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
        #TODO: verify that the user actually exists, for example if it was deleted since the JWT was emited
        return User(username= decoded_data.get("username"))
    except JWTError:
        return credentials_exception


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    for user in users:
        if user["username"] == form_data.username and user["password"] == form_data.password:
            data = dict()
            data["username"] = form_data.username
            jwt_token = jwt.encode(data, JWT_KEY, algorithm="HS256")
            return {"access_token": jwt_token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    

@router.get("/items/")
async def read_items(user: Annotated[User, Depends(decode_token)]):
    return "worked"

    