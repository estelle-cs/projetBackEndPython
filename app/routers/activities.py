#System imports

#Libs imports
from typing import Annotated, List, Optional
from fastapi import APIRouter, status, HTTPException, Depends, Body
import datetime

#Local imports
from internal.models import User, Activity
from database import mydb
from internal.auth import decode_token


router = APIRouter()

@router.get("/activities")
async def get_all_activities(currentUser: Annotated[User, Depends(decode_token)]) -> List[Activity]:
    cursor = mydb.cursor(dictionary=True)
    planning_query = "SELECT id FROM Planning WHERE idCompany=%s"
    cursor.execute(planning_query, (currentUser.idCompany,))
    planning_ids = [planning['id'] for planning in cursor.fetchall()]
    if currentUser.role == 'admin' or currentUser.role == 'user':
        query = "SELECT * FROM Activity WHERE idPlanning IN ({})".format(','.join(map(str, planning_ids)))
        cursor.execute(query)
        activities = cursor.fetchall()
    elif currentUser.role == 'maintainer':
        query = "SELECT * FROM Activity"
        cursor.execute(query)
        activities = cursor.fetchall()
    else: 
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    return [Activity(**activity) for activity in activities]


@router.get("/activities/{activity_id}")
async def get_activity_by_id(currentUser: Annotated[User, Depends(decode_token)], activity_id: int) -> Activity:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Activity WHERE id=%s"
    cursor.execute(query, (activity_id,))
    activity = cursor.fetchone()
    query_planning = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query_planning, (activity['id'],))
    planning = cursor.fetchone()
    if (currentUser.role == 'admin' or currentUser.role == 'user') and activity is not None and planning["idCompany"] != currentUser.idCompany:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    elif activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    else :
        return Activity(**activity)
    

@router.post("/activities")
async def create_activity(currentUser: Annotated[User, Depends(decode_token)], new_activity: Activity) -> Activity:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Activity"
    cursor.execute(query)
    activities = cursor.fetchall()
    for activity in activities:
        if activity["id"] == new_activity.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An activity with this id already exists")
    query_planning = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query_planning, (new_activity['idPlanning'],))
    planning = cursor.fetchone()
    if (currentUser.role == 'admin' or currentUser.role == 'user') and currentUser.idCompany != planning.idCompany:
         raise HTTPException(status_code=403, detail="Logged-in user is not allowed to create new activities in a different company")
    insert_query = "INSERT INTO Activity (id, idPlanning, idOwner, name, day, startTime, endTime) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    data = (new_activity.id, new_activity.idPlanning, currentUser.id, new_activity.name, new_activity.day, new_activity.startTime, new_activity.endTime)
    cursor.execute(insert_query, data)
    mydb.commit()
    return new_activity


@router.put("/activities/{activity_id}")
async def update_activity(activity_id: int, currentUser: Annotated[User, Depends(decode_token)], updated_activity: Activity) -> Activity:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Activity WHERE id=%s"
    cursor.execute(query, (activity_id,))
    activity_to_update = cursor.fetchone()
    #Récupération du planning pour avoir l'id de l'entreprise
    query_planning = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query_planning, (activity_to_update['idPlanning'],))
    planning = cursor.fetchone()
    if currentUser.role != 'admin' and currentUser.role != 'maintainer' and (currentUser.role == 'user' and currentUser.id != activity_to_update['idOwner']):
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update this activity")
    if activity_to_update is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    elif (currentUser.role == 'admin' or currentUser.role == 'user') and currentUser.idCompany != planning["idCompany"]:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update activities in a different company")
    else:
        updated_idPlanning = activity_to_update['idPlanning'] if updated_activity.idPlanning is None or updated_activity.idPlanning == 0 else updated_activity.idPlanning
        updated_idOwner = activity_to_update['idOwner'] if updated_activity.idOwner is None or updated_activity.idOwner == 0 else updated_activity.idOwner
        updated_name = activity_to_update['name'] if updated_activity.name is None or updated_activity.name == "string" else updated_activity.name
        updated_day = activity_to_update['day'] if updated_activity.day is None else updated_activity.day
        updated_startTime = activity_to_update['startTime'] if updated_activity.startTime is None or updated_activity.startTime == "string" else updated_activity.startTime
        updated_endTime = activity_to_update['endTime'] if updated_activity.endTime is None or updated_activity.endTime == "string" else updated_activity.endTime
        # Modification de l'activité
        update_query = "UPDATE Activity SET idPlanning=%s, idOwner=%s, name=%s, day=%s, startTime=%s, endTime=%s WHERE id=%s"
        data = (updated_idPlanning, updated_idOwner, updated_name, updated_day, updated_startTime, updated_endTime, activity_id)
        cursor.execute(update_query, data)
        mydb.commit()
        # Récupération de l'activité modifié
        query = "SELECT * FROM Activity WHERE id=%s"
        cursor.execute(query, (activity_id,))
        updated_activity = cursor.fetchone()
        return Activity(**updated_activity)
    

