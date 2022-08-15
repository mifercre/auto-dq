import * as React from "react";
import { useCallback, useState, useEffect, FC } from "react";
import { useVersion, useDataProvider, DataProvider } from 'react-admin';
import { Card } from "@material-ui/core";
import { CheckExecution } from '../types';
import LatestCheckExecutions from "../dashboard/LatestCheckExecutions";
import { Record } from 'ra-core';
import CardWithTitle from "../dashboard/CardWithTitle";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { colors, tryParseJSON } from "../utils";

interface State {
    lastCheckExecutions: CheckExecution[];
}

interface AsideProps {
    record?: Record
}

const formatXAxis = value => {
    const d = new Date(value)
    return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate()
}

export const AsideChecks: FC<AsideProps> = ({ record }) => {
    const version = useVersion();
    const dataProvider:DataProvider = useDataProvider();
    const [state, setState] = useState<State>({ lastCheckExecutions: [] });
    const fetchLatestCheckExecutions = useCallback(async () => {
        const fromDate = new Date();
        fromDate.setDate(fromDate.getDate() - 10)
        const { data: checkExecs } = await dataProvider.getListUnpaginated('check_executions', {
            filter: { 
                check_id: record? record.id : 0, 
                exec_time___gte: fromDate.toISOString() + '"' 
            },
            sort: { field: 'exec_time', order: 'DESC' },
            limit: 100
        });
        setState(state => ({
                ...state,
                lastCheckExecutions: checkExecs,
            })
        );
    }, [dataProvider]);
    useEffect(() => {
        fetchLatestCheckExecutions();
    }, [version]);
    const { lastCheckExecutions } = state;

    var stats: any[] = [];
    var statsSeries: Set<string> = new Set();

    lastCheckExecutions.forEach((exec) => {
        const results = tryParseJSON(exec.results);
        // Add results keys to the series set 
        Object.keys(results).forEach(statsSeries.add, statsSeries);
        stats.unshift(Object.assign({}, { date: exec.exec_time }, results));
    });
    return (
        <div style={{ width: '40%', marginLeft: '1em', height: 'fit-content' }}>
            <Card>
                <LatestCheckExecutions title='Latest Executions' checkExecutions={lastCheckExecutions} />
            </Card>
            <br/>
            <CardWithTitle title='Latest Executions Results'>
                <ResponsiveContainer height={400} width='100%'>
                    <LineChart data={stats} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                        <XAxis dataKey="date" tickFormatter={formatXAxis}/>
                        <YAxis />
                        <Legend verticalAlign="top" height={36}/>
                        <Tooltip />
                        <CartesianGrid stroke="#f5f5f5" />
                        {Array.from(statsSeries).map((k, i) => (
                            <Line type="monotone" dataKey={k} stroke={colors[i]} yAxisId={0} />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </CardWithTitle>
        </div>
    );
};
