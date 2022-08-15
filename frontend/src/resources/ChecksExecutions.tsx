import * as React from "react";
import { 
    List, Datagrid, TextField, ReferenceField, Show, SimpleShowLayout, DateField, Labeled, Pagination,
    EditButton, useNotify
} from 'react-admin';
import { TimeSinceNowField } from "../utils";
import { makeStyles } from '@material-ui/core/styles';
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import OpenInNewIcon from '@material-ui/icons/OpenInNew';
import { httpClient, apiUrl } from "../DataProvider";

export const CheckExecutionList = props => (
    <List {...props} perPage={100} pagination={<Pagination rowsPerPageOptions={[100, 300, 600]} {...props} />}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <ReferenceField source="check_id" reference="checks_base" link={(record) => record.check_class === 'check' ? `/checks/${record.check_id}` : `/custom_checks/${record.check_id}`}>
                <TextField source="name" />
            </ReferenceField>
            <DateField source="exec_time" options={{ year: 'numeric', month: 'short', day: 'numeric', hour12: false, 
hour: '2-digit', minute: '2-digit', second: '2-digit'}}/>
            <TimeSinceNowField label="Time since last execution" source="exec_time_since" />
            <TextField source="status" />
        </Datagrid>
    </List>
);

const useStyles = makeStyles({
    terminal: { background: 'black', padding: 10 },
    prompt: { whiteSpace: 'pre-wrap', color: 'white' },
});

const TerminalTextField = props => {
    const classes = useStyles();
    return (
        <div className={classes.terminal}>
            <TextField className={classes.prompt} {...props} />;
        </div>
    )
};

const SetAsSucceedButton = (data) => {
    const notify = useNotify();
    const record = data.record;
    if (record.status !== 'success') {
        return (
            <EditButton
                icon={<LabelImportantIcon/>}
                label='Manually set as Success'
                onClick={() => { 
                    notify('Check execution status will be set as `success` shortly'); 
                    httpClient(`${apiUrl}/check_executions/success/${record.id}`, { method: 'PUT' })
                }}
                to={`..`}
            />
        )
    }
    return <div/>
};

const OpenInSupersetButton = (props => {
    return (
        <EditButton
            icon={<OpenInNewIcon/>}
            label="Open on Superset"
            onClick={() => { 
                window.open(props.record.superset_link, '_blank');
            }}
            to={"#"}
            {...props}
        />
    )
});

export const CheckExecutionShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id" />
            <ReferenceField source="check_id" reference="checks_base" link={(record) => record.check_class === 'check' ? `/checks/${record.check_id}` : `/custom_checks/${record.check_id}`}>
                <TextField source="name" />
            </ReferenceField>
            <DateField 
                source="exec_time" 
                options={{ year: 'numeric', month: 'short', day: 'numeric', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'}}
            />
            <TimeSinceNowField addLabel label="Time since last execution" source="exec_time_since" />
            <TextField source="status" />
            <SetAsSucceedButton {...props.data} />
            <TextField source="results" />
            <Labeled label="Logs">
                <TerminalTextField source="logs" />
            </Labeled>
            <OpenInSupersetButton props /> 
        </SimpleShowLayout>
    </Show>
);
