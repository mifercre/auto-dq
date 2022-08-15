import * as React from 'react';
import { useCallback, useState, useEffect, FC } from "react";
import { useVersion, useDataProvider, EditButton, showNotification, DataProvider } from 'react-admin';
import { Record } from 'ra-core';
import { makeStyles } from '@material-ui/core/styles';
import { httpClient, apiUrl } from "../DataProvider";
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import { Paper } from '@material-ui/core';

interface Props {
    record?: Record
}

interface State {
    tablePartitions: any[],
    selectedPartitions: any[],
    hoverTitle: string
}

const useStyles = makeStyles(theme => ({
    gameContainer: {
        background: 'F4A460',
        gridTemplateColumns: 'repeat(13px, 1fr)',
        gridGap: 1,
        // gridAutoRows: '470',
    },
    gridContainer: {
        display: 'grid',
        gridTemplateColumns: 'repeat(30, 13px)',
        gridGap: 1,
    },
    gridCell: {
        height: 13,
        width: 13,
        borderRadius: 1,
        background: 'lightgray',
    },
    button: {
        color: 'red',
        // This is JSS syntax to target a deeper element using css selector, here the svg icon for this button
        '& svg': { color: 'red' }
    },
}));

const getCellStyle = (color) => {
    return { height: 13, width: 13, borderRadius: 1, background: color }
}

const legendItem = (color, text) => {
    return (
        <div>
            <div style={{display: 'inline-flex', marginRight: 10, height: 13, width: 13, background: color}}/>
            <span>{text}</span>
        </div>
    );
}

const triggerCheckExecution = (id, partitions) => {
    httpClient(`${apiUrl}/db_tables/trigger_checks/${id}`, {
        method: 'POST',
        body: JSON.stringify(partitions),
    })
}

export const Heatmap: FC<Props> = ({ record }) => {
    const version = useVersion();
    const dataProvider:DataProvider = useDataProvider();
    const [state, setState] = useState<State>({ 
        tablePartitions: [],
        selectedPartitions: [],
        hoverTitle: ''
    });
    const fetchDbTablePartitions = useCallback(async () => {
        const fromDate = new Date();
        fromDate.setDate(fromDate.getDate() - 10)
        const { data: partitions } = await dataProvider.getListUnpaginated('db_table_partitions', {
            filter: { 
                table_id: record? record.id : 0, 
            },
            sort: { field: 'name', order: 'DESC' },
            limit: 10000
        });
        setState(state => ({
                ...state,
                tablePartitions: partitions,
                hoverTitle: partitions.length > 0 ? 'Latest partition: ' + partitions[0].name : ''
            })
        );
    }, [dataProvider]);

    useEffect(() => {
        fetchDbTablePartitions();
    }, [version]);

    const { tablePartitions, selectedPartitions, hoverTitle } = state;
    const classes = useStyles(record);

    const handleMouseHover = (title: string) => {
        setState({
            ...state,
            hoverTitle: title
        });
    }
    if (tablePartitions.length === 0) {
        return <small>No partitions found</small>
    }
    return (
        <div className={classes.gameContainer}>
            <span>{hoverTitle}</span>
            <br/>
            <div className={classes.gridContainer}>
                {tablePartitions.map(p => {
                    let color = 'lightgray'
                    if (p.check_executions != null) {
                        if (p.check_executions.status === 'fail') color = 'red'
                        else color = 'green'
                    }
                    return (
                        <div>
                            <div style={getCellStyle(color)}
                                onMouseEnter={() => {handleMouseHover(p.name)}}
                                onClick={() => {
                                    setState({
                                        ...state,
                                        selectedPartitions: [...selectedPartitions, p]
                                    });
                                }}
                            >
                            </div>
                        </div>
                    )}
                )}
            </div>
            <br/>
            <div>
            <span>Run check for partitions:</span> <small>(click on the partitions above to backfill them)</small>
            <Paper elevation={1} style={{ padding: '10px' }}>
                {Array.from(new Set(selectedPartitions)).map(p => (<div>{p.name}</div>))}
                {selectedPartitions.length > 0 ?
                    <EditButton
                        className={classes.button}
                        icon={<LabelImportantIcon/>}
                        label='Trigger'
                        onClick={() => { 
                            showNotification('Checks for selected partitions will run shortly'); 
                            triggerCheckExecution(record? record.id : '', selectedPartitions.map(p => p.id));
                        }}
                        to={"/db_tables/" + (record ? record.id : '') + "/show"}
                    /> : '' }
                </Paper>
            </div>
            <br/>
            <span>Legend:</span>
            <div>
                {legendItem('lightgray', 'No checks run')}
                {legendItem('green', 'All checks successful')}
                {legendItem('red', 'Some check failed')}
            </div>
        </div>
    );
};
