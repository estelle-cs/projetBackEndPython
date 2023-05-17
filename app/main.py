#System imports

#Libs imports
from fastapi import FastAPI, Response, status

#Local imports
from routers import users, companies, plannings, activities
from internal import auth

app = FastAPI()

app.include_router(auth.router, tags=["Authentification"])
app.include_router(users.router, tags=["User"])
app.include_router(companies.router, tags=["Company"])
app.include_router(plannings.router, tags=["Planning"])
app.include_router(activities.router, tags=["Activities"])
