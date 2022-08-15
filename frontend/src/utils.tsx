import * as React from "react";
import { 
    TextField
} from 'react-admin';
import { Chip } from "@material-ui/core";
import CheckIcon from '@material-ui/icons/Check';
import ClearIcon from '@material-ui/icons/Clear';
import CachedIcon from '@material-ui/icons/Cached';

export const colors = ["#073b4c", "#ef476f","#06d6a0","#ffd166", "#118ab2"];

export function timeSince(date: any) {
    const d: any = new Date()
    var seconds = Math.floor((d - date) / 1000);
    var interval = seconds / 31536000;
  
    if (interval > 1) { return Math.floor(interval) + (Math.floor(interval) === 1? " year ago" : " years ago"); }
    interval = seconds / 2592000;
    if (interval > 1) { return Math.floor(interval) + (Math.floor(interval) === 1? " month ago" : " months ago"); }
    interval = seconds / 86400;
    if (interval > 1) { return Math.floor(interval) + (Math.floor(interval) === 1? " day ago" : " days ago"); }
    interval = seconds / 3600;
    if (interval > 1) { return Math.floor(interval) + (Math.floor(interval) === 1? " hour ago" : " hours ago"); }
    interval = seconds / 60;
    if (interval > 1) { return Math.floor(interval) + (Math.floor(interval) === 1? " minute ago" : " minutes ago"); }
    return Math.floor(interval) + (Math.floor(interval) === 1? " second ago" : " seconds ago");
}

export const TimeSinceNowField = props => {
    props.record.exec_time_since = timeSince(Date.parse(props.record.exec_time + 'Z'));
    return <TextField {...props} />;
};

export const LastCheckExecInfoField = props => {
    props.record.last_exec_info = props.record.status + ' (' + timeSince(Date.parse(props.record.exec_time + 'Z')) + ')';
    if (props.record.status === 'running') {
        return <Chip icon={<CachedIcon />} style={{ backgroundColor: 'lightblue' }} label={props.record.status + ' (' + timeSince(Date.parse(props.record.exec_time + 'Z')) + ')'}/>
    } else if (props.record.status === 'success') {
        return <Chip icon={<CheckIcon />} style={{ backgroundColor: 'lightgreen' }} label={props.record.status + ' (' + timeSince(Date.parse(props.record.exec_time + 'Z')) + ')'}/>
    }
    else {
        return <Chip icon={<ClearIcon  />} style={{ backgroundColor: '#ff8c8c' }} label={props.record.last_exec_info}/>
    }
};

export function tryParseJSON(jsonString) {
    try {
        var o = JSON.parse(jsonString);
        // Handle non-exception-throwing cases:
        // Neither JSON.parse(false) or JSON.parse(1234) throw errors, hence the type-checking,
        // but... JSON.parse(null) returns null, and typeof null === "object", 
        // so we must check for that, too. Thankfully, null is falsey, so this suffices:
        if (o && typeof o === "object") {
            return o;
        }
    }
    catch (e) { }
    return false;
};

export const crontabValidation = (value) => {
    var cronregex = new RegExp(/^(\*|([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])|\*\/([0-9]|1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9])) (\*|([0-9]|1[0-9]|2[0-3])|\*\/([0-9]|1[0-9]|2[0-3])) (\*|([1-9]|1[0-9]|2[0-9]|3[0-1])|\*\/([1-9]|1[0-9]|2[0-9]|3[0-1])) (\*|([1-9]|1[0-2])|\*\/([1-9]|1[0-2])) (\*|([0-6])|\*\/([0-6]))$/);
    if (!cronregex.test(value)) {
        return 'Wrong crontab format';
    }
    return undefined;
};
