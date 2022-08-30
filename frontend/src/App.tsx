import * as React from "react";
import { Admin, Resource } from 'react-admin';
import { CheckList, CheckEdit, CheckCreate, CheckShow } from './resources/Checks';
import { CustomCheckList, CustomCheckEdit, CustomCheckCreate, CustomCheckShow } from './resources/CustomChecks';
import { CheckExecutionList, CheckExecutionShow } from './resources/ChecksExecutions';
import { DBList, DBEdit, DBShow, DBCreate } from './resources/Dbs';
import { DBSchemaList, DBSchemaShow } from './resources/DbSchemas'
import { DBTableList, DBTableShow } from './resources/DbTables';
import { DBColumnShow } from './resources/DbColumns';
import dataProvider from './DataProvider';
import { Dashboard } from './dashboard';
import Layout from './layout/Layout';
import customRoutes from './CustomRoutes';

const App = () => (
    <Admin 
        disableTelemetry
        layout={Layout}
        dataProvider={dataProvider} 
        dashboard={Dashboard}
        customRoutes={customRoutes}
    >
        <Resource name="checks" list={CheckList} edit={CheckEdit} show={CheckShow} create={CheckCreate} />
        <Resource name="custom_checks" list={CustomCheckList} edit={CustomCheckEdit} show={CustomCheckShow} create={CustomCheckCreate} />
        <Resource name="check_executions" list={CheckExecutionList} show={CheckExecutionShow} />
        <Resource name="dbs" list={DBList} edit={DBEdit} show={DBShow} create={DBCreate} />
        <Resource name="db_schemas" list={DBSchemaList} show={DBSchemaShow} />
        <Resource name="db_tables" list={DBTableList} show={DBTableShow} />
        <Resource name="db_columns" show={DBColumnShow} />

        {/* Resources without CRUD UI pages */}
        <Resource name="checks_base" />
        <Resource name="db_table_partitions"/>
        <Resource name="dbs/supported_dbs"/>
    </Admin>
);

export default App;