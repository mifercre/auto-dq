import * as React from "react";
import { useCallback, useState, useEffect, FC } from "react";
import { useVersion, useDataProvider, EditButton, showNotification, DataProvider } from 'react-admin';
import { Card, Typography, Divider} from "@material-ui/core";
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import { makeStyles } from '@material-ui/core/styles';
import { Check } from '../types';
import { Record } from 'ra-core';
import DBTableChecks from '../DBTableChecks';
import { httpClient, apiUrl } from "../DataProvider";
import HelpIcon from '@material-ui/icons/Help';

interface State {
    dbTableChecks: Check[];
}

interface AsideProps {
    record?: Record
}

const useStyles = makeStyles(theme => ({
    main: {
        padding: 16,
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    divHelp: { display: 'inline-block', width: '100%' }
}));

interface Props {
    props?: Record
}

const CreateTableCheckButtons: FC<Props> = ({ props }) => {
    const classes = useStyles(props);
    return (
        <div className={classes.main}>
            <div className={classes.divHelp}>
                <Typography style={{float: 'left'}} color="textSecondary">Checks Available <small>(using table partitions row count as source)</small></Typography>
                <EditButton 
                    icon={<HelpIcon/>} 
                    label='HELP'
                    style={{float: 'right'}}
                    to={`/help`}
                />
            </div>
            <Divider/>
            <EditButton
                icon={<LabelImportantIcon/>}
                label='Outliers'
                style={{marginTop: '1em'}}
                onClick={() => { 
                    showNotification('Outliers check will run shortly'); 
                    const query = { table_id: props.id };
                    const url = `${apiUrl}/checks/outliers/auto?params=${JSON.stringify(query)}`;
                    httpClient(url, { method: 'POST' })
                }}
                to={`/checks`}
            />
            <EditButton
                icon={<LabelImportantIcon/>}
                label='Incremental'
                style={{marginTop: '1em'}}
                onClick={() => { 
                    showNotification('Incremental check will run shortly'); 
                    const query = { table_id: props.id };
                    const url = `${apiUrl}/checks/ordered/auto?params=${JSON.stringify(query)}`;
                    httpClient(url, { method: 'POST' })
                }}
                to={`/checks`}
            />
        </div>
    )
};

export const DBTableChecksAside: FC<AsideProps> = ({ record }) => {
    const version = useVersion();
    const dataProvider:DataProvider = useDataProvider();
    const [state, setState] = useState<State>({ dbTableChecks: [] });
    const fetchDbTableChecks = useCallback(async () => {
        const fromDate = new Date();
        fromDate.setDate(fromDate.getDate() - 10)
        const { data: checks } = await dataProvider.getListUnpaginated('checks', {
            filter: { 
                table_id: record? record.id : 0, 
            },
            sort: { field: 'id', order: 'DESC' },
            limit: 100
        });
        setState(state => ({
                ...state,
                dbTableChecks: checks,
            })
        );
    }, [dataProvider]);
    useEffect(() => {
        fetchDbTableChecks();
    }, [version]);
    const { dbTableChecks } = state;

    if (record) {
        return (
            <div style={{ width: '40%', marginLeft: '1em', height: 'fit-content' }}>
                {record.has_partition_column ?
                    <Card style={{ marginBottom: '1em' }}> 
                        <CreateTableCheckButtons props={record}/>
                    </Card> : ''}
                <Card>
                    <DBTableChecks title='Checks registered on this table' checks={dbTableChecks} />
                </Card>
            </div>
        );
    }
    return <div/>
};
