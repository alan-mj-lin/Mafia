import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';

import { createStyles, makeStyles, withStyles, Theme } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';

import axios from 'axios';
import { stringify } from 'querystring';

import { ErrorDialog } from '../components/ErrorDialog';

import { styleDay, styleNight } from '../helpers/DayAndNight';

import { API_URL } from '../var/env';

export const StartPage = () => {
  const classes = useStyles();
  const history = useHistory();
  const [displayName, setDisplayName] = useState<string>('');
  const [roomId, setRoomId] = useState<string>('');
  const [mafiaNum, setMafiaNum] = useState<string>('3');
  const [errorMessage, setErrorMessage] = useState<string>('');

  styleDay();

  return (
    <Container maxWidth="sm">
      <Typography variant="h2">Mafia</Typography>
      <form className={classes.root} noValidate autoComplete="off">
        <StyledTextField
          id="gamename"
          onChange={(event) => {
            setDisplayName(event.target.value);
          }}
          label="Display Name"
        />
        <StyledTextField
          id="room"
          onChange={(event) => {
            setRoomId(event.target.value);
            console.log(roomId);
          }}
          label="Room ID"
        />
        <Button
          variant="contained"
          color="primary"
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
                history.push(`/room/${roomId}`);
                console.log(roomId, displayName);
              })
              .catch((error) => {
                console.log(error);
                if (error.response?.status >= 400) {
                  setErrorMessage(error.response.data.message);
                } else {
                }
              });
          }}
        >
          Join Room
        </Button>
        <br />
        <StyledTextField
          id="mafia"
          value={mafiaNum}
          onChange={(event) => {
            setMafiaNum(event.target.value);
          }}
          label="Number of Mafia"
        />
        <br />
        <Button
          variant="contained"
          color="primary"
          onClick={async () => {
            await axios
              .post(`${API_URL}/actions/create-room`, stringify({ numMafia: mafiaNum }), {
                withCredentials: true,
              })
              .then((data) => {
                console.log(data);
                history.push(`/room/${data?.data.roomId}`);
              });
          }}
        >
          Create Room
        </Button>
      </form>
      <ErrorDialog
        isStartPage={true}
        handleClick={() => setErrorMessage('')}
        message={errorMessage}
        isOpen={errorMessage !== '' ? true : false}
      />
    </Container>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      '& > *': {
        margin: theme.spacing(1),
      },
    },
    textField: {
      color: 'white',
    },
  }),
);

const StyledTextField = withStyles({
  root: {
    color: 'white',
    '& label.Mui-focused': {
      color: 'white',
    },
    '& label': {
      color: 'lightgrey',
    },
    '& input': {
      color: 'yellow',
    },
  },
})(TextField);
