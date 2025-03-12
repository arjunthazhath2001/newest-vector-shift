# hubspot.py

from typing import List
from fastapi import Request, HTTPException
import json
from fastapi.responses import HTMLResponse
import httpx
import secrets
from backend.integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
import asyncio

# If we wish to integrate any service or access its API then we have to register our app first and mention the app name,app description, and scopes(the permissions to access or edit certain information present in the user's account) and we also have to mention redirect URL--> this is the URL that the user will be redirected to once the OAuth is successful. If we do that the "HUBSPOT" developers console or any other service's developers console will give us two main things "CLIENT ID" & "CLIENT SECRET".

#And for configuration purposes we need to mention 4 mandatory things: 
# 1.CLIENT_ID, ---> to let know hubspot that the app trying to access is "vectorshift" that was registered in the developers console.
# 2.CLIENT_SECRET, ----> the password to prove that its exactly our app and it matches the ClientID
# 3.REDIRECT_URL(which in our case is http://localhost:8000/integrations/hubspot/oauth2callback ---> u can find this endpoint inside main.py----> which will trigger another function oauth2callback_hubspot), 
# 4. authorization_url which also can be found in the developers console once your app is created

CLIENT_ID = "c0cd42ac-1437-413d-816a-cff84b4c38d0"
CLIENT_SECRET =  "59397392-6bb8-4f0c-b20e-b8534736dc5e"
REDIRECT_URI = "http://localhost:8000/integrations/hubspot/oauth2callback"
authorization_url= f"https://app-na2.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=crm.objects.contacts.write%20oauth%20crm.objects.contacts.read"

######## the below encoded_client_id_secret #########


#PKCE(Proof key for code exchange is not supported by HUBSPOT in OAuth2.0. Although we can see that PKCE is implement in airtable. we cant follow that here. So lets do something similar to notion)

async def authorize_hubspot(user_id, org_id): 
    # this function will hit the full authorization url and in return gets the "authorization code"
        
    # THIS IS THE js code given in hubspot docs to build the full auth url 
    # const authUrl =
    #   'https://app.hubspot.com/oauth/authorize' +
    #  `?client_id=${encodeURIComponent(CLIENT_ID)}` +
    #   `&scope=${encodeURIComponent(SCOPES)}` +
    #   `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`;
    # +`&state=${encodeURIComponent(STATE)}`;

    #so the url should have---> authorizaiton url + client_id + scope + redirect_uri + state. We have everything except the state information. So lets create it by looking at the example in notion.py, airtable.py
    state_data = {
            'state': secrets.token_urlsafe(32), #to create a random 32 bit string
            'user_id': user_id, 
            'org_id': org_id #having the user id & org id helps in letting our app know that "oh, okay so that auth_code we received just know belongs to this ID and we will be storing the access token by mapping it to this particular user_id & org_id"
        }
    encoded_state = json.dumps(state_data) # convert the state_data object into a string that can be embedded in the url

    #now its a good practice to store this state in our redis db temporarily till we get an authorisation code from the authorization server of hubspot. so once we are redirected back to a url along with code in that url then we can see whether our state which we passed  on(currently read from redis) is what was actually received in the redirect url too. if yes then 100% it is from hubspot. Thus we can trust the auth_code
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)
    
    #you can find this function inside redis_client(dont forget to import these from the file) where this is used to set key value pair in the redis db and it will expire in 10mins(600 seconds). So the key value pair would look something like: hubspot_state:TestOrg:TestUser   erjnefriFVns_9wjnsDFnDFclslwerlxftANX

    #now its time to return the hubspot auth_url to our '/integrations/hubspot/authorize' endpoint which will again return this url to the frontend that will open this url in a new window
    auth_url= f"{authorization_url}&state={encoded_state}"
    return auth_url



#now the above function will trigger the endpoint '/integrations/hubspot/oauth2callback' (inside main.py) because that was our redirect URI. and that above endpoint will trigger the below function:

############################################################################################

