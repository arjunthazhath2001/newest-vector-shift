import { useState } from 'react';
import {
    Box, 
    Typography, 
    Button
} 

from '@mui/material';
import axios from 'axios';
import { HubspotContactsDisplay } from './HubspotContactsDisplay';
const endpointMapping = {
    'Notion': 'notion',
    'Airtable': 'airtable',
    'Hubspot': 'hubspot',
};

export const DataForm = ({ integrationType, credentials }) => {
    const [loadedData, setLoadedData] = useState(null);
    const endpoint = endpointMapping[integrationType]; //the endpoint is chosen from the map, if you remember from our integration.js we had passed down the integration type which we actually set inside the hubspot.js file

    const handleLoad = async () => {
        try {
            const formData = new FormData();
            formData.append('credentials', JSON.stringify(credentials));
            const response = await axios.post(`http://localhost:8000/integrations/${endpoint}/load`, formData);
            // like always when we are hitting an endpoint we are required to carry some FORMDATA required for that endpoint 
            //in our case since we loading the data from our integration (HUBSPOT) we obviously need to send credentials. As of now its in json format. So we have to stringify it (convert into string before passing it to the endpoint).

            //NOW LETS GO AND SEE WHATS HAPPENING at the http://localhost:8000/integrations/${hubspot}/load endpoint

            const data = response.data;
            setLoadedData(data);
            // Axios automatically parses JSON responses, so response.data will be a JavaScript object containing all the contact information
        } catch (e) {
            alert(e?.response?.data?.detail);  //creates an alert box incase of any error
        }
    }

    return ( 
        //THIS COMPONENT RETURNS A TEXT FIELD AND 2 BUTTONS (ONE IS LOAD DATA) (ANOTHER ONE IS CLEAR DATA)
        <Box display='flex' flexDirection='column' width='100%'>
            {loadedData ? (
                integrationType === 'Hubspot' ? (
                    <HubspotContactsDisplay data={loadedData} />
                ) : (
                    <Typography sx={{ mt: 2 }}>
                        Loaded {loadedData.length} items
                    </Typography>
                )
            ) : (
                <Typography sx={{ mt: 2 }}>
                    No data loaded
                </Typography>
            )}
            
            <Box display='flex' gap={1} sx={{ mt: 2 }}>
                
                <Button
                    onClick={handleLoad}
                    variant='contained'
                >
                    Load Data
                </Button>
                {/* A click on THIS LOAD DATA BUTTON IS what triggers the handleLoad function. Lets see what that function does */}

                <Button
                    onClick={() => setLoadedData(null)}
                    variant='contained'
                >
                    Clear Data
                </Button>
                {/* A click on THIS CLEAR DATA BUTTON sets the loadedData variabe back to null.*/}

            </Box>
        </Box>
    );
}
