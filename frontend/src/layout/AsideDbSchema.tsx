import * as React from "react";
import { FC } from "react";
import { Record } from 'ra-core';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import CardWithTitle from "../dashboard/CardWithTitle";


const colors = [
    '#ef476f', // active
    '#F5F5F5' // inactive
]
interface AsideProps {
    record?: Record
}

export const AsideDBSchema: FC<AsideProps> = ({ record }) => {
    let data = [{
        "name": "tables with checks",
        "value": record? record.tables_with_checks : 0
    },
    {
        "name": "tables without",
        "value": record? record.table_count - record.tables_with_checks : 0
    }];
    return (
        <div style={{ minWidth: '20%', marginLeft: '1em', height: 'fit-content' }}>        
            <CardWithTitle title='Checks coverage' subtitle='(# of tables with checks, out of all tables in this schema)'>
            <ResponsiveContainer height={200} width='100%'>
                <PieChart width={150} height={150}>
                    <Pie data={data} dataKey="value" outerRadius={50} fill="#8884d8" isAnimationActive={false} label >
                    {
                        data.map((entry, i) => <Cell fill={colors[i % colors.length]}/>)
                    }
                    </Pie>
                </PieChart>
                </ResponsiveContainer>
            </CardWithTitle>
        </div>
    );
};