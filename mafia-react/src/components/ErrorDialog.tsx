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
  isStartPage: boolean;
}

export const ErrorDialog = ({
  isOpen,
  message,
  handleClick,
  isStartPage,
}: ErrorDialogProps) => {
  const classes = useStyles();
  return (
    <div className={isStartPage ? classes.startpage : classes.root}>
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
      position: 'fixed',
      right: '1',
      bottom: '0',
      '& > * + *': {
        marginTop: theme.spacing(2),
      },
    },
    startpage: {
      width: '100%',
      '& > * + *': {
        marginTop: theme.spacing(2),
      },
    },
  }),
);
