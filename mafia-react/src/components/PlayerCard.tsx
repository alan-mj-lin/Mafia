import React from 'react';

import { Card, Button, ButtonGroup } from 'react-bootstrap';

import spyicon from '../images/spyicon.png';

export interface PlayerCardProps {
  name: string;
  role: string;
  status: string;
  phase: string;
  onKill: (event: React.MouseEvent<unknown>) => void;
  // onCheck: (event: React.MouseEvent<unknown>) => void;
  // onHeal: (event: React.MouseEvent<unknown>) => void;
}

export const PlayerCard = ({
  name,
  role,
  status,
  phase,
  onKill,
}: // onCheck,
// onHeal,
PlayerCardProps) => {
  return (
    <Card style={{ width: '18rem' }}>
      <Card.Img variant="top" src={spyicon} />
      <Card.Body>
        <Card.Title>{name}</Card.Title>
        <Card.Text>{role}</Card.Text>
        <Card.Text>{status}</Card.Text>
        <ButtonGroup>
          <Button
            variant="primary"
            disabled={phase !== 'mafia'}
            onClick={(event) => onKill(event)}
          >
            Kill
          </Button>
          <Button
            variant="primary"
            disabled={phase !== 'detective'}
            // onClick={(event) => onCheck(event)}
          >
            Check
          </Button>
          <Button
            variant="primary"
            disabled={phase !== 'doctor'}
            // onClick={(event) => onHeal(event)}
          >
            Heal
          </Button>
        </ButtonGroup>
      </Card.Body>
    </Card>
  );
};
