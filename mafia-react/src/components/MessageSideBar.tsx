import React, { useState } from 'react';

import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemAvatar from '@material-ui/core/ListItemAvatar';
import ListItemText from '@material-ui/core/ListItemText';
import Avatar from '@material-ui/core/Avatar';
import Drawer from '@material-ui/core/Drawer';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import { ErrorDialog } from '../components/ErrorDialog';

import spyicon from '../images/spyicon.png';
import spyiconInverted from '../images/spyicon-inverted.png';

interface MessageType {
  primary: string;
  secondary: string;
}

export interface MessageSideBarProps {
  messages: MessageType[];
  errorMessage: string;
  handleErrorClose: () => void;
  phase: string;
}

export const MessageSideBar = ({
  messages,
  errorMessage,
  handleErrorClose,
  phase,
}: MessageSideBarProps) => {
  const classes = useStyles();
  const isDay = phase === 'voting';
  return (
    <Drawer variant="permanent" className={classes.drawer} anchor="right">
      <ErrorDialog
        isStartPage={false}
        message={errorMessage}
        isOpen={errorMessage !== '' ? true : false}
        handleClick={handleErrorClose}
      />
      <List className={`${classes.list} ${isDay && classes.isDay}`}>
        {messages.map((message, index) => {
          return (
            <ListItem key={index}>
              <ListItemAvatar>
                <Avatar src={isDay ? spyicon : spyiconInverted} />
              </ListItemAvatar>
              {isDay ? (
                <ListItemText primary={message.primary} secondary={message.secondary} />
              ) : (
                <ListItemText
                  primary={message.primary}
                  secondary={message.secondary}
                  classes={{ secondary: classes.secondaryText }}
                />
              )}
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
      border: 'none',
      background: 'black',
      color: 'white',
    },
    list: {
      width: '18vw',
      flexShrink: 0,
      background: 'black',
      color: 'white',
    },
    secondaryText: {
      color: 'lightgrey',
    },
    secondaryTextDay: {
      color: 'black',
    },
    isDay: {
      background: 'white',
      color: 'black',
    },
  }),
);
