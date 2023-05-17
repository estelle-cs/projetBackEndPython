#System imports

#Libs imports
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Annotated

#Local imports
from internal.models import Company, User
from database import mydb
from internal.auth import decode_token


router = APIRouter()

@router.get("/companies")
async def get_all_companies(currentUser: Annotated[User, Depends(decode_token)]) -> List[Company]:
    # On vérifie que l'user a le role maintainer 
    if currentUser.role == 'maintainer':
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM Company"
        cursor.execute(query)
        companies = cursor.fetchall()
        return [Company(**company) for company in companies]
    else :
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")

@router.get("/companies/{company_id}")
async def get_company_by_id(currentUser: Annotated[User, Depends(decode_token)], company_id: int, name: Optional[str] = None) -> Company:
    # On vérifie que l'user a le role maintainer 
    if currentUser.role == 'maintainer':
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM User WHERE id=%s"
        values = (company_id,)
        cursor.execute(query, values)
        company = cursor.fetchone()
        if company is None:
            raise HTTPException(status_code=404, detail="User not found")
        if name is not None and company['name'] != name:
            raise HTTPException(status_code=404, detail="User not found")
        return Company(**company)
    else :
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to access this resource")
    

@router.post("/companies")
async def create_company(currentUser: Annotated[User, Depends(decode_token)], new_company: Company) -> Company:
    # On vérifie que l'user a le role maintainer 
    if currentUser.role == 'maintainer':
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM Company"
        cursor.execute(query)
        companies = cursor.fetchall()
        for company in companies:
            if company["id"] == new_company.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A company with this id already exists")
        insert_query = "INSERT INTO Company (id, name) VALUES (%s, %s)"
        data = (new_company.id, new_company.name)
        cursor.execute(insert_query, data)
        mydb.commit()
        return new_company
    else :
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to create new companies")
    

@router.put("/companies/{company_id}")
async def update_company(company_id: int, currentUser: Annotated[User, Depends(decode_token)], updated_company: Company) -> Company:
    # On vérifie que l'user a le role maintainer 
    if currentUser.role == 'maintainer':
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM Company WHERE id=%s"
        cursor.execute(query, (company_id,))
        company_to_update = cursor.fetchone()
        if company_to_update is None : 
            raise HTTPException(status_code=404, detail="Company not found") 
        updated_name = company_to_update['name'] if updated_company.name is None or updated_company.name == "string" else updated_company.name
        update_query = "UPDATE Company SET name=%s WHERE id=%s"
        data = (updated_name, company_id)
        cursor.execute(update_query, data)
        mydb.commit()
        # Récupération de la company modifiée
        query = "SELECT * FROM Company WHERE id=%s"
        cursor.execute(query, (company_id,))
        updated_company = cursor.fetchone()
        return Company(**updated_company)
    else :
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to update companies")
    

@router.delete("/companies/{company_id}")
async def delete_company(currentUser: Annotated[User, Depends(decode_token)],company_id: int) -> Company:
    # On vérifie que l'user a le role maintainer 
    if currentUser.role == 'maintainer':
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM Company WHERE id=%s"
        cursor.execute(query, (company_id,))
        company_to_delete = cursor.fetchone()
        if company_to_delete is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        delete_query = "DELETE FROM Company WHERE id=%s"
        cursor.execute(delete_query, (company_id,))
        mydb.commit()
        return Company(**company_to_delete)
    else: 
        raise HTTPException(status_code=403, detail="Logged-in user is not allowed to delete companies")
