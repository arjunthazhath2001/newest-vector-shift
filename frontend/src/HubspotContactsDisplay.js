// HubspotContactsDisplay.js
import React from 'react';
import { 
    Box, 
    Typography, 
    List, 
    ListItem, 
    ListItemText,
    Divider
} from '@mui/material';

export const HubspotContactsDisplay = ({ data }) => {
    if (!data || data.length === 0) {
        return (
            <Box sx={{ mt: 2 }}>
                <Typography variant="body1">No contacts found</Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ mt: 2, width: '100%', maxHeight: 300, overflow: 'auto' }}>
            <Typography variant="subtitle1" gutterBottom>
                Loaded {data.length} contacts
            </Typography>
            <List>
                {data.map((contact, index) => (
                    <React.Fragment key={contact.id}>
                        <ListItem>
                            <ListItemText
                                primary={contact.name || 'No Name'}
                                secondary={// Extract email from contact name if it contains @ symbol
                                    contact.name && contact.name.includes('@') 
                                        ? null  // Name is already an email
                                        : 'Contact'
                                }
                            />
                        </ListItem>
                        {index < data.length - 1 && <Divider />}
                    </React.Fragment>
                ))}
            </List>
        </Box>
    );
};