@router.post("/activities/{activity_id}")
async def subscribe_unsuscribe_activity(activity_id: int, currentUser: Annotated[User, Depends(decode_token)]) -> Activity:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Activity WHERE id=%s"
    cursor.execute(query, (activity_id,))
    activity_to_update = cursor.fetchone()
    #Récupération du planning pour avoir l'id de l'entreprise
    query_planning = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query_planning, (activity_to_update['idPlanning'],))
    planning = cursor.fetchone()
    if activity_to_update is None:
        raise HTTPException(status_code=404, detail="Activity not found") 
    elif (currentUser.role == 'admin' or currentUser.role == 'user') and currentUser.idCompany != planning["idCompany"]:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to subscribe to activities in a different company")
    else:
        #Vérification de l'inscription du user pour cette activité
        search_query = "SELECT * FROM User_activity WHERE id_user=%s AND id_activity=%s"
        search_data = (currentUser.id, activity_id)
        cursor.execute(search_query, search_data)
        subscription = cursor.fetchone()
        if subscription is None:
            # Ajout de l'inscription si l'user est pas encore inscrit
            insert_query = "INSERT INTO User_activity (id_user, id_activity) VALUES (%s, %s)"
            data = (currentUser.id, activity_id)
            cursor.execute(insert_query, data)
            mydb.commit()
        else :
            # Désinscription si l'user était déjà inscrit
            delete_query = "DELETE FROM User_activity WHERE id_user=%s AND id_activity=%s"
            delete_data = (currentUser.id, activity_id)
            cursor.execute(delete_query, delete_data)
            mydb.commit()
        # Récupération de l'activité modifiée
        query = "SELECT * FROM Activity WHERE id=%s"
        cursor.execute(query, (activity_id,))
        updated_activity = cursor.fetchone()
        return Activity(**updated_activity)
    

@router.delete("/activities/{activity_id}")
async def delete_activity(currentUser: Annotated[User, Depends(decode_token)], activity_id: int) -> Activity:
    cursor = mydb.cursor(dictionary=True)
    query = "SELECT * FROM Activity WHERE id=%s"
    cursor.execute(query, (activity_id,))
    activity_to_delete = cursor.fetchone()
    #Récupération du planning pour avoir l'id de l'entreprise
    query_planning = "SELECT * FROM Planning WHERE id=%s"
    cursor.execute(query_planning, (activity_to_delete['idPlanning'],))
    planning = cursor.fetchone()
    if currentUser.role != 'admin' and currentUser.role != 'maintainer' and (currentUser.role == 'user' and currentUser.id != activity_to_delete['idOwner']):
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete activities")
    elif (currentUser.role == 'admin' or currentUser.role == 'user') and currentUser.idCompany != planning["idCompany"]:
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete activity in a different company")
    elif activity_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else :
        delete_query = "DELETE FROM Activity WHERE id=%s"
        cursor.execute(delete_query, (activity_id,))
        mydb.commit()
        return Activity(**activity_to_delete)
    
    