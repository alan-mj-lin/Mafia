import React, { useState } from 'react';
import axios from 'axios';
import { stringify } from 'querystring';
import Cookies from 'js-cookie';

import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Modal from '@material-ui/core/Modal';
import Backdrop from '@material-ui/core/Backdrop';
import Fade from '@material-ui/core/Fade';

import { PlayerType } from '../types';

import { API_URL } from '../var/env';

export interface EntryModalProps {
  playerData: PlayerType | undefined;
  roomId: string;
  isRoomMaster: boolean;
}

export const EntryModal = ({ playerData, roomId, isRoomMaster }: EntryModalProps) => {
  const classes = useStyles();
  const [displayName, setDisplayName] = useState<string>('');
  const [open, setOpen] = useState<boolean>(true);
  const handleClose = () => {
    setOpen(false);
  };
  return (
    <Modal
      className={classes.modal}
      open={
        playerData !== undefined || Cookies.get('userId') === 'observer' || isRoomMaster
          ? false
          : true
      }
      closeAfterTransition
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
      }}
    >
      <Fade in={open}>
        <div className={classes.paper}>
          <h2 id="transition-modal-title">Room {roomId}</h2>
          <TextField
            id="gamename"
            onChange={(event) => {
              setDisplayName(event.target.value);
            }}
            label="Display Name"
          />
          <Button
            onClick={async () => {
              await axios
                .post(
                  `${API_URL}/actions/join-room`,
                  stringify({
                    roomId: roomId,
                    name: displayName,
                  }),
                  { withCredentials: true },
                )
                .then((data) => {
                  console.log(data);
                });
              handleClose();
            }}
          >
            Join Room
          </Button>
          <Button
            onClick={async () => {
              await axios
                .post(
                  `${API_URL}/actions/join-room`,
                  stringify({
                    roomId: roomId,
                    name: displayName,
                    option: 'observe',
                  }),
                  { withCredentials: true },
                )
                .then((data) => {
                  console.log(data);
                });
              handleClose();
            }}
          >
            Observe
          </Button>
        </div>
      </Fade>
    </Modal>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    modal: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    paper: {
      backgroundColor: theme.palette.background.paper,
      border: '2px solid #000',
      boxShadow: theme.shadows[5],
      padding: theme.spacing(2, 4, 3),
    },
  }),
);
