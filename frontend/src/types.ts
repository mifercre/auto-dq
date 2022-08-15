import {
    Record,
    Identifier,
} from 'ra-core';

export interface CheckExecution extends Record {
    id: Identifier;
    exec_time: Date;
    status: string;
    results: string;
    check_name: string;
}

export interface Check extends Record {
    id: Identifier;
    name: string;
    schedule: string;
    description: string;
}
