import axios, { AxiosResponse } from 'axios';
import { stringify } from 'querystring';
import { API_URL } from '../var/env';

export function gameStart(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/rooms/${roomId}/start`, null, { withCredentials: true });
}

export function nightStart(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/rooms/${roomId}/night`, null, { withCredentials: true });
}

export function killRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/rooms/${roomId}/kill`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function healRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/rooms/${roomId}/heal`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function checkRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/rooms/${roomId}/check`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function voteRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/rooms/${roomId}/vote`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function endVotesRequest(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/rooms/${roomId}/hang`, null, { withCredentials: true });
}

export function skipTurnRequest(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/rooms/${roomId}/skip`, null, { withCredentials: true });
}

export function playerDisconnect(roomId: string): Promise<AxiosResponse> {
  return axios.get(`${API_URL}/rooms/${roomId}/disconnect`, { withCredentials: true });
}
