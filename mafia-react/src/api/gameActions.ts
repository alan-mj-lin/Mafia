import axios, { AxiosResponse } from 'axios';
import { stringify } from 'querystring';
import { API_URL } from '../var/env';

export function gameStart(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/room/${roomId}/start`, null, { withCredentials: true });
}

export function nightStart(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/room/${roomId}/night`, null, { withCredentials: true });
}

export function killRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/room/${roomId}/kill`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function healRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/room/${roomId}/heal`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function checkRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/room/${roomId}/check`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function voteRequest(roomId: string, targetId: string): Promise<AxiosResponse> {
  return axios.patch(
    `${API_URL}/room/${roomId}/vote`,
    stringify({ targetId: targetId }),
    { withCredentials: true },
  );
}

export function endVotesRequest(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/room/${roomId}/hang`, null, { withCredentials: true });
}

export function skipTurnRequest(roomId: string): Promise<AxiosResponse> {
  return axios.patch(`${API_URL}/room/${roomId}/skip`, null, { withCredentials: true });
}