#THE authorize_hubspot tells the hubspot that our app wants to access data on behalf of a "HUBSPOT USER", if the user gives permission then an (authorisation code) is returned to our app. BUT MIND YOU STILL THE POPUP WINDOW ISNT CLOSED. Its redirecting back to another URL and calling our oauth2callback_hubspot function. which will Use this (authorisation code) to get an ACCESS_TOKEN from hubspot. Using this access token we can access and edit the data limited to the scopes mentioned earlier. 

############################################################################################


async def oauth2callback_hubspot(request: Request): #this function will exchange the authorization code with the authorization server and in return gets back the access token. And this function is responsible for closing the window in our frontend

    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    
    #the response URL that we get back from hubspot's authorisation url will have 2 things for sure. 
    # 1. CODE, authorization code meant for our particular user 
    # 2. STATE, yes the exact state which we sent to HUBSPOT in our previous function. We can extract this state and check whether its exactly what we sent to HUBSPOT, to verify that we got response from the leigtimate source. Sometimes the response url that we get can have an error too.
    # So we have to check for error in query params and raise a HTTPException if any. 
    # code, state in the query params should also be stored.   
    
    
    state_data = json.loads(encoded_state) 
    #we have to convert the state(which is string currently) into a json object. BUT WHY? 
    # If you remember we had 3 components in our state data , randome 32 bit state, user_id and org_id
    # and all 3 are present in this encoded_state, if we dont convert it into a json object we cant access individual values like user_id and org_id 
    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')


    #Once we capture the state now its time to check it with the state value that we have already stored in our redis database. 
    # So 1st lets retrieve the state value from redis using the get value method.
    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    #now if the saved_state from is not there(which means our 10 mins barrier was over) or if the original_state that we extracted from our response url does not match the saved_state stored in redis then we again have to raise an HTTPException.
    if not saved_state or original_state != json.loads(saved_state).get('state'): #we are doing json.loads() because data extracted from redis comes in the format of a string. so we have to convert it into json before comparing with the (original_state) which is also in the json format.
        raise HTTPException(status_code=400, detail='State does not match.')

    #ONCE WE HAVE ENSURED THAT THE STATE IS SAME AS WHAT WE SENT. Its time to move on to the process of "EXCHANGING AUTHORIZATION CODE WITH ACCESS TOKEN."



    #The 'async with' syntax tells Python to:
    # Await the completion of the context manager's setup
    # Execute the code block
    # Await the completion of cleanup afterward 




    async with httpx.AsyncClient() as client: #we are creating a new http client called as client. Using the 'with' keyword will close connections once the task of the client is done.
        
        #since the gather function has 2 operations inside both will return values but we are not going to use the return value of delete_key_redis. the only return thats useful for us is the response from the post request (for access token) 
        response, _ = await asyncio.gather( 
            #we have used asyncio.gather because we are concurrently performing two asynchronous tasks, one is posting a request to get access tokens for hubspot and the other one is a redis operation to delete the "hubspot_state" key which we no longer need because we have already verified that the response which we have received back is actually from Hubspot....based on the state information.
            client.post(
            'https://api.hubapi.com/oauth/v1/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,         # we are sending the authorisaiton code which we extracted req.query_params a while ago                    
                'redirect_uri': REDIRECT_URI, 
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            }, 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        ),  #the format of this post request is available in https://developers.hubspot.com/docs/guides/api/app-management/oauth-tokens
         
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}'), #deleting the state information from redis as it is no longer necessary
        )

    #since we have recceived our response we not have to store it in our REDIS DB under the key name ("hubspot_credentials"). And this access token will expire in 600 seconds.
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    #json.dumps converts json object into string format so that it can be stored in the redis DB
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    #once all the above lines of code are processed we are creating a html script to close the window that is currently open. Since we got our access token this window is no longer needed
    return HTMLResponse(content=close_window_script)
    #and we are returning this HTML response to the frontend that will close the window. So after this command we have to go and check how is a window closure handled inside hubspot.js

