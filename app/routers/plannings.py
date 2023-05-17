#System imports

#Libs imports
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Annotated

#Local imports
from internal.models import Planning, User
from database import mydb
from internal.auth import decode_token

router = APIRouter()

@router.get("/plannings")
async def get_all_plannings(currentUser: Annotated[User, Depends(decode_token)]) -> List[Planning]:
    cursor = mydb.cursor(dictionary=True)
    if currentUser.role == 'admin' or currentUser.role == 'user':
        query = "SELECT * FROM Planning WHERE idCompany=%s"
        cursor.execute(query, (currentUser.idCompany,))
        plannings = cursor.fetchall()
    elif currentUser.role == 'maintainer':
        query = "SELECT * FROM Planning"
        cursor.execute(query)
        plannings = cursor.fetchall()
    else: 
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    return [Planning(**planning) for planning in plannings]


@router.get("/plannings/{planning_id}")
async def get_planning_by_id(currentUser: Annotated[User, Depends(decode_token)], planning_id: int) -> Planning:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query, (planning_id,))
    planning = cursor.fetchone()
    if (currentUser.role == 'admin' or currentUser.role == 'user') and planning is not None and planning["idCompany"] != currentUser.idCompany:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    elif planning is None:
        raise HTTPException(status_code=404, detail="Planning not found")
    else :
        return Planning(**planning)


@router.post("/plannings")
async def create_planning(currentUser: Annotated[User, Depends(decode_token)], new_planning: Planning) -> Planning:
    if currentUser.role != 'admin' and currentUser.role != 'maintainer':
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to create new plannings")
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Planning"
    cursor.execute(query)
    plannings = cursor.fetchall()
    for planning in plannings:
        if planning["id"] == new_planning.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A planning with this id already exists")
    if currentUser.role == 'admin' and currentUser.idCompany != new_planning.idCompany:
         raise HTTPException(status_code=403, detail="Logged-in user is not allowed to create new plannings in a different company")
    insert_query = "INSERT INTO Planning (id, idCompany) VALUES (%s, %s)"
    data = (new_planning.id, new_planning.idCompany)
    cursor.execute(insert_query, data)
    mydb.commit()
    return new_planning

@router.put("/plannings/{planning_id}")
async def update_planning(planning_id: int, currentUser: Annotated[User, Depends(decode_token)], updated_planning: Planning) -> Planning:
    if currentUser.role != 'admin' and currentUser.role != 'maintainer':
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update plannings")
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query, (planning_id,))
    planning_to_update = cursor.fetchone()
    if planning_to_update is None:
        raise HTTPException(status_code=404, detail="Planning not found") 
    elif currentUser.role == 'admin' and currentUser.idCompany != planning_to_update["idCompany"]:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update plannings in a different company")
    else:
        updated_idCompany = planning_to_update['idCompany'] if updated_planning.idCompany is None or updated_planning.idCompany == 0 else updated_planning.idCompany
        # Modification du planning
        update_query = "UPDATE Planning SET idCompany=%s WHERE id=%s"
        data = (updated_idCompany, planning_id)
        cursor.execute(update_query, data)
        mydb.commit()
        # Récupération du planning modifié
        query = "SELECT * FROM Planning WHERE id=%s"
        cursor.execute(query, (planning_id,))
        updated_planning = cursor.fetchone()
        return Planning(**updated_planning)

@router.delete("/plannings/{planning_id}")
async def delete_planning(currentUser: Annotated[User, Depends(decode_token)], planning_id: int) -> Planning:
    if currentUser.role != 'admin' and currentUser.role != 'maintainer':
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete plannings")
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query, (planning_id,))
    planning_to_delete = cursor.fetchone()
    if currentUser.role == 'admin' and currentUser.idCompany != planning_to_delete['idCompany']:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete planning in a different company")
    elif planning_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else :
        delete_query = "DELETE FROM Planning WHERE id=%s"
        cursor.execute(delete_query, (planning_id,))
        mydb.commit()
        return Planning(**planning_to_delete)