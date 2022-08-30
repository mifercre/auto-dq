import * as React from "react";
import { 
    List, Datagrid, TextField, Show, SimpleShowLayout, Pagination, ReferenceManyField, SingleFieldList, ChipField, 
    Create, SimpleForm, TextInput, NumberInput, CloneButton, EditButton, Edit, useNotify, SelectInput, ShowButton,
    required,
    ReferenceInput
} from 'react-admin';
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import CachedIcon from '@material-ui/icons/Cached';
import { makeStyles } from '@material-ui/core/styles';
import { httpClient, apiUrl } from "../DataProvider";
import { stringify } from 'query-string';
import { TopToolbarThin } from "../layout/TopToolbarThin";

export const DBList = props => (
    <List {...props} perPage={100} pagination={<Pagination rowsPerPageOptions={[100, 300, 600]} {...props} />}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="name" />
            <TextField source="type" />
            <TextField source="hostname" />
            <TextField source="port" />
            <TextField source="database" />
            <EditButton />
            <CloneButton />
        </Datagrid>
    </List>
);

const DB_TYPES = [
    { id: 'presto', name: 'presto' },
    { id: 'postgresql', name: 'postgresql' },
];

const RefreshDBButton = (props) => {
    const notify = useNotify();
    return (
        <EditButton
            icon={<CachedIcon/>}
            label='Fetch Schemas'
            onClick={() => { 
                notify('DB tree will be refreshed shortly');
                httpClient(`${apiUrl}/dbs/refresh/${props.data.id}?${stringify({force: true})}`, { method: 'POST' }) 
            }}
            to={`#`}
            {...props}
        />
    )
}

const useStyles = makeStyles({
    button: {
        color: 'red',
        '& svg': { color: 'red' }
    },
});

const testDBConnection = (record, notify) => {
    httpClient(`${apiUrl}/dbs/${record.id}/test_conn`, {
        method: 'GET',
    }).then(({ json }) => {
        notify(`Connection ${json.success? 'success' : 'failed'}`);
    });
};

const TestDBConnButton = (record) => {
    const classes = useStyles();
    const notify = useNotify();
    return (
        <EditButton
            className={classes.button}
            icon={<LabelImportantIcon/>}
            label='Test Connection'
            onClick={() => { 
                notify('Trying to connect'); 
                testDBConnection(record, notify);
            }}
            to={"#"}
        />
    )
};

const DBActions = ({ ...props }) => {
    return (
        <TopToolbarThin>
            <EditButton basePath={props.basePath} record={props.data} />
            <ShowButton basePath={props.basePath} record={props.data} />
            <RefreshDBButton {...props} />
            <TestDBConnButton {...props.data} />
        </TopToolbarThin>
    )
};

export const DBShow = props => (
    <Show {...props} actions={<DBActions props />}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="name" />
            <TextField source="type" />
            <TextField source="hostname" />
            <TextField source="port" />
            <TextField source="database" />
            <TextField source="blacklist" label="Blacklist (Comma separated list of schemas that shouldn't be included in Auto-DQ metadata (accepts regex too)"/>
            <ReferenceManyField label="Schemas" reference="db_schemas" target="database_id" sort={{ field: 'name', order: 'ASC' }}>
                <SingleFieldList linkType="show">
                    <ChipField source="name" />
                </SingleFieldList>
            </ReferenceManyField>
        </SimpleShowLayout>
    </Show>
);

export const DBCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="name" validate={[required()]} />
            <ReferenceInput label="Type" source="type" reference="dbs/supported_dbs" validate={[required()]}>
                <SelectInput optionText="type" />
            </ReferenceInput>
            <TextInput source="hostname" validate={[required()]} />
            <NumberInput source="port" validate={[required()]} />
            <TextInput source="database" />
            <TextInput source="username" />
            <TextInput source="password" />
            <TextInput fullWidth source="blacklist" label="Blacklist (Comma separated list of schemas that shouldn't be included in Auto-DQ metadata, accepts regex too)"/>
        </SimpleForm>
    </Create>
);

export const DBEdit = props => (
    <Edit undoable={false} {...props}>
        <SimpleForm>
            <TextInput disabled source="id" />
            <TextInput source="name" validate={[required()]} />
            <ReferenceInput label="Type" source="type" reference="dbs/supported_dbs" validate={[required()]}>
                <SelectInput optionText="type" />
            </ReferenceInput>
            <TextInput source="hostname" validate={[required()]} />
            <NumberInput source="port" validate={[required()]} />
            <TextInput source="database" />
            <TextInput source="username" />
            <TextInput source="password" />
            <TextInput fullWidth multiline source="blacklist" label="Blacklist (Comma separated list of schemas that shouldn't be included in Auto-DQ metadata, accepts regex too)"/>
        </SimpleForm>
    </Edit>
);
