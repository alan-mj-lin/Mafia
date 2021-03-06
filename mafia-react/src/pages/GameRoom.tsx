import React, { useState } from 'react';
import { useParams, Redirect } from 'react-router-dom';

import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Slide from '@material-ui/core/Slide';
import useScrollTrigger from '@material-ui/core/useScrollTrigger';

import { useQuery } from 'react-query';
import axios from 'axios';
import Cookies from 'js-cookie';
import { stringify } from 'querystring';

import { PlayerCard } from '../components/PlayerCard';
import { MessageSideBar } from '../components/MessageSideBar';
import { ErrorDialog } from '../components/ErrorDialog';
import { styleDay, styleNight } from '../helpers/DayAndNight';

import {
  gameStart,
  nightStart,
  killRequest,
  healRequest,
  checkRequest,
  voteRequest,
  endVotesRequest,
  skipTurnRequest,
} from '../api/';

import { API_URL } from '../var/env';
import { EntryModal } from '../components/EntryModal';

interface RouteParams {
  roomId: string;
}

interface PlayerType {
  name: string;
  role: string;
  status: string;
  userId: string;
  checked: boolean;
}

interface Props {
  /**
   * Injected by the documentation to work in an iframe.
   * You won't need it on your project.
   */
  window?: () => Window;
  children: React.ReactElement;
}

function HideOnScroll(props: Props) {
  const { children, window } = props;
  // Note that you normally won't need to set the window ref as useScrollTrigger
  // will default to window.
  // This is only being set here because the demo is in an iframe.
  const trigger = useScrollTrigger({ target: window ? window() : undefined });

  return (
    <Slide appear={false} direction="up" in={!trigger}>
      {children}
    </Slide>
  );
}

