from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware

from integrations.airtable import authorize_airtable, get_items_airtable, oauth2callback_airtable, get_airtable_credentials

from integrations.notion import authorize_notion, get_items_notion, oauth2callback_notion, get_notion_credentials

from integrations.hubspot import authorize_hubspot, get_hubspot_credentials, get_items_hubspot, oauth2callback_hubspot

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}


# Airtable
@app.post('/integrations/airtable/authorize')
async def authorize_airtable_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_airtable(user_id, org_id)

@app.get('/integrations/airtable/oauth2callback')
async def oauth2callback_airtable_integration(request: Request):
    return await oauth2callback_airtable(request)

@app.post('/integrations/airtable/credentials')
async def get_airtable_credentials_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_airtable_credentials(user_id, org_id)

@app.post('/integrations/airtable/load')
async def get_airtable_items(credentials: str = Form(...)):
    return await get_items_airtable(credentials)


# Notion
@app.post('/integrations/notion/authorize')
async def authorize_notion_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_notion(user_id, org_id)

@app.get('/integrations/notion/oauth2callback')
async def oauth2callback_notion_integration(request: Request):
    return await oauth2callback_notion(request)

@app.post('/integrations/notion/credentials')
async def get_notion_credentials_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_notion_credentials(user_id, org_id)

@app.post('/integrations/notion/load')
async def get_notion_items(credentials: str = Form(...)):
    return await get_items_notion(credentials)



# HubSpot
@app.post('/integrations/hubspot/authorize')
async def authorize_hubspot_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await authorize_hubspot(user_id, org_id)

 # Here we are. After the "CONNECT TO HUBSPOT" BUTTON WAS CLICKED, WE HAVE reached this endpoint where we have a function authorize_hubspot_integration() and we are unpacking the user_id and org_id which from the form data which was passed along with the post request when we pressed the "CONNECT TO HUBSPOT" button. Using this user_id and org_id as functional parameters we are calling another function authorize_hubspot().

 #If we go to the import statement at the top, then we can see that this function has been imported from the "integrations/hubspot.py" file. Now its time to go and see what this function does. 



#this redirect url is responsible for invoking the below function that will exchange the authorisation_code in return for access token and refresh token. the argument that the oauth2callback function takes is the response url that hubspot has sent after being verified by the user
@app.get('/integrations/hubspot/oauth2callback')
async def oauth2callback_hubspot_integration(request: Request):
    return await oauth2callback_hubspot(request)



#now again we are here from frontend because handleWindowClosed function sent a post request to this endpoint. Now lets go and see whats happening inside the get_hubspot_credentials() function which again takes 2 functional args ---> user_id and org_id 
@app.post('/integrations/hubspot/credentials')
async def get_hubspot_credentials_integration(user_id: str = Form(...), org_id: str = Form(...)):
    return await get_hubspot_credentials(user_id, org_id)



@app.post('/integrations/hubspot/load')  # changed from /hubspot/get_hubspot_items---> /hubspot/load
async def load_slack_data_integration(credentials: str = Form(...)):
    return await get_items_hubspot(credentials)

# we came from data-form.js with the credentials and since the endpoint type was "hubspot" we reached this endpoint. This is calling a function get_items_hubspot and passing the credentials as a functional argument. So lets go to that function inside hubspot.py. 
