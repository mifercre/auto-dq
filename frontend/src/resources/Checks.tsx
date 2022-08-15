import * as React from "react";
import { Fragment } from 'react';
import { 
    List, Datagrid, TextField, TextInput, BooleanField, ChipField, ReferenceField, SimpleShowLayout, Show,
    SimpleForm, RadioButtonGroupInput, Edit, Create, CloneButton, BooleanInput, Filter, EditButton, 
    ShowButton, Pagination, ReferenceInput, SelectInput, BulkDeleteButton, Button, useUpdateMany, useRefresh, 
    useNotify, useUnselectAll, FormDataConsumer, NumberInput, NumberField, required
} from 'react-admin';
import { LastCheckExecInfoField } from "../utils";
import { AsideChecks } from "../layout/AsideChecks";
import { makeStyles } from '@material-ui/core/styles';
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import { httpClient, apiUrl } from "../DataProvider";
import AlarmOffIcon from '@material-ui/icons/AlarmOff';
import AlarmOnIcon from '@material-ui/icons/AlarmOn';
import { TopToolbarThin } from "../layout/TopToolbarThin";
import { validateCrontab } from "./CustomChecks";

const sourceTypeChoices = [
    { id: 'column', name: 'Individual column' },
    { id: 'table', name: 'Table partitions' },
];
const columnCheckTypeChoices = [
    { id: 'uniqueness', name: 'Uniqueness' },
    { id: 'outliers', name: 'Outliers' },
    { id: 'freshness', name: 'Freshness' },
    { id: 'non_null', name: 'Non-Null' },
];
const tableCheckTypeChoices = [
    { id: 'outliers', name: 'Outliers' },
    { id: 'ordered', name: 'Incremental' },
];
const allCheckTypeChoices = columnCheckTypeChoices.concat(tableCheckTypeChoices).filter((value, idx, self) => self.findIndex(t => (t.id === value.id)) === idx)

const CheckFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Name" source="name___ilike" alwaysOn/>
    </Filter>
);

const EnableDisableChecksButton = ({ enable, selectedIds }) => {
    const refresh = useRefresh();
    const notify = useNotify();
    const unselectAll = useUnselectAll();
    const [updateMany, { loading }] = useUpdateMany(
        'checks',
        selectedIds,
        { active: enable },
        {
            onSuccess: () => {
                refresh();
                notify('Checks updated');
                unselectAll('checks');
            },
            onFailure: error => notify('Error: checks not updated', 'warning'),
        }
    );
    return (
        <Button
            label={enable? "Enable" : "Disable"}
            disabled={loading}
            onClick={updateMany}
        >   
            {enable? <AlarmOnIcon /> : <AlarmOffIcon />}
        </Button>
    );
};

const BulkActionButtons = props => (
    <Fragment>
        <EnableDisableChecksButton enable={true} {...props} />
        <EnableDisableChecksButton enable={false} {...props} />
        <BulkDeleteButton {...props} />
    </Fragment>
);

export const CheckList = props => (
    <List {...props} 
        bulkActionButtons={<BulkActionButtons />} 
        filters={<CheckFilter />} 
        perPage={30} 
        pagination={<Pagination rowsPerPageOptions={[30, 60, 100]} {...props} />}
    > 
        <Datagrid rowClick="edit">
            <TextField source="name" />
            <ChipField size="small" source="schedule" />
            <TextField source="type" />
            <BooleanField source="active" />
            <ReferenceField label="Last execution" source="last_check_execution_id" reference="check_executions" link="show">
                <LastCheckExecInfoField source="last_exec_info" />
            </ReferenceField>
            <CloneButton />
        </Datagrid>
    </List>
);

const useStyles = makeStyles({
    button: {
        color: 'red',
        '& svg': { color: 'red' }
    },
});

const triggerCheckExecution = (record) => {
    httpClient(`${apiUrl}/checks/trigger/${record.id}`, {
        method: 'POST',
    })
};

const TriggerButton = (record) => {
    const classes = useStyles();
    const notify = useNotify();
    return (
        <EditButton
            className={classes.button}
            icon={<LabelImportantIcon/>}
            label='Trigger'
            onClick={() => { 
                notify('Check will run shortly'); 
                triggerCheckExecution(record);
            }}
            to={`/checks`}
        />
    )
};

const CheckActions = ({ ...props }) => {
    return (
        <TopToolbarThin>
            <EditButton basePath={props.basePath} record={props.data} />
            <ShowButton basePath={props.basePath} record={props.data} />
            <TriggerButton {...props.data} />
        </TopToolbarThin>
    )
};

const CheckEditTitle = ({ record }) => {
    return <span>Check #{record ? `${record.id} - ${record.name}` : ''}</span>;
};

const CommaSeparatedListInput = props => {
    return (
        <TextInput {...props} 
            parse={inputValue => { 
                if (typeof inputValue === "string") {
                    return inputValue.split(',')
                }
                return inputValue
            }}
            // TODO: validate={commaSeparated}
        />
    )
};

