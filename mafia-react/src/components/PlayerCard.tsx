import React from 'react';

import { Card, Button } from 'react-bootstrap';

import spyicon from '../images/spyicon.png';

export interface PlayerCardProps {
  name: string;
  role: string;
  status: string;
}

export const PlayerCard = ({ name, role, status }: PlayerCardProps) => {
  return (
    <Card style={{ width: '18rem' }}>
      <Card.Img variant="top" src={spyicon} />
      <Card.Body>
        <Card.Title>{name}</Card.Title>
        <Card.Text>{role}</Card.Text>
        <Card.Text>{status}</Card.Text>
        <Button variant="primary">Kill</Button>
      </Card.Body>
    </Card>
  );
};
