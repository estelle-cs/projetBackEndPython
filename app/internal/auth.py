#System imports
from typing import Annotated

#Libs imports
from fastapi import Depends, APIRouter, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

#Local imports
from internal.models import User
from database import mydb

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

cursor = mydb.cursor(dictionary=True)
query = "SELECT * FROM User"
cursor.execute(query)
users = cursor.fetchall()

JWT_KEY = "kajshkdalasjjlhgkjguifoudhsfkxahdsf"

async def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_data = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
        # On vérifie que l'utilisateur existe toujours depuis la génération du token et si oui on le retourne
        query = "SELECT * FROM User WHERE email=%s"
        cursor.execute(query, (decoded_data["email"],))
        user = cursor.fetchone()
        if user:
            return User(id=user["id"], name=user["name"], surname=user["surname"], email=user["email"], idCompany=user["idCompany"], role=user["role"])
        else:
            raise credentials_exception
    except JWTError:
        return credentials_exception

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    for user in users:
        if user["email"] == form_data.username : 
            if user["password"] == form_data.password:
                data = dict()
                data["email"] = form_data.username
                jwt_token = jwt.encode(data, JWT_KEY, algorithm="HS256")
                return {"access_token": jwt_token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect name or password")
    

@router.get("/items/")
async def read_items(user: Annotated[User, Depends(decode_token)]):
    return "worked"

    