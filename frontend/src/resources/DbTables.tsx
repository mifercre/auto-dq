import { 
    Datagrid, TextField, Show, TabbedShowLayout, ReferenceManyField, useNotify, EditButton, SingleFieldList, Labeled, List, Pagination, 
    ReferenceField, Tab
} from 'react-admin';
import CachedIcon from '@material-ui/icons/Cached';
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import { httpClient, apiUrl } from "../DataProvider";
import { Chip } from "@material-ui/core";
import { DBTableChecksAside } from "../layout/AsideDbTableChecks";
import { Heatmap } from "../layout/Heatmap";
import { TopToolbarThin } from "../layout/TopToolbarThin";

export const DBTableList = props => (
    <List {...props} perPage={100} pagination={<Pagination rowsPerPageOptions={[100, 300, 600]} {...props} />}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="name" />
            <ReferenceField source="schema_id" reference="db_schemas">
                <TextField source="name" />
            </ReferenceField>
        </Datagrid>
    </List>
);

const CreateCheckButtons = (props) => {
    const notify = useNotify();
    const uniquenessButton = <EditButton
        icon={<LabelImportantIcon/>}
        label='Uniqueness'
        onClick={() => { 
            notify('Uniqueness check will run shortly'); 
            const query = { column_id: props.record.id };
            const url = `${apiUrl}/checks/uniqueness/auto?params=${JSON.stringify(query)}`;
            httpClient(url, { method: 'POST' })
        }}
        to={`/checks`}
        {...props}
    />
    const nonNullButton = <EditButton
        icon={<LabelImportantIcon/>}
        label='Non-null'
        onClick={() => { 
            notify('Non-null check will run shortly'); 
            const query = { column_id: props.record.id };
            const url = `${apiUrl}/checks/non_null/auto?params=${JSON.stringify(query)}`;
            httpClient(url, { method: 'POST' })
        }}
        to={`/checks`}
        {...props}
    />
    const outliersButton = <EditButton
        icon={<LabelImportantIcon/>}
        label='Outliers'
        onClick={() => { 
            notify('Outliers check will run shortly'); 
            const query = { column_id: props.record.id };
            const url = `${apiUrl}/checks/outliers/auto?params=${JSON.stringify(query)}`;
            httpClient(url, { method: 'POST' })
        }}
        to={`/checks`}
        {...props}
    />
    // TODO: available checks for each column type should be 
    //  retrieved from API instead of hardcoding it here
    if (props.record.type === 'INTEGER') {
        return <div>
            {uniquenessButton}
            {nonNullButton}
            {outliersButton}
        </div>
    } else if (['FLOAT', 'DOUBLE PRECISION'].includes(props.record.type)) {
        return <div>
            {nonNullButton}
            {outliersButton}
        </div>
    } else if (['BOOLEAN'].includes(props.record.type)) {
        return <div>
            {nonNullButton}
        </div>
    } else if (['VARCHAR', 'TEXT', 'DATE'].includes(props.record.type)) {
        return <div>
            {uniquenessButton}
            {nonNullButton}
        </div>
    }
    return <div/>
};

const PartitionField = props => {
    return <Chip label={props.record.name + ': ' + props.record.type}/>
};

const RefreshDBTableButton = (props) => {
    const notify = useNotify();
    return (
        <EditButton
            icon={<CachedIcon/>}
            label='Refresh'
            onClick={() => { 
                notify('Columns will be refreshed shortly');
                httpClient(`${apiUrl}/db_tables/refresh/${props.data.id}`, { method: 'POST' }) 
            }}
            to={`#`}
            {...props}
        />
    )
}

const DBTableActions = ({ ...props }) => {
    return (
        <TopToolbarThin> 
            <RefreshDBTableButton {...props} />
        </TopToolbarThin>
    )
};

export const DBTableShow = props => {
    return (
        <Show 
            actions={<DBTableActions props />} 
            aside={<DBTableChecksAside />} 
            {...props}
        >
            <TabbedShowLayout>
                <Tab label="summary">
                    <ReferenceField source="schema_id" reference="db_schemas">
                        <TextField source="name" />
                    </ReferenceField>
                    <TextField source="id" label="Table Id"/>
                    <TextField source="name" />
                    <ReferenceManyField label="Partition Columns" reference="db_columns" target="table_id" filter={{ is_partition_column: true }} sort={{ field: 'id', order: 'ASC' }}>
                        <SingleFieldList linkType={false}>
                            <PartitionField {...props} />
                        </SingleFieldList>
                    </ReferenceManyField>
                    <ReferenceManyField label="Columns" reference="db_columns" target="table_id" sort={{ field: 'id', order: 'ASC' }}>
                        <Datagrid>
                            <TextField source="name" sortable={false} />
                            <TextField source="type" sortable={false} />
                            <CreateCheckButtons source="Checks Available (single column checks)" sortable={false}/>
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
                <Tab label="Partitions">
                    <ReferenceManyField label="Partition Columns" reference="db_columns" target="table_id" filter={{ is_partition_column: true }} sort={{ field: 'id', order: 'ASC' }}>
                        <SingleFieldList linkType={false}>
                            <PartitionField {...props} />
                        </SingleFieldList>
                    </ReferenceManyField>
                    <Labeled label="Partitions">
                        <Heatmap />
                    </Labeled>
                </Tab> 
            </TabbedShowLayout>
        </Show>
    )
};
