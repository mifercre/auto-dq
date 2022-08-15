import * as React from 'react';
import { AppBar } from 'react-admin';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles({
    title: {
        flex: 1,
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
    },
    spacer: {
        flex: 1,
    },
});

const CustomAppBar = (props: any) => {
    const classes = useStyles();
    return (
        <AppBar elevation={1} >
            <span className={classes.spacer} />
            <div style={{display: 'inline-flex'}}>
                <img alt="logo" src="logodq.png" width="30" height="30" style={{marginRight: 10}}></img>
                <Typography
                    variant="h6"
                    color="inherit"
                    className={classes.title}
                >
                    Auto-DQ v0.1
                </Typography>
            </div>
            <span className={classes.spacer} />
        </AppBar>
    );
};

export default CustomAppBar;
