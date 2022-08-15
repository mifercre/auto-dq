import * as React from 'react';
import { FC } from 'react';
import { Card, Box, Typography, Divider } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';

interface Props {
    title: string;
    subtitle?: string;
    children: React.ReactNode;
}

const useStyles = makeStyles(theme => ({
    card: {
        minHeight: 52,
        flex: '1',
        '& a': {
            textDecoration: 'none',
            color: 'inherit',
        },
    },
    main: {
        overflow: 'inherit',
        padding: 16,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    }
}));

const CardWithTitle: FC<Props> = props => {
    const { title, subtitle, children } = props;
    const classes = useStyles(props);
    return (
        <Card className={classes.card}>
            <div className={classes.main}>
                <Box textAlign="left">
                    <Typography color="textSecondary">{title}</Typography>
                    {subtitle? <Typography variant='caption' color="textSecondary">{subtitle}</Typography> : ''}                    
                </Box>
            </div>
            {children && <Divider />}
            {children}
        </Card>
    );
};

export default CardWithTitle;
