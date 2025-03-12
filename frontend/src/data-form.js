import { useState } from 'react';
import {
    Box,
    TextField,
    Button,
} from '@mui/material';
import axios from 'axios';

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
        <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' width='100%'>
            <Box display='flex' flexDirection='column' width='100%'>
                <TextField
                    label="Loaded Data"
                    value={loadedData || ''}
                    sx={{mt: 2}}
                    InputLabelProps={{ shrink: true }}
                    disabled
                />  
                {/* THE TEXT FIELD displays value only if there is something in the loadedData variable, else the textfield remains empty and this text field is disable you cannot edit the values*/}
                
                <Button
                    onClick={handleLoad}
                    sx={{mt: 2}}
                    variant='contained'
                >
                    Load Data
                </Button>
                {/* A click on THIS LOAD DATA BUTTON IS what triggers the handleLoad function. Lets see what that function does */}

                <Button
                    onClick={() => setLoadedData(null)}
                    sx={{mt: 1}}
                    variant='contained'
                >
                    Clear Data
                </Button>
                {/* A click on THIS CLEAR DATA BUTTON sets the loadedData variabe back to null.*/}

            </Box>
        </Box>
    );
}
