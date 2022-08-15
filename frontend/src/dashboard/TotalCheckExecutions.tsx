import * as React from 'react';
import { FC } from 'react';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import CancelOutlinedIcon from '@material-ui/icons/CancelOutlined';
import CardWithIcon from './CardWithIcon';

interface Props {
    title?: string;
    type?: string;
    subtitle?: string;
}

const TotalCheckExecutions: FC<Props> = ({ title, subtitle, type='success' }) => {
    return (
        <CardWithIcon
            to="/"
            icon={ type === 'success'? CheckCircleOutlineIcon: CancelOutlinedIcon }
            title={title}
            subtitle={subtitle}
            type={type}
        />
    );
};

export default TotalCheckExecutions;