# below is sample response of our request for access token(mentioned in docs):
# // Example response
# {
#   "token_type": "bearer",
#   "refresh_token": "1e8fbfb1-8e96-4826-8b8d-c8af73715",
#   "access_token": "CIrToaiiMhIHAAEAQAAAARiO1ooBIOP0sgEokuLtAEaOaTFnToZ3VjUbtl46MAAAAEAAAAAgAAAAAAAAAAAACAAAAAAAOABAAAAAAAAAAAAAAAQAkIUVrptEzQ4hQHP89Eoahkq-p7dVIAWgBgAA",
#   "expires_in": 1800
# }

# so we gonna store this entire thing in our redis DB



async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    #in the previous function, before closing the window we stored the credentials which includes access token & refresh token
    #no we are trying to fetch it from our redis database. only then using this access token we can access or edit the hubspot data of our user
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    
    #if not accessed with 600 seconds or 10 mins the credentials will no longer be there in redis since we have already declared this expiration time in the previous function while storing our credentials in redis db 
    credentials = json.loads(credentials)
    #but remember before storing into redis we converted into string format, so once we retrieve it, then also its gonna be in string format, so using json.loads() function we have to convert the string credentials into json format only then we can access the individual keys inside it(like access token, refresh token etc )
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')

    #since we have fetched it from the redis db and stored in a variable we no longer have to store it in redis due to security reasons. so lets delete the hubspot_credentials key and return the credentials to the "handleWindowClosed" function.
    return credentials




#Standardizing data from external APIs to our format ensures that the external data can be smoothly processed by our system's backend, stored in our database, and presented in a way that makes sense to our users or other parts of our system.

#################################################################################################
#PLEASE REFER TO get_hubspot_items function before you look into the below integration item_function 
#################################################################################################

async def create_integration_item_metadata_object(response_json: dict, item_type: str) -> IntegrationItem:
    
    """Creates an integration metadata object from a HubSpot response
    
    Args:
        response_json: The raw JSON response from HubSpot API
        item_type: The type of HubSpot item (e.g., 'Contact', 'Company')
        
    Returns:
        A standardized IntegrationItem object
    """
    # Extract the unique ID from the response
    item_id = str(response_json.get('id', ''))
    
    # Process different item types accordingly
    if item_type == 'Contact':
        # For contacts, use first and last name to create a display name
        properties = response_json.get('properties', {})
        first_name = properties.get('firstname', '')
        last_name = properties.get('lastname', '')
        email = properties.get('email', '')
        
        # Construct a name using available information
        if first_name or last_name:
            name = f"{first_name} {last_name}".strip()
        elif email:
            name = email
        else:
            name = f"Contact {item_id}"
    else:
        # Generic handling for other item types
        name = response_json.get('properties', {}).get('name', f"{item_type} {item_id}")
    
    # Create and return the standardized IntegrationItem
    integration_item_metadata = IntegrationItem(
        id=f"{item_id}_{item_type}",  # Create a unique ID combining HubSpot ID and item type
        name=name,  # Use the constructed name
        type=item_type,  # Store the item type
        creation_time=response_json.get('createdAt'),  # Store creation timestamp if available
        last_modified_time=response_json.get('updatedAt'),  # Store update timestamp if available
        # Additional fields could be included here as needed
    )
    
    return integration_item_metadata
    









# the get_items_hubspot needs a helper function to perform its job----> 
# 1. create_integration_item_metadata_object and 

