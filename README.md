# efficom-car-dealer

A back-end app serving resources representing a car-dealer

# Documentation
documentation is automatically available at [FQDN](https://fr.wikipedia.org/wiki/Fully_qualified_domain_name):port/docs/ or /redoc
The default FQDN is `localhost` and default port is 80.

# Run the application
Two possible modes to launch the application, the recommended one is Docker mode.  
Once launched, the app will be accessible at http://localhost except if you've changed port 80 to something else.
## Docker mode
**requirements:** docker and docker-compose installed  
To launch, your terminal must be in the root folder of this repository. Then issue :  
`docker-compose up --build`

## Uvicorn mode
**requirements:** python3.10 or greater installed  
First, install dependencies
`pip install -r requirements.txt`

Then, run the app:  
`uvicorn app.main:app --host 0.0.0.0 --port 80`


# Key takeaways:

- Separate code in different files
- Have a proper import section at top of file separating system, libs, and local imports
- always use absolute paths for local imports. eg `from internal.models import Car` instead of `from ..models import Car` Reason: you only use relative imports when the absolute import is too long. Otherwise you ALWAYS use absolute import, they reduce the risk of errors.
- Define properly your models in the parameters and return type (`-> list[User]`) of your endpoints everywhere possible. This will ensure your code fail if your data is not as expected. This is best. you don't wan badly formatted data going smoothly in and out your endpoints
- always use path parameters when targeting a resource (generally with it's unique id). Query parameters are for additional filtering options most of the time.
- Find and use the best HTTP action (GET, POST, PUT, PATCH, DELETE) corresponding to the CRUD action you are performing.
- Try to check what is the most appropriate HTTP code to return (200, 201, 204, 403, 401, etc...)
- Always return a 2xx HTTP code like that: `return Response(status_code=status.HTTP_204_NO_CONTENT)`
- Always **raise** a 4xx or 5xx HTTP **error** code like that: `raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)`
- Always use the status package of FastAPI while doing the above instead of using integers code directly such as `200`