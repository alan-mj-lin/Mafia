import React, { useState } from 'react';

import { makeStyles, Theme, createStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import IconButton from '@material-ui/core/IconButton';
import Collapse from '@material-ui/core/Collapse';
import Button from '@material-ui/core/Button';
import CloseIcon from '@material-ui/icons/Close';

export interface ErrorDialogProps {
  isOpen: boolean;
  message: string;
  handleClick: () => void;
}

export const ErrorDialog = ({ isOpen, message, handleClick }: ErrorDialogProps) => {
  const classes = useStyles();
  return (
    <div className={classes.root}>
      <Collapse in={isOpen}>
        <Alert
          severity="error"
          action={
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={() => {
                handleClick();
              }}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          }
        >
          {message}
        </Alert>
      </Collapse>
    </div>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      zIndex: 9999,
      width: '18vw',
      position: 'relative',
      margin: 'auto',
      top: '30vh',
      '& > * + *': {
        marginTop: theme.spacing(2),
      },
    },
  }),
);
