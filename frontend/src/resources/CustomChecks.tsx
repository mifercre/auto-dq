import { Fragment } from 'react';
import { 
    List, Datagrid, TextField, TextInput, BooleanField, ChipField, ReferenceField, SimpleShowLayout, Show,
    SimpleForm, Edit, Create, CloneButton, BooleanInput, Filter, EditButton, ShowButton, Pagination, 
    ReferenceInput, SelectInput, BulkDeleteButton, Button, useUpdateMany, useRefresh, useNotify, 
    useUnselectAll, required
} from 'react-admin';
import { crontabValidation, LastCheckExecInfoField } from "../utils";
import { AsideChecks } from "../layout/AsideChecks";
import { makeStyles } from '@material-ui/core/styles';
import LabelImportantIcon from '@material-ui/icons/LabelImportant';
import { httpClient, apiUrl } from "../DataProvider";
import AlarmOffIcon from '@material-ui/icons/AlarmOff';
import AlarmOnIcon from '@material-ui/icons/AlarmOn';
import { TopToolbarThin } from "../layout/TopToolbarThin";

const CheckFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Name" source="name___ilike" alwaysOn/>
        <TextInput label="Search by Source" source="source___ilike" alwaysOn/>
    </Filter>
);

const EnableDisableChecksButton = ({ enable, selectedIds }) => {
    const refresh = useRefresh();
    const notify = useNotify();
    const unselectAll = useUnselectAll();
    const [updateMany, { loading }] = useUpdateMany(
        'custom_checks',
        selectedIds,
        { active: enable },
        {
            onSuccess: () => {
                refresh();
                notify('Checks updated');
                unselectAll('custom_checks');
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

export const CustomCheckList = props => (
    <List {...props} 
        bulkActionButtons={<BulkActionButtons />} 
        filters={<CheckFilter />} 
        perPage={30} 
        pagination={<Pagination rowsPerPageOptions={[30, 60, 100]} {...props} />}
    > 
        <Datagrid rowClick="edit">
            <TextField source="name" />
            <ChipField size="small" source="schedule" />
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

const triggerCustomCheckExecution = (record) => {
    httpClient(`${apiUrl}/custom_checks/trigger/${record.id}`, {
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
                triggerCustomCheckExecution(record);
            }}
            to={`/custom_checks`}
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

export const validateCrontab = [required(), crontabValidation];

export const CustomCheckEdit = props => {
    const notify = useNotify();
    const refresh = useRefresh();
    const onFailure = (error) => {
        notify(`Could not edit custom check: ${JSON.stringify(error.body)}`);
        refresh();
    };
    return (
        <Edit title={<CheckEditTitle record/>} 
            aside={<AsideChecks />} 
            actions={<CheckActions props />} 
            undoable={false}
            mutationMode="pessimistic"
            onFailure={onFailure}
            {...props}
        >
            <SimpleForm>
                <TextInput disabled source="id" />
                <TextInput source="name" disabled validate={[required()]}/>
                <TextInput source="schedule" validate={validateCrontab} />
                <TextInput multiline fullWidth source="description" />
                <TextInput multiline fullWidth source="source" validate={[required()]}/>
                <BooleanInput source="active" label='Active'/>
            </SimpleForm>
        </Edit>
    )
};

export const CustomCheckShow = props => (
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
            <TextField source="name" />
            <ChipField size="small" source="schedule" />
            <TextField source="description" />
            <TextField source="source" />
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

export const CustomCheckCreate = props => {
    const notify = useNotify();
    const refresh = useRefresh();
    const onFailure = (error) => {
        notify(`Could not create custom check: ${JSON.stringify(error.body)}`);
        refresh();
    };
    return <Create {...props} onFailure={onFailure}>
        <SimpleForm >
            <ReferenceInput label="DB" source="database_id" reference="dbs">
                <SelectInput optionText="name" validate={[required()]}/>
            </ReferenceInput>
            <TextInput source="name" label="DQ Check name" validate={[required()]}/>
            <TextInput source="schedule" validate={validateCrontab}/>
            <TextInput multiline fullWidth source="description" />
            <TextInput multiline fullWidth label='SQL Source (your query should return 0 rows for the DQ check to succeed)' source="source" defaultValue="SELECT * FROM (SELECT 1) AS dummy WHERE 1=2" validate={[required()]}/>
            <BooleanInput source="active" label='Active'/>
        </SimpleForm>
    </Create>
};
