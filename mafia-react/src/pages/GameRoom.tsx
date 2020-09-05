import React from "react";
import { useParams, Redirect } from 'react-router-dom';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import { useQuery } from 'react-query';
import axios from 'axios';

import { PlayerCard } from '../components/PlayerCard';
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

export const GameRoom = () => {
    const classes = useStyles();
    const params = useParams<RouteParams>();
    const { isLoading, error, data} = useQuery(params.roomId, 
        async () => {
            const room =  await axios.get(`${API_URL}/room?roomId=${params.roomId}`)
            return room;
        },
        {
            refetchInterval: 2000
        }
    )
    console.log(data?.data);
    return (
        <div>
            {error && <Redirect to={{
                pathname: "/notfound"
            }}/>}
            {(data?.data.message === "Not Found") && <Redirect to={{
                pathname: "/notfound"
            }}/>}
            <Typography variant="h2">Game Room</Typography>
            <Grid container className={classes.root} spacing={2}>
                {data?.data.players.map((player: any) => {
                    return (
                        <Grid item>
                            <PlayerCard name={player.name} role={player.role} status={player.status} />
                        </Grid>
                    )
                })}
            </Grid>
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
  }),
);