#System imports

#Libs imports
from typing import Annotated, List, Optional
from fastapi import APIRouter, status, HTTPException, Depends, Body

#Local imports
from internal.models import User
from database import mydb
from internal.auth import decode_token


router = APIRouter()

@router.get("/users")
async def get_all_users(currentUser: Annotated[User, Depends(decode_token)]) -> List[User]:
    cursor = mydb.cursor(dictionary=True)
    if currentUser.role == 'admin':
        query = "SELECT * FROM User WHERE idCompany=%s"
        cursor.execute(query, (currentUser.idCompany,))
        users = cursor.fetchall()
    elif currentUser.role == 'maintainer':
        query = "SELECT * FROM User"
        cursor.execute(query)
        users = cursor.fetchall()
    else: 
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    return [User(**user) for user in users]


@router.get("/users/{user_id}")
async def get_user_by_id(currentUser: Annotated[User, Depends(decode_token)], user_id: int, name: Optional[str] = None) -> User:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM User WHERE id=%s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    if currentUser.role != 'admin' and currentUser.role != 'maintainer' or user is not None and currentUser.role == 'admin' and currentUser.idCompany != user['idCompany']:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    elif user is None:
        raise HTTPException(status_code=404, detail="User not found")
    elif name is not None and user['name'] != name:
        raise HTTPException(status_code=404, detail="User not found")
    elif currentUser.role == 'admin' and currentUser.idCompany == user['idCompany'] or currentUser.role == 'maintainer' :
        return User(**user)


@router.post("/users")
async def create_user(currentUser: Annotated[User, Depends(decode_token)], new_user: User, password: Optional[str] = Body(None, description="User password")) -> User:
    if currentUser.role != 'admin' and currentUser.role != 'maintainer':
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to create new users")
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM User"
    cursor.execute(query)
    users = cursor.fetchall()
    for user in users:
        if user["id"] == new_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this id already exists")
    if currentUser.role == 'admin' and currentUser.idCompany != new_user.idCompany:
         raise HTTPException(status_code=403, detail="Logged-in user is not allowed to create new users in a different company")
    insert_query = "INSERT INTO User (id, name, surname, email, password, role, idCompany) VALUES (%s, %s,%s, %s, %s, %s, %s)"
    data = (new_user.id, new_user.name, new_user.surname ,new_user.email, password, new_user.role, new_user.idCompany)
    cursor.execute(insert_query, data)
    mydb.commit()
    return new_user

@router.put("/users/{user_id}")
async def update_user(user_id: int, currentUser: Annotated[User, Depends(decode_token)], updated_user: User, password: Optional[str] = Body(None, description="User password")) -> User:
    if currentUser.role != 'admin' and currentUser.role != 'maintainer':
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update users")
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM User WHERE id=%s"
    cursor.execute(query, (user_id,))
    user_to_update = cursor.fetchone()
    if user_to_update is None:
        raise HTTPException(status_code=404, detail="User not found") 
    elif currentUser.role == 'admin' and currentUser.idCompany != user_to_update["idCompany"]:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update users in a different company")
    else:
        updated_name = user_to_update['name'] if updated_user.name is None or updated_user.name == "string" else updated_user.name
        updated_surname = user_to_update['surname'] if updated_user.surname is None or updated_user.surname == "string" else updated_user.surname
        updated_email = user_to_update['email'] if updated_user.email is None or updated_user.email == "string" else updated_user.email
        updated_password = user_to_update['password'] if password is None or password == "string" else password
        updated_role = user_to_update['role'] if updated_user.role is None or updated_user.role == "string" else updated_user.role
        # Modification de l'user 
        update_query = "UPDATE User SET name=%s, surname=%s, email=%s, password=%s, role=%s WHERE id=%s"
        data = (updated_name, updated_surname ,updated_email, updated_password, updated_role, user_id)
        cursor.execute(update_query, data)
        mydb.commit()
        # Récupération de l'user modifié
        query = "SELECT * FROM User WHERE id=%s"
        cursor.execute(query, (user_id,))
        updated_user = cursor.fetchone()
        return User(**updated_user)


@router.delete("/users/{user_id}")
async def delete_user(currentUser: Annotated[User, Depends(decode_token)],user_id: int) -> User:
    if currentUser.role != 'admin' and currentUser.role != 'maintainer':
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete users")
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM User WHERE id=%s"
    cursor.execute(query, (user_id,))
    user_to_delete = cursor.fetchone()
    if currentUser.role == 'admin' and currentUser.idCompany != user_to_delete['idCompany']:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete users in a different company")
    elif user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else :
        delete_query = "DELETE FROM User WHERE id=%s"
        cursor.execute(delete_query, (user_id,))
        mydb.commit()
        return User(**user_to_delete)
    

