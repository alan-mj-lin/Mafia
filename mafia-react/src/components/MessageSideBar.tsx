import React, { useState } from 'react';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import ListItemText from '@material-ui/core/ListItemText';
import Avatar from '@material-ui/core/Avatar';
import Drawer from '@material-ui/core/Drawer';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import { ErrorDialog } from '../components/ErrorDialog';

import spyiconInverted from '../images/spyicon-inverted.png';

interface MessageType {
  primary: string;
  secondary: string;
}

export interface MessageSideBarProps {
  messages: MessageType[];
  errorMessage: string;
  handleErrorClose: () => void;
}

export const MessageSideBar = ({
  messages,
  errorMessage,
  handleErrorClose,
}: MessageSideBarProps) => {
  const classes = useStyles();
  return (
    <Drawer variant="permanent" className={classes.drawer} anchor="right">
      <ErrorDialog
        message={errorMessage}
        isOpen={errorMessage !== '' ? true : false}
        handleClick={handleErrorClose}
      />
      <List className={classes.list}>
        {messages.map((message, index) => {
          return (
            <ListItem key={index}>
              <ListItemAvatar>
                <Avatar src={spyiconInverted} />
              </ListItemAvatar>
              <ListItemText
                primary={message.primary}
                secondary={message.secondary}
                classes={{ secondary: classes.secondaryText }}
              />
            </ListItem>
          );
        })}
      </List>
    </Drawer>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    drawer: {
      width: 400,
      border: 'none',
      background: 'black',
      color: 'white',
    },
    list: {
      flexShrink: 0,
      background: 'black',
      color: 'white',
    },
    secondaryText: {
      color: 'lightgrey',
    },
  }),
);
