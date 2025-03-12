import { useState } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubspotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';

const integrationMapping = {
    'Notion': NotionIntegration,
    'Airtable': AirtableIntegration,
    'Hubspot': HubspotIntegration,
};

// Each of the above key chosen will trigger the Integration component either inside hubspot.js or notion.js or airtable.js

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const CurrIntegration = integrationMapping[currType];

  return (
    <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%' }}>
        <Box display='flex' flexDirection='column'>
        <TextField
            label="User"
            value={user}
            onChange={(e) => setUser(e.target.value)}
            sx={{mt: 2}}
        />
        <TextField
            label="Organization"
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            sx={{mt: 2}}
        />
        <Autocomplete
            id="integration-type"
            options={Object.keys(integrationMapping)}
            sx={{ width: 300, mt: 2 }}
            renderInput={(params) => <TextField {...params} label="Integration Type" />}
            onChange={(e, value) => setCurrType(value)}
        />

        {/* The above autocomplete tag is where users can choose the integration which they need(Notion, Airtable, Hubspot etc).When an option is chosen immediately currType is assigned a value through the  setCurrType variable and this 'currType' value is the one thats used to render the below component. */}
        </Box>
        
        
        
        {/* The below component is triggered only when the user chooses an integration service (aka only when the currType has a value set through the above Autocomplete component). Till then the below component is not triggered.  The component searches the "Integration Mapping list we have above with the currtype key. Based on the "currtype" key the value of "CurrIntegration" component can be either "AirtableIntegration (inside ./integrations/airtable.js)" or "NotionIntegration (inside ./integrations/notion.js) or "HubspotIntegration (inside ./integrations/hubspot.js)".
        
         And this below component is the very first part that sets up for the OAuth process which we will see in detail inside "hubspot.js" file on how the OAuth process happens particularly for HUBSPOT INTEGRATION. At the intial stage we are passing down the user name & org name which the user gave but the Integration Params is empty we are just passing down the integrationParams and setIntegrationParams into the respective Integration component and the PROCESS OF SETTING INTEGRATION PARAMS HAPPENS INSIDE THAT COMPONENT(post OAuth) AND NOT HERE. */}
        {currType && 
        <Box>
            <CurrIntegration user={user} org={org} integrationParams={integrationParams} setIntegrationParams={setIntegrationParams} />
        </Box>
        }

        {/* After returning back from "hubspot.js / notion.js/ airtable.js" where OAuth process just took place and we have got hold of the access token. The integrationParams we passed in the above component will have an object assigned and this object will contain credentials(access token) that will help us access or load data from the authorised service. AND THE BELOW COMPONENT IS TRIGGERED ONLY WHEN THE "integrationParams" has a value assigned to it----indicating that access token is received post successful OAuth process. With this credentials stored in IntegrationParams the DataForm component is called which is inside "data-form.js" ---and this component triggers the endpoint that can be used to load data from hubspot(or any other integration) and also clear the data. */}

        {integrationParams?.credentials && 
        <Box sx={{mt: 2}}>
            <DataForm integrationType={integrationParams?.type} credentials={integrationParams?.credentials} />
        </Box>
        }
    </Box>
  );
}
