import * as React from "react";
import { 
    List, Datagrid, TextField, Show, SimpleShowLayout, Pagination, ReferenceManyField, SingleFieldList, ChipField,
    EditButton, useNotify, ReferenceField
} from 'react-admin';
import CachedIcon from '@material-ui/icons/Cached';
import { httpClient, apiUrl } from "../DataProvider";
import { stringify } from 'query-string';
import { AsideDBSchema } from "../layout/AsideDbSchema";
import { TopToolbarThin } from "../layout/TopToolbarThin";

export const DBSchemaList = props => (
    <List {...props} perPage={100} pagination={<Pagination rowsPerPageOptions={[100, 300, 600]} {...props} />}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="name" />
            <ReferenceField source="database_id" reference="dbs">
                <TextField source="name" />
            </ReferenceField>
        </Datagrid>
    </List>
);

const RefreshDBSchemaButton = (props) => {
    const notify = useNotify();
    return (
        <EditButton
            icon={<CachedIcon/>}
            label='Refresh'
            onClick={() => { 
                notify('Tables will be refreshed shortly');
                httpClient(`${apiUrl}/db_schemas/refresh/${props.data.id}?${stringify({force: true})}`, { method: 'POST' }) 
            }}
            to={`#`}
            {...props}
        />
    )
}

const DBSchemaActions = ({ ...props }) => {
    return (
        <TopToolbarThin>
            <RefreshDBSchemaButton {...props} />
        </TopToolbarThin>
    )
};

export const DBSchemaShow = props => {
    return <Show actions={<DBSchemaActions props />} aside={<AsideDBSchema />} {...props}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="name" />
            <ReferenceManyField label="Tables" reference="db_tables" target="schema_id" sort={{ field: 'name', order: 'ASC' }}>
                <SingleFieldList linkType="show">
                    <ChipField source="name" />
                </SingleFieldList>
            </ReferenceManyField>
        </SimpleShowLayout>
    </Show>
};
