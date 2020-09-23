import React from 'react';

import { Card, Button, ButtonGroup } from 'react-bootstrap';

import Avatar from '@material-ui/core/Avatar';
import { red, green, grey } from '@material-ui/core/colors';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import spyicon from '../images/spyicon.png';

export interface PlayerCardProps {
  name: string;
  role: string;
  status: string;
  phase: string;
  checked: boolean;
  onKill: (event: React.MouseEvent<unknown>) => void;
  onCheck: (event: React.MouseEvent<unknown>) => void;
  onHeal: (event: React.MouseEvent<unknown>) => void;
}

export const PlayerCard = ({
  name,
  role,
  status,
  phase,
  checked,
  onKill,
  onHeal,
  onCheck,
}: PlayerCardProps) => {
  const classes = useStyles();
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
            onClick={(event) => onCheck(event)}
          >
            Check
          </Button>
          <Button
            variant="primary"
            disabled={phase !== 'doctor'}
            onClick={(event) => onHeal(event)}
          >
            Heal
          </Button>
          <span> &nbsp; </span>
          <span> &nbsp; </span>
          <span> &nbsp; </span>
          <span> &nbsp; </span>
          {checked && role === 'mafia' && <Avatar className={classes.red}></Avatar>}
          {checked && role !== 'mafia' && <Avatar className={classes.green}></Avatar>}
          {!checked && <Avatar className={classes.grey}></Avatar>}
        </ButtonGroup>
      </Card.Body>
    </Card>
  );
};

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      display: 'flex',
      '& > *': {
        margin: theme.spacing(1),
      },
    },
    red: {
      color: theme.palette.getContrastText(red[900]),
      backgroundColor: red[900],
    },
    green: {
      color: theme.palette.getContrastText(green[500]),
      backgroundColor: green[500],
    },
    grey: {
      color: theme.palette.getContrastText(grey[500]),
      backgroundColor: grey[500],
    },
  }),
);
