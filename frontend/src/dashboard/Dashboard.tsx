import React, {
    useState,
    useEffect,
    useCallback,
    FC,
} from 'react';
import { useVersion, useDataProvider, DataProvider } from 'react-admin';

import Welcome from './Welcome';
import TotalCheckExecutions from './TotalCheckExecutions';
import LatestCheckExecutions from './LatestCheckExecutions';
import { CheckExecution } from '../types';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import CardWithTitle from './CardWithTitle';

interface State {
    totalCheckExecutions?: number;
    lastCheckExecutions?: CheckExecution[];
    lastFailedCheckExecutions?: CheckExecution[];
    countLastSuccessCheckExecutions?: number;
    lastDaySuccessPercent?: string;
    stats?: any[];
}

const styles = {
    flex: { display: 'flex' },
    flexScrollList: { display: 'flex', maxHeight: 500 },
    flexColumn: { display: 'flex', flexDirection: 'column' },
    leftCol: { flex: 1, marginRight: '0.5em' },
    rightCol: { flex: 1, marginLeft: '0.5em' },
    singleCol: { marginTop: '1em', marginBottom: '1em' },
};

const Spacer = () => <span style={{ width: '1em' }} />;
// const VerticalSpacer = () => <span style={{ height: '1em' }} />;

const Dashboard: FC = () => {
    const [state, setState] = useState<State>({
        totalCheckExecutions: 0,
        countLastSuccessCheckExecutions: 0,
        lastDaySuccessPercent: '...',
        stats: []
    });
    const version = useVersion();
    const dataProvider:DataProvider = useDataProvider();
    
    const fetchTotalCheckExecutions = useCallback(async () => {
        const { data: checkExecutions } = await dataProvider.getOne('check_executions', {id: 'count'});
        setState(state => ({
            ...state,
            totalCheckExecutions: checkExecutions.data[0]
        }));
    }, [dataProvider]);

    const fetchLatestCheckExecutions = useCallback(async () => {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1)
        const { data: checkExecs } = await dataProvider.getListUnpaginated('check_executions', {
            filter: { exec_time___gte: yesterday.toISOString() + '"' },
            sort: { field: 'exec_time', order: 'DESC' }
        });
        const failedCheckExecs = checkExecs.filter((checkExec: CheckExecution) => checkExec.status === 'fail');
        const successCheckExecs = checkExecs.filter((checkExec: CheckExecution) => checkExec.status === 'success');
        setState(state => ({
            ...state,
            lastCheckExecutions: checkExecs,
            lastFailedCheckExecutions: failedCheckExecs,
            countLastSuccessCheckExecutions: successCheckExecs.length,
            lastDaySuccessPercent: (successCheckExecs.length !== 0 ? (successCheckExecs.length / checkExecs.length * 100).toFixed(2) : '0.0')
        }));
    }, [dataProvider]);

    

    const fetchStats = useCallback(async () => {
        const { data: stats } = await dataProvider.getOne('check_executions', {id: 'stats'});

        var prep_data: any[] = [];
        stats.data.forEach((x: number[]) => {
            prep_data.push({date: x[0], success_pct: x[2] / x[1] * 100});
        });
        setState(state => ({
            ...state,
            stats: prep_data
        }));
    }, [dataProvider]);

    useEffect(() => {
        fetchTotalCheckExecutions();
        fetchLatestCheckExecutions();
        fetchStats();
    }, [version]); // eslint-disable-line react-hooks/exhaustive-deps

    const {
        totalCheckExecutions,
        lastFailedCheckExecutions,
        countLastSuccessCheckExecutions,
        lastDaySuccessPercent,
        stats,
    } = state;
    return (
        <>
            <Welcome />
            <div style={styles.flex}>
                <div style={styles.leftCol}>
                    <div style={styles.flex}>
                        <TotalCheckExecutions title='Success percent since yesterday' subtitle={lastDaySuccessPercent + '%'} />
                    </div>
                    <div style={styles.singleCol}>
                        <div style={styles.flex}>
                            <TotalCheckExecutions title='Total checks run ever' subtitle={totalCheckExecutions + ''}/>
                            <Spacer />
                            <TotalCheckExecutions title='Successful since yesterday' subtitle={countLastSuccessCheckExecutions + ''}/>
                        </div>
                    </div>
                    <div style={styles.singleCol}>
                        <CardWithTitle title='Daily Success Percentage (all checks)'>
                            <ResponsiveContainer height={400} width='100%'>
                                <LineChart data={stats} margin={{ top: 20, right: 50, left: 5, bottom: 15 }} >
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <CartesianGrid stroke="#f5f5f5" />
                                    <Line type="monotone" dataKey="success_pct" stroke="#ff7300" yAxisId={0} />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardWithTitle>
                    </div>
                </div>
                <div style={styles.rightCol}>
                    <div style={styles.flexScrollList}>
                        <LatestCheckExecutions title='Latest Failed Check Executions' checkExecutions={lastFailedCheckExecutions} />
                    </div>
                </div>
            </div>
        </>
    );
};

export default Dashboard;