export const CheckEdit = props => (
    <Edit 
        title={<CheckEditTitle record/>} 
        aside={<AsideChecks />} 
        actions={<CheckActions props />} 
        undoable={false}
        {...props}
    >
        <SimpleForm>
            <TextInput disabled source="id" />
            <ReferenceInput label="DB" source="database_id" reference="dbs">
                <SelectInput optionText="name" disabled />
            </ReferenceInput>
            <ReferenceInput label="DBSchema" source="schema_id" reference="db_schemas">
                <SelectInput optionText="name" disabled />
            </ReferenceInput>
            <ReferenceInput label="DBTable" source="table_id" reference="db_tables">
                <SelectInput optionText="name" disabled />
            </ReferenceInput> 
            <ReferenceInput label="DBColumn" source="column_id" reference="db_columns">
                <SelectInput optionText="name" disabled />
            </ReferenceInput> 
            <TextInput source="name" disabled />
            <TextInput source="schedule" validate={validateCrontab}/>
            <RadioButtonGroupInput source="type" choices={allCheckTypeChoices} disabled/>
            <TextInput multiline fullWidth source="description" />
            <CommaSeparatedListInput source="false_positives" label='False positive dates' />
            <NumberInput source="delta_threshold_seconds"/>
            <BooleanInput source="active" label='Active'/>
        </SimpleForm>
    </Edit>
);

export const CheckShow = props => (
    <Show 
        aside={<AsideChecks />} 
        actions={<CheckActions props />} 
        {...props}
    >
        <SimpleShowLayout>
            <TextField source="id" />
            <ReferenceField label="DB" source="database_id" reference="dbs" link="show">
                <TextField source="name" />
            </ReferenceField>
            <ReferenceField label="DB Schema" source="schema_id" reference="db_schemas" link="show">
                <TextField source="name" />
            </ReferenceField>
            <ReferenceField label="DB Table" source="table_id" reference="db_tables" link="show">
                <TextField source="name" />
            </ReferenceField>
            <ReferenceField label="DB Column" source="column_id" reference="db_columns" link="show">
                <TextField source="name" />
            </ReferenceField>
            <TextField source="name" />
            <ChipField size="small" source="schedule" />
            <TextField source="type" />
            <TextField source="description" />
            <TextField source="false_positives" label='False positive dates' />
            <NumberField source="delta_threshold_seconds" />
            <BooleanField source="active" />
            <ReferenceField label="Last execution status" source="last_check_execution_id" reference="check_executions" link="show">
                <TextField source="status" />
            </ReferenceField>
            <ReferenceField label="Last execution at" source="last_check_execution_id" reference="check_executions" link="show">
                <TextField source="exec_time" />
            </ReferenceField>
            <CloneButton />
        </SimpleShowLayout>
    </Show>
);

export const CheckCreate = props => {
    return <Create {...props}>
        <SimpleForm >
            <TextInput source="name" label="DQ Check name" validate={[required()]}/>
            <TextInput source="schedule" validate={validateCrontab}/>
            <TextInput multiline fullWidth source="description" />
            <ReferenceInput label="DB" source="database_id" reference="dbs">
                <SelectInput optionText="name" validate={[required()]} />
            </ReferenceInput>
            <FormDataConsumer>
                {({formData, ...rest}) => formData.database_id &&
                    <ReferenceInput label="Schema" source="schema_id" reference="db_schemas" filter={{ database_id: formData.database_id }} sort={{ field: 'name', order: 'ASC' }} perPage={1000}>
                        <SelectInput optionText="name" validate={[required()]} />
                    </ReferenceInput>
                }
            </FormDataConsumer>
            <FormDataConsumer>
                {({formData, ...rest}) => formData.database_id && formData.schema_id &&
                    <ReferenceInput label="Table" source="table_id" reference="db_tables" target="schema_id" filter={{ schema_id: formData.schema_id }} sort={{ field: 'name', order: 'ASC' }} perPage={1000}>
                        <SelectInput optionText="name" validate={[required()]} />
                    </ReferenceInput>
                }
            </FormDataConsumer>
            <RadioButtonGroupInput label="Source type" source="check_source_type" choices={sourceTypeChoices} 
                helperText="Whether to execute the check on a single column&partition or on the table partitions row count" />
            <FormDataConsumer>
                {({formData, ...rest}) => formData.database_id && formData.schema_id && formData.table_id && formData.check_source_type === 'column' &&
                    <ReferenceInput label="Column" source="column_id" reference="db_columns" target="table_id" filter={{ table_id: formData.table_id }} sort={{ field: 'name', order: 'ASC' }} perPage={1000}>
                        <SelectInput optionText="name" />
                    </ReferenceInput>
                }
            </FormDataConsumer>
            {/* <FormDataConsumer>
                {({formData, ...rest}) => formData.check_source_type === 'table' && 
                    (
                    <RadioButtonGroupInput source="table_partition_column" choices={[
                        { id: 'use_partition_column', name: 'Use table partition column' }, 
                        { id: 'use_custom_column', name: 'Use custom column' }, 
                    ]} />
                )}
            </FormDataConsumer>
            <FormDataConsumer>
                {({formData, ...rest}) => formData.check_source_type === 'table' && formData.table_partition_column === 'use_custom_column' &&
                    (
                    <ReferenceInput label="Column" source="partition_by_column_id" reference="db_columns" target="table_id" filter={{ table_id: formData.table_id }} sort={{ field: 'name', order: 'ASC' }} perPage={1000}>
                        <SelectInput optionText="name" />
                    </ReferenceInput>
                )}
            </FormDataConsumer> */}
            <FormDataConsumer>
                {({formData, ...rest}) => (
                    <RadioButtonGroupInput source="type" choices={formData.check_source_type === 'table' ? tableCheckTypeChoices : columnCheckTypeChoices} />
                )}
            </FormDataConsumer>
            <FormDataConsumer>
                {({formData, ...rest}) => formData.type === 'freshness' &&
                    <NumberInput source="delta_threshold_seconds"/>
                }
            </FormDataConsumer>
            {/* <TextInput multiline fullWidth source="extra_where" label="Additional WHERE filters"/> */}
            <BooleanInput source="active" label='Active'/>
        </SimpleForm>
    </Create>
};
