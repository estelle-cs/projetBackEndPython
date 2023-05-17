PROJECT NAME : Project Back Python
DESCRIPTION : A back-end app serving resources representing a company

# Run the application

To run the application, we use the uvicorn mode.
Once launched, the app will be accessible at http://localhost except if you've changed port 80 to something else.

## Uvicorn mode

**requirements:** python3.10 or greater installed  
First, install dependencies
`pip install -r requirements.txt`

Then, run the app:  
Go to app file `cd app`
`python -m uvicorn main:app --reload`

# USERS LIST

| username                 | password | role       | Entreprise |
| ------------------------ | -------- | ---------- | ---------- |
| big.boss@main.com        | main     | maintainer | 1          |
| clara.luciani@user.com   | clara    | user       | 1          |
| kate.winslet@admin.com   | admin    | admin      | 1          |
| amanda.lachaise@user.com | amanda   | user       | 1          |
| leo.lou@user.com         | leo      | user       | 2          |
| thomas.stev@admin.com    | thomas   | admin      | 2          |
