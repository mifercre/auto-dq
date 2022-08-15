import * as React from 'react';
import { TopToolbar } from 'react-admin';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
    toolbar: {
        paddingTop: '10px', 
        paddingBottom: '10px', 
        minHeight: '0px',
        justifyContent: 'flex-end', 
    },
});

export const TopToolbarThin = ({ ...props }) => {
    const classes = useStyles();
    return <TopToolbar className={classes.toolbar} {...props} />;
};