export const GameRoom = (props: Props) => {
  const classes = useStyles();
  const params = useParams<RouteParams>();
  const [errorMessage, setErrorMessage] = useState<string>('');
  const { isLoading, error, data } = useQuery(
    params.roomId,
    async () => {
      const room = await axios.get(`${API_URL}/room?roomId=${params.roomId}`, {
        withCredentials: true,
      });
      if (room.data.phase === 'voting') {
        styleDay();
      } else {
        styleNight();
      }
      // console.log(room);
      return room;
    },
    {
      refetchInterval: 2000,
    },
  );
  function showErrorMessage(message: string, delayToHide: number = 5000) {
    setErrorMessage(message);
    setTimeout(() => {
      setErrorMessage('');
    }, delayToHide);
  }
  const playerData = data?.data.players.find(
    (player: PlayerType) => player.userId === Cookies.get('userId'),
  );
  return (
    <div>
      {error && (
        <Redirect
          to={{
            pathname: '/notfound',
          }}
        />
      )}
      {!isLoading && data?.status !== 200 && (
        <Redirect
          to={{
            pathname: '/notfound',
          }}
        />
      )}
      {!isLoading && data?.status === 200 && (
        <div>
          <EntryModal
            isRoomMaster={data?.data.roomMaster === Cookies.get('userId') ? true : false}
            playerData={playerData}
            roomId={params.roomId}
          />
          <Typography variant="h2">
            Game Room
            {data?.data.roomMaster === Cookies.get('userId') && (
              <span className={classes.headerNote}> - You are room master!</span>
            )}
          </Typography>
          <Grid container className={classes.root} spacing={2}>
            {data?.data.players.map((player: PlayerType, index: number) => {
              const isUser = player.userId === Cookies.get('userId');
              return (
                <Grid
                  item
                  key={index}
                  data-is-user={isUser}
                  style={{ order: isUser ? -1 : 0 }}
                >
                  <PlayerCard
                    name={player.name}
                    role={
                      player.userId === Cookies.get('userId') ||
                      data?.data.roomMaster === Cookies.get('userId') ||
                      (playerData !== undefined &&
                        playerData.role === 'mafia' &&
                        player.role === 'mafia') ||
                      data?.data.status === 'ended'
                        ? player.role
                        : '???'
                    }
                    trueRole={player.role}
                    checked={
                      playerData !== undefined && playerData.role === 'detective'
                        ? player.checked
                        : false
                    }
                    status={player.status}
                    isUser={player.userId === Cookies.get('userId')}
                    phase={data?.data.phase}
                    onKill={async (event) =>
                      await killRequest(params.roomId, player.userId).catch((err) => {
                        if (err.response.status >= 400)
                          showErrorMessage(err.response.data.message);
                      })
                    }
                    onHeal={async (event) =>
                      await healRequest(params.roomId, player.userId).catch((err) => {
                        if (err.response.status >= 400)
                          showErrorMessage(err.response.data.message);
                      })
                    }
                    onCheck={async (event) =>
                      await checkRequest(params.roomId, player.userId).catch((err) => {
                        if (err.response.status >= 400)
                          showErrorMessage(err.response.data.message);
                      })
                    }
                    onHang={async (event) =>
                      await voteRequest(params.roomId, player.userId).catch((err) => {
                        if (err.response.status >= 400)
                          showErrorMessage(err.response.data.message);
                      })
                    }
                  />
                </Grid>
              );
            })}
          </Grid>

          <MessageSideBar
            messages={
              playerData !== undefined
                ? data?.data.gameMessages
                : data?.data.observerMessages
            }
            errorMessage={errorMessage}
            handleErrorClose={() => setErrorMessage('')}
            phase={data?.data.phase}
          />

          <HideOnScroll {...props}>
            <AppBar position="fixed" color="primary" className={classes.appBar}>
              <Toolbar>
                <ButtonGroup>
                  <Button
                    variant="contained"
                    disabled={Cookies.get('userId') !== data?.data.roomMaster}
                    onClick={async () =>
                      await skipTurnRequest(params.roomId)
                        .then(() => {
                          if (data?.data.phase === 'voting') styleDay();
                        })
                        .catch((error) => {
                          if (error.response.status >= 400)
                            showErrorMessage(error.response.data.message);
                        })
                    }
                  >
                    Skip Turn
                  </Button>
                  <Button
                    variant="contained"
                    disabled={
                      Cookies.get('userId') !== data?.data.roomMaster ||
                      data?.data.phase !== 'voting'
                    }
                    onClick={async () =>
                      await endVotesRequest(params.roomId).catch((error) => {
                        if (error.response.status >= 400)
                          showErrorMessage(error.response.data.message);
                      })
                    }
                  >
                    End Votes
                  </Button>
                  <Button
                    variant="contained"
                    disabled={
                      Cookies.get('userId') !== data?.data.roomMaster ||
                      data?.data.phase !== 'voting'
                    }
                    onClick={async () =>
                      await nightStart(params.roomId)
                        .then(styleNight)
                        .catch((err) => {
                          if (err.response.status >= 400)
                            showErrorMessage(err.response.data.message);
                        })
                    }
                  >
                    Start Night
                  </Button>
                  <Button
                    variant="contained"
                    disabled={
                      Cookies.get('userId') !== data?.data.roomMaster ||
                      data?.data.status !== 'pre-game'
                    }
                    onClick={async () =>
                      await gameStart(params.roomId)
                        .then(styleDay)
                        .catch((error) => {
                          if (error.response.status >= 400)
                            showErrorMessage(error.response.data.message);
                        })
                    }
                  >
                    Start Game
                  </Button>
                </ButtonGroup>
                {/* {Cookies.get('userId') && <h2>{Cookies.get('userId')}</h2>} */}
              </Toolbar>
            </AppBar>
          </HideOnScroll>
        </div>
      )}
    </div>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      width: '80vw',
    },
    headerNote: {
      fontSize: '0.5em',
      verticalAlign: 'middle',
      fontStyle: 'italic',
      color: 'red',
    },
    paper: {
      height: 140,
      width: 100,
    },
    control: {
      padding: theme.spacing(2),
    },
    appBar: {
      top: 'auto',
      bottom: 0,
    },
  }),
);
