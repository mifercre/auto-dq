import * as React from 'react';
import { FC, useState} from 'react';
import { DashboardMenuItem, MenuItemLink } from 'react-admin';
import AllInboxIcon from '@material-ui/icons/AllInbox';
import AssignmentTurnedInIcon from '@material-ui/icons/AssignmentTurnedIn';
import DoneAllIcon from '@material-ui/icons/DoneAll';
import SubMenu from './SubMenu';

interface Props {
    dense: boolean;
    onMenuClick: () => void;
}

const Menu: FC<Props> = ({ onMenuClick, dense }) => {
    const [state, setState] = useState({
        menuCheck: true,
        menuDb: true,
    });
    const handleToggle = (menu: string) => {
        setState(state => ({ ...state, [menu]: !state[menu] }));
    };

    const open = true;
    return (
        <div>
            {' '}
            <DashboardMenuItem onClick={onMenuClick} sidebarIsOpen={open} />
            <MenuItemLink
                to={`/check_executions`}
                primaryText='Check Executions'
                leftIcon={<DoneAllIcon />}
                onClick={onMenuClick}
                sidebarIsOpen={open}
                dense={dense}
            />
            <SubMenu
                handleToggle={() => handleToggle('menuCheck')}
                isOpen={state.menuCheck}
                sidebarIsOpen={open}
                name="Checks"
                icon={<AssignmentTurnedInIcon />}
                dense={dense}
            >
                <MenuItemLink
                    to={`/checks`}
                    primaryText='Checks'
                    onClick={onMenuClick}
                    sidebarIsOpen={open}
                    dense={dense}
                />
                <MenuItemLink
                    to={`/custom_checks`}
                    primaryText='Custom Checks'
                    onClick={onMenuClick}
                    sidebarIsOpen={open}
                    dense={dense}
                />
            </SubMenu>
            <SubMenu
                handleToggle={() => handleToggle('menuDb')}
                isOpen={state.menuDb}
                sidebarIsOpen={open}
                name="Sources"
                icon={<AllInboxIcon />}
                dense={dense}
            >
                <MenuItemLink
                    to={`/dbs`}
                    primaryText='DBs'
                    onClick={onMenuClick}
                    sidebarIsOpen={open}
                    dense={dense}
                />
                <MenuItemLink
                    to={`/db_schemas`}
                    primaryText='Schemas'
                    onClick={onMenuClick}
                    sidebarIsOpen={open}
                    dense={dense}
                />
                <MenuItemLink
                    to={`/db_tables`}
                    primaryText='Tables'
                    onClick={onMenuClick}
                    sidebarIsOpen={open}
                    dense={dense}
                />
            </SubMenu>
        </div>
    );
};

export default Menu;
