import React from "react";

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import ListItemText from '@material-ui/core/ListItemText';
import Avatar from '@material-ui/core/Avatar';
import Drawer from '@material-ui/core/Drawer';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import spyicon from '../images/spyicon.png';

const drawerWidth = 500;

interface MessageType {
    primary: string;
    secondary: string;
}

export interface MessageSideBarProps {
    messages: MessageType[];
}

export const MessageSideBar = ({messages}: MessageSideBarProps) => {
    const classes = useStyles();
    return (
        <Drawer
            className={classes.drawer}
            variant="permanent"
            classes={{
            paper: classes.drawerPaper,
            }}
            anchor="right"
        >
            <List>
                {messages.map((message) => {
                    return(
                        <ListItem>
                            <ListItemAvatar>
                                <Avatar src={spyicon} />
                            </ListItemAvatar>
                            <ListItemText
                                primary={message.primary}
                                secondary={message.secondary}
                            />
                        </ListItem>
                    )
                })}
            </List>
        </Drawer>
    )
}

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      flexGrow: 1,
    },
    paper: {
      height: 140,
      width: 100,
    },
    control: {
      padding: theme.spacing(2),
    },
    drawer: {
        width: drawerWidth,
        flexShrink: 0,
    },
    drawerPaper: {
    width: drawerWidth,
    },
  }),
);