async def get_items_hubspot(credentials) -> List[IntegrationItem]: #this is to indicate that we are going to return a list of integrationitems

    #what are integration items though?
    #its not just about fetching a contact or an item and displaying it. We have to standardise the API response according to a format that our app needs (aka integration item) and then display it to our app users. And for that each item will be processed using the function "create_integration_item_metadata_object". and only after that we will store it in the "list_of_integration_item_metadata"
    
    """Aggregates metadata relevant for a HubSpot integration"""

    credentials = json.loads(credentials)
    access_token = credentials.get('access_token')
    # if you remember we passed the credentials from our data-form.js file in the string format. but now we have to extract 'access_token' from that credential. so we have to convert that string into json using json.loads(). 
    #onces thats done then we can use the get function on credentials to get hold of the access token.


    # List to store all integration items
    list_of_integration_item_metadata = []
    
    
    #########################################################################################################################

    # USUALLY THE BASIC FORMAT OF API REQUESTS FOR MOST SERVICES ARE: client.get(url, headers=headers, params=params)
    # U need a 
    # 1. "url endpoint : where we are gonna fetch data from", 
    # 2. "headers: which includes access token and content type", 
    # 3."params: where we mention filtering instructions, sorting instrucitons, pagination parameters etc"

    #########################################################################################################################

    contacts_url = 'https://api.hubapi.com/crm/v3/objects/contacts'

    #The above url to retrieve contacts in bacthes is in the docs: "https://developers.hubspot.com/docs/guides/api/crm/objects/contacts"

    headers = {
        'Authorization': f'Bearer {access_token}', # we extracted access token in the first few lines of this function
        'Content-Type': 'application/json',
    }
    
    # Limit is set to 10 contacts per request    
    params = {
        'limit': 10,  # this number can be changed
     
    }
    #to see the list of parameters that you can play with visit: https://developers.hubspot.com/docs/reference/api/crm/objects/contacts#get-%2Fcrm%2Fv3%2Fobjects%2Fcontacts

    # Create an HTTP client that will be reused for all requests. orelse for every single page request you will have to establish a new connectio(3-way handshake) which will be resource and time intensive. thats why we use httpx.AsyncClient for connection pooling. Connect once and carry out multiple requests instead of new connection every time.
    async with httpx.AsyncClient() as client:
        has_more = True
        # Continue fetching data as long as there are more results available
        while has_more:
            # Make the API request to HubSpot to fetch contacts
            response = await client.get(contacts_url, headers=headers, params=params)
            # Check if the request was successful (HTTP 200 OK status)
            if response.status_code == 200:
                # Parse the JSON response
                response_json = response.json()
                # Extract the list of contacts from the response. always use response.json() to extract the response so that we can access the key-value pairs inside the response

                #to see how sample response looks like visit: https://developers.hubspot.com/docs/reference/api/crm/objects/contacts#get-%2Fcrm%2Fv3%2Fobjects%2Fcontacts

                #   {
                #   "paging": {
                #     "next": {
                #       "link": "?after=NTI1Cg%3D%3D",
                #       "after": "NTI1Cg%3D%3D"
                #     }
                #   },
                #   "results": []
                
                #response from hubspot has 2 componenets, 1. RESULTS---> contains contact info  2. PAGING---> whether there is a next page

                contacts = response_json.get('results', [])
                # Extract pagination information
                paging_info = response_json.get('paging', {})


                # Process each contact and transform it to our standard format
                for contact in contacts:
                    # Convert each contact to our IntegrationItem format
                    contact_item = await create_integration_item_metadata_object(contact, 'Contact') #you can take a look at this function above the current function which we are working on 


                    # Add the processed contact to our list
                    list_of_integration_item_metadata.append(contact_item)
                
                # Check if there's a next page of results
                if 'next' in paging_info:
                    # Get the cursor for the next page
                    after = paging_info['next'].get('after')
                    # It’s like saying, “Hey, here’s the special code (after) that lets you grab the next set of contacts.”


                    if after:
                    # "Hey, I’m ready for the next batch of contacts. Here’s the special code you gave me (the cursor)."
                    # This ensures that, when you make the next request, HubSpot knows to start where the last set of contacts left off, rather than starting from the beginning again.
                        params['after'] = after 
                    else:
                        # No "after" cursor means no more pages
                        has_more = False
                else:
                    # No "next" in paging_info means no more pages
                    has_more = False

                
            else:
                # If the API request failed, log the error and break the loop
                print(f"Failed to fetch contacts: {response.status_code} - {response.text}")
                break
    # Log the total number of items found
    print(f"Found {len(list_of_integration_item_metadata)} HubSpot integration items")

    # Return the list of standardized integration items
    return list_of_integration_item_metadata

