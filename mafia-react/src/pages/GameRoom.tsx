import React, { useState } from "react";
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

import { PlayerCard } from '../components/PlayerCard';
import { MessageSideBar } from '../components/MessageSideBar';

import { API_URL } from '../var/env';

interface RouteParams {
    roomId: string;
}

interface PlayerType {
    name: string;
    role: string;
    status: string;
    userId: string;
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
    const { isLoading, error, data} = useQuery(params.roomId, 
        async () => {
            const room =  await axios.get(`${API_URL}/room?roomId=${params.roomId}`)
            
            console.log(room)
            return room;
        },
        {
            refetchInterval: 2000
        }
    )

    return (
        <div>
            {(error) && <Redirect to={{
                pathname: "/notfound"
            }}/>}
            {(!isLoading && data?.status !== 200) && <Redirect to={{
                pathname: "/notfound"
            }}/>}
            {(!isLoading && data?.status ===200) &&
            <div>
                <Typography variant="h2">Game Room</Typography>
                <Grid sm={8} container className={classes.root} spacing={2}>
                    {data?.data.players.map((player: PlayerType) => {
                        const playerData = data?.data.players.find((player: PlayerType)=> player.userId === Cookies.get('userId'));
                        return (
                            <Grid item>
                                <PlayerCard name={player.name} role={
                                    (player.userId === Cookies.get('userId') || (playerData !== undefined && playerData.role === 'mafia' && player.role === 'mafia') || data?.data.status === 'ended') ? player.role : '???'
                                } status={player.status} />
                            </Grid>
                        )
                    })}
                </Grid>
                <MessageSideBar messages={data?.data.gameMessages}/>
                <HideOnScroll {...props}>
                    <AppBar position="fixed" color="primary" className={classes.appBar}>
                        <Toolbar>
                            <ButtonGroup>
                                <Button variant="contained" disabled={(Cookies.get('userId') !== data?.data.roomMaster)}>Skip Turn</Button>
                                <Button variant="contained" disabled={(Cookies.get('userId') !== data?.data.roomMaster)}>Hang</Button>
                                <Button variant="contained" disabled={(Cookies.get('userId') !== data?.data.roomMaster)}>Start Night</Button>
                                <Button variant="contained" disabled={(Cookies.get('userId') !== data?.data.roomMaster)}>Start Game</Button>
                            </ButtonGroup>
                            {(Cookies.get('userId')) && <h2>{Cookies.get('userId')}</h2>}
                        </Toolbar>
                    </AppBar>
                </HideOnScroll>
            </div>
            }           
        </div>
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
    appBar: {
        top: 'auto',
        bottom: 0,
    },
  }),
);