import React from "react";
import { useParams, Redirect } from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import { useQuery } from 'react-query';
import axios from 'axios';
import { API_URL } from '../var/env';

interface RouteParams {
    roomId: string;
}

export const GameRoom = () => {
    const params = useParams<RouteParams>();
    const { isLoading, error, data} = useQuery(params.roomId, async () => {
        const room =  await axios.get(`${API_URL}/room?roomId=${params.roomId}`)
        return room;
    })
    return (
        <div>
            {error && <Redirect to={{
                pathname: "/notfound"
            }}/>}
            {(data?.data.message === "Not Found") ? <Redirect to={{
                pathname: "/notfound"
            }}/> : <Typography variant="h2">Game Room</Typography> }
            
        </div>
    )
}