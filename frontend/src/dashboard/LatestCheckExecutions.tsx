import * as React from 'react';
import { FC } from 'react';
import { List, ListItem, Paper, ListItemText, ListItemSecondaryAction, Chip } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import LibraryBooksIcon from '@material-ui/icons/LibraryBooks';
import { Link } from 'react-router-dom';
import CheckIcon from '@material-ui/icons/Check';
import ClearIcon from '@material-ui/icons/Clear';
import CachedIcon from '@material-ui/icons/Cached';
import CardWithIcon from './CardWithIcon';
import { CheckExecution } from '../types';
import { timeSince, tryParseJSON } from '../utils';

interface Props {
    title?: string,
    checkExecutions?: CheckExecution[];
}

const useStyles = makeStyles(theme => ({
    avatar: {
        background: theme.palette.background.paper,
    },
    listItemText: {
        overflowY: 'hidden',
        height: '4em',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
    },
}));

const LatestCheckExecutions: FC<Props> = ({ title, checkExecutions = [] }) => {
    const classes = useStyles();
    return (
        <CardWithIcon
            to="/check_executions"
            icon={LibraryBooksIcon}
            title={title}
            subtitle={'' + checkExecutions.length}
        >
            <Paper style={{ maxHeight: 400, overflow: 'auto' }}>
                <List>
                {checkExecutions.map((record: CheckExecution) => {
                    const results = tryParseJSON(record.results);
                    let statusChip = <Chip icon={<CachedIcon />} style={{ backgroundColor: 'lightblue' }} label={record.status + ' (' + timeSince(Date.parse(record.exec_time + 'Z')) + ')'}/>
                    if (record.status === 'success') {
                        statusChip = <Chip icon={<CheckIcon />} style={{ backgroundColor: 'lightgreen' }} label={record.status + ' (' + timeSince(Date.parse(record.exec_time + 'Z')) + ')'}/>
                    }
                    else if (record.status === 'fail') {
                        statusChip = <Chip icon={<ClearIcon  />} style={{ backgroundColor: '#ff8c8c' }} label={record.status + ' (' + timeSince(Date.parse(record.exec_time + 'Z')) + ')'} />
                    }
                    return (
                        <ListItem
                            key={record.id}
                            button
                            component={Link}
                            to={`/check_executions/${record.id}/show`}
                            alignItems="flex-start"
                        >
                            <ListItemText
                                primary={record.check_name}
                                secondary={
                                    <div style={{ display: 'inline-flex' }}>
                                        <span>{new Date(Date.parse(record.exec_time + 'Z')).toLocaleString()}</span>
                                        &nbsp;&nbsp;&nbsp;
                                        {results === undefined ? '' : Object.keys(results).map((k: string) => {
                                            return <span>{k}: {results[k]}&nbsp;</span>
                                         })}
                                    </div>
                                }
                                className={classes.listItemText}
                                style={{ paddingRight: 0 }}
                            />
                            <ListItemSecondaryAction>
                                {statusChip}
                            </ListItemSecondaryAction>
                        </ListItem>
                    )}
                )}
                </List>
            </Paper>
            
        </CardWithIcon>
    );
};

export default LatestCheckExecutions;
