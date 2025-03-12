import { useState, useEffect } from 'react';
import {
    Box,
    Button,
    CircularProgress
} from '@mui/material';
import axios from 'axios';

// hubspot.js

{/* The airtable.js file and notion.js file looks exactly the same. BECAUSE THE ENTIRE OAuth process for any service(hubspot/notion/airtable) is nothing but "A NEW WINDOW OPENING"(the user sending a request to connect with the HUBSPOT SERVICE THROUGH OUR APP) AND "THAT WINDOW GETTING CLOSED"(storing the authorization code that was offered by the authorization server of the HUBSPOT SERVICE).

So we need a function that triggers opening of a new window and we also need a function that handles the workflow once the window is closed. Both these functions will trigger two different endpoints. THIS HIGH LEVEL PROCESS IS THE SAME FOR EVERY INTEGRATION SERVICE */}




export const HubspotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
    const [isConnecting, setIsConnecting] = useState(false); //CHANGES TO TRUE WHEN THE WINDOW IS OPEN, THE USER IS TRYING TO CONNECT AND THE OAuth process is still not finished and the authorization code hasnt been received yet
    const [isConnected, setIsConnected] = useState(false); //CHANGES TO TRUE WHEN THE OAuth process is finished and the authorization code has been received


    // Function to open OAuth in a new window
    const handleConnectClick = async () => {
        try {
            setIsConnecting(true);
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/authorize`, formData);
            //hits the backend url of authorisation for hubspot and triggers a authorize_hubspot function inside the hubspot.py
            const authURL = response?.data;
            //the response is an authorization url for hubspot so we are capturing that data("url") alone
            const newWindow = window.open(authURL, 'Hubspot Authorization', 'width=600, height=600');

            //with this url we are opening a new window with the title "Hubspot Authorization"

            // Polling for the window to close
            const pollTimer = window.setInterval(() => {
                if (newWindow?.closed !== false) { 
                    window.clearInterval(pollTimer);
                    handleWindowClosed();
                }
            }, 200); //every 200 milliseconds we are checking whether this new window is closed or not. if it is "CLOSED" then we are stopping the setInterval function using clearInterval. And immediately we are calling the function "handleWindowClosed()"
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail);
        }
    }
    // This async function(since we are making a post request) immediately sets the isConnecting attribute to True and this will immediately show a CIRCULAR PROGRESS BAR IN THE BUTTON. We are defining a new formdata. Anytime we send a request to an endpoint(URL) we will have to send a body along with it. And we can append that body data(which can contain multiple infos) to this form and send this 'gift wrapped form' along with the post request to the endpoint where this form will be dissected and its data in the form will be used to process the request. And in our case we passed the "USER NAME" AND "ORG NAME" from our previous integration-form.js. And in the form we are adding these values with the name of "user_id" and "org_id". AND from our frontend we are sending a post request using axios to our backend. http://localhost:8000/integrations/hubspot/authorize along with the form data. THIS ENDPOINT WILL USUALLY TRIGGER A FUNCTION IN THE BACKEND. And you can see all the endpoints inside the "main.py" file which is the typical entrypoint for FASTAPI apps where each endpoint is responsible for triggering a particular function.

    //SO NOW ITS TIME TO VISIT THE "main.py" file and see what this endpoint will trigger and what kind of response it will return



    // Function to handle logic when the OAuth window closes
    const handleWindowClosed = async () => {
        try { 
            // once the oauth2callback_hubspot returns the HTML response that closes the window, the pollTimer in the above function immediately calles this function
            const formData = new FormData();
            formData.append('user_id', user);
            formData.append('org_id', org);
            const response = await axios.post(`http://localhost:8000/integrations/hubspot/credentials`, formData);
            //again we are sending a post request to an endpoint inside main.py along with the form data which contains user_id and org_id
            //So lets go over to this endpoint and see which function is triggered over there
            const credentials = response.data; 

            //we are back from get_hubspot_credentials funciton and the response is in the format:
            // {
            //     "token_type": "bearer",
            //     "refresh_token": "1e8fbfb1-8e96-4826-8b8d-c8af73715",
            //     "access_token": "CIrToaiiMhIHAAEAQAAAARiO1ooBIOP0sgEokuLtAEaOaTFnToZ3VjUbtl46MAAAAEAAAAAgAAAAAAAAAAAACAAAAAAAOABAAAAAAAAAAAAAAAQAkIUVrptEzQ4hQHP89Eoahkq-p7dVIAWgBgAA",
            //     "expires_in": 1800
            //   }
            // Axios automatically parses JSON responses, so response.data will be a JavaScript object containing all the credential information
              
            if (credentials) {
                setIsConnecting(false);  //if credentials are there are then we are no longer in connecting stage, so we change the "isConnecting" attribute value to false.
                setIsConnected(true); //since we got the credentials we are in the connected stage. so we change the isConnected attribute's value to true
                setIntegrationParams(prev => ({ ...prev, credentials: credentials, type: 'Hubspot' }));
                //This code:
                // Takes the previous state (prev) of integrationParams
                // Creates a new object that includes all properties from the previous state (...prev is the spread operator)
                // Updates or adds the credentials property with the newly obtained HubSpot credentials
                // Sets the type property to 'Hubspot'

            }
            setIsConnecting(false); // even if credentials are not there but the window got closed then the isConnecting variable should be false, so that the circular progress goes away
        } catch (e) {
            setIsConnecting(false);
            alert(e?.response?.data?.detail);
        }
    }

    useEffect(() => {
        setIsConnected(integrationParams?.credentials ? true : false)
    }, [integrationParams]);

    //If credentials exist when the page is mounted, then the 'isConnected' state variable is set to true and the 'button name' reflects that

    //////////////////////////////////////////////////////////////////////////////////////////////

    // SINCE THE WINDOW IS CLOSED, NOW FROM HERE THE CONTROL WILL GO BACK TO THE "integration-form.js FILE". SO LETS GO BACK THERE AND RENDER THE NEXT COMPONENT.

    /////////////////////////////////////////////////////////////////////////////////////////////
    return (
        <>
        <Box sx={{mt: 2}}>
            
            <Box display='flex' alignItems='center' justifyContent='center' sx={{mt: 2}}>
                
                
                {/* When this component of HubSpotIntegration or AirtableIntegratin or NotionIntegration is called.....the only thing the user is going to see is just a BUTTON. And when the user clicks on that button (provided we havent connected with Hubspot yet), the "handleConnectClick" function is called.*/}
                <Button 
                    variant='contained' 
                    onClick={isConnected ? () => {} :handleConnectClick}
                    color={isConnected ? 'success' : 'primary'}
                    disabled={isConnecting}
                    style={{
                        pointerEvents: isConnected ? 'none' : 'auto',
                        cursor: isConnected ? 'default' : 'pointer',
                        opacity: isConnected ? 1 : undefined
                    }}
                >   

                {/* The button component can have 3 states---> 1.not connected, 2. in the process of connecting and 3. successfully connected, so based on that state we have to display the BUTTON TEXT. If the isConnected value is True(which "it will be" once the OAuth window is closed) then the button text should read "HUBSPOT CONNECTED". And if the window is still open(isConnecting) --> then we have a small circular progress animation. And if nothing has happened to that button yet and no window is open the it should read "CONNECT TO HUBSPOT"   */}
                    {isConnected ? 'Hubspot Connected' : isConnecting ? <CircularProgress size={20} /> : 'Connect to Hubspot'}
                </Button>
            </Box>
        </Box>
      </>
    );
}
