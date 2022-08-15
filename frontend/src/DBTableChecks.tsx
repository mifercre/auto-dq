import * as React from 'react';
import { FC } from 'react';
import { List, ListItem, Paper, ListItemText, ListItemSecondaryAction } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import LibraryBooksIcon from '@material-ui/icons/LibraryBooks';
import { Link } from 'react-router-dom';
import CardWithIcon from './dashboard/CardWithIcon';
import { Check } from './types';

interface Props {
    title?: string,
    checks?: Check[];
}

const useStyles = makeStyles(theme => ({
    listItemText: {
        overflowY: 'hidden',
        height: '4em',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
    },
}));

const DBTableChecks: FC<Props> = ({ title, checks = [] }) => {
    const classes = useStyles();
    return (
        <CardWithIcon
            to="#"
            icon={LibraryBooksIcon}
            title={title}
            type='success'
            subtitle={'' + checks.length}
        >
            <Paper style={{ maxHeight: 400, overflow: 'auto' }}>
                <List>
                {checks.map((record: Check) => {
                    return (
                        <ListItem
                            key={record.id}
                            button
                            component={Link}
                            to={`/checks/${record.id}/show`}
                            alignItems="flex-start"
                        >
                            <ListItemText
                                primary={record.name}
                                secondary={record.description}
                                className={classes.listItemText}
                                style={{ paddingRight: 0 }}
                            />
                            <ListItemSecondaryAction>
                                {record.schedule}
                            </ListItemSecondaryAction>
                        </ListItem>
                        )
                    })}
                </List>
            </Paper>
        </CardWithIcon>
    );
};

export default DBTableChecks;
