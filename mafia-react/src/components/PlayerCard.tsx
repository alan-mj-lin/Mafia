import React from 'react';

import { Card, Button, ButtonGroup } from 'react-bootstrap';

import Avatar from '@material-ui/core/Avatar';
import { red, green, grey } from '@material-ui/core/colors';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import spyicon from '../images/spyicon.png';

export interface PlayerCardProps {
  name: string;
  role: string;
  trueRole: string;
  status: string;
  phase: string;
  checked: boolean;
  onKill: (event: React.MouseEvent<unknown>) => void;
  onCheck: (event: React.MouseEvent<unknown>) => void;
  onHeal: (event: React.MouseEvent<unknown>) => void;
  onHang: (event: React.MouseEvent<unknown>) => void;
}

export const PlayerCard = ({
  name,
  role,
  trueRole,
  status,
  phase,
  checked,
  onKill,
  onHeal,
  onCheck,
  onHang,
}: PlayerCardProps) => {
  const classes = useStyles();
  let avatar;
  if (!checked) {
    avatar = <Avatar className={classes.grey}></Avatar>;
  } else if (checked && trueRole === 'mafia') {
    avatar = <Avatar className={classes.red}></Avatar>;
  } else if (checked && trueRole !== 'mafia') {
    avatar = <Avatar className={classes.green}></Avatar>;
  }
  return (
    <Card className={classes.card}>
      <Card.Img className={classes.image} variant="top" src={spyicon} />
      <Card.Body style={{ padding: '1rem' }}>
        <div className={classes.infoGroup}>
          <div className={classes.infoText}>
            <Card.Title className={classes.name}>{name}</Card.Title>
            <Card.Text>
              {role} {status}
            </Card.Text>
          </div>
          <div className={classes.avatar}>{avatar}</div>
        </div>
        <hr></hr>
        <ButtonGroup>
          <Button
            className={classes.actionButton}
            variant="primary"
            disabled={phase !== 'mafia'}
            onClick={(event) => onKill(event)}
          >
            Kill
          </Button>
          <Button
            className={classes.actionButton}
            variant="primary"
            disabled={phase !== 'detective'}
            onClick={(event) => onCheck(event)}
          >
            Check
          </Button>
          <Button
            className={classes.actionButton}
            variant="primary"
            disabled={phase !== 'doctor'}
            onClick={(event) => onHeal(event)}
          >
            Heal
          </Button>
          <Button
            className={classes.actionButton}
            variant="primary"
            disabled={phase !== 'voting'}
            onClick={(event) => onHang(event)}
          >
            Hang
          </Button>
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
    card: {
      width: '15rem',
    },
    image: {
      width: '10rem',
      margin: 'auto',
    },
    infoGroup: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, 50%)',
    },
    infoText: {
      margin: 'auto',
    },
    name: {
      overflowWrap: 'anywhere',
    },
    avatar: {
      padding: '1rem',
    },
    actionButton: {
      fontSize: '12px',
    },
  }),
);
