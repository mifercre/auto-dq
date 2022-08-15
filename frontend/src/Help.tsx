import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import { Title } from 'react-admin';
import { makeStyles } from '@material-ui/core/styles';
import { Typography } from "@material-ui/core";

const useStyles = makeStyles(theme => ({
    main: {
        padding: 24,
        justifyContent: 'space-between',
        alignItems: 'center',
    },
    divHelp: { display: 'inline-block', width: '100%' }
}));

const Help = (props => {
    const classes = useStyles(props);
    return (
        <Card className={classes.main}>
            <Title title="Help Page" />
            <Typography color="textPrimary" variant="h4">Data Quality Measurements</Typography>
            <CardContent>
                <Typography color="textPrimary" variant="h6">Uniqueness</Typography>
                <Typography color="textSecondary">
                Checks that there are no duplicates in all values from the input source.
                </Typography>
            </CardContent>
            <CardContent>
                <Typography color="textPrimary" variant="h6">Outliers</Typography>
                <Typography color="textSecondary">
                Checks that all values from the input source are within 3 standard deviations (i.e there are no outliers)
                </Typography>
            </CardContent>
            <CardContent>
                <Typography color="textPrimary" variant="h6">Non-null</Typography>
                <Typography color="textSecondary">
                Checks that all values from the input source are non-null
                </Typography>
            </CardContent>
            <CardContent>
                <Typography color="textPrimary" variant="h6">Freshness</Typography>
                <Typography color="textSecondary">
                Checks that all values (timestamps) from the input source are within certain time delta
                </Typography>
            </CardContent>
            <CardContent>
                <Typography color="textPrimary" variant="h6">Ordered (incremental)</Typography>
                <Typography color="textSecondary">
                Checks that all values from the input source are in order (smaller to bigger)
                </Typography>
            </CardContent>
            {/* TODO: */}
            {/* <CardContent>
                <Typography color="textPrimary" variant="h6">Consistency</Typography>
                <Typography color="textSecondary">
                Checks that all values from the input source and the target are consistent (i.e. they are the same)<br/>
                Example: count of daily events from raw table A should be the same as the count of daily events on presto view B
                </Typography>
            </CardContent> */}
            <br/>
            <br/>
            <Typography color="textPrimary" variant="h4">FAQ</Typography>
            <CardContent>
                <Typography color="textPrimary" variant="h6">How to setup checks for a new data source?</Typography>
                <Typography color="textSecondary">
                There are two possible ways to create new checks. You can either:
                <br/>
                - Go to DBs &gt; Select a DB &gt; Select schema &gt; Select table &gt; Click on any of the checks available for the table or the columns. This will automatically create an schedule a check to run daily (at a random specific hour/minute). You can later view or change the details of the check if needed.
                <br/>
                - Go to Checks &gt; Click on Create (on the top right corner) &gt; Fill the form with the needed fields. In this case you are expected to write the needed source/target SQL query that will be run by DQ system to retrieve the data and execute the check.
                </Typography>
            </CardContent>
            <br/>
            <br/>
            <Typography color="textPrimary" variant="h4">Contact</Typography>
            <CardContent>
                <Typography color="textSecondary">
                For further questions/doubts, you can submit an issue to [github repo]
                </Typography>
            </CardContent>
        </Card>
    )
});

export default Help;