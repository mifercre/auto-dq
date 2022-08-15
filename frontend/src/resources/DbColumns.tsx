import * as React from "react";
import { 
    TextField, Show, SimpleShowLayout, BooleanField
} from 'react-admin';

export const DBColumnShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id" />
            <TextField source="name" />
            <BooleanField source="is_partition_column" />
        </SimpleShowLayout>
    </Show>
);
