import * as React from 'react';
import { Layout, Sidebar } from 'react-admin';
import AppBar from './AppBar';
import Menu from './Menu';
import { lightTheme } from './Themes';

const CustomSidebar = (props: any) => <Sidebar {...props} size={200} style={{marginTop: 16}}/>;

export default (props: any) => {
    return (
        <Layout
            {...props}
            appBar={AppBar}
            sidebar={CustomSidebar}
            menu={Menu}
            theme={lightTheme}
        />
    );
};
