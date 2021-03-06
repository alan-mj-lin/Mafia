import React from 'react';

import { Card, Button, ButtonGroup } from 'react-bootstrap';

import Avatar from '@material-ui/core/Avatar';
import { red, green, grey } from '@material-ui/core/colors';
import { makeStyles, createStyles, Theme } from '@material-ui/core/styles';

import spyicon from '../images/spyicon.png';
import spyiconInverted from '../images/spyicon-inverted.png';

export interface PlayerCardProps {
  name: string;
  role: string;
  trueRole: string;
  status: string;
  phase: string;
  checked: boolean;
  isUser: boolean;
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
  isUser,
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
  const isDay = phase === 'voting';
  return (
    <Card className={`${classes.card} ${isUser && classes.isUser}`}>
      <Card.Img
        className={classes.image}
        variant="top"
        src={isUser || isDay ? spyicon : spyiconInverted}
      />
      <Card.Body className={classes.cardBody}>
        <div className={classes.infoGroup}>
          <div className={classes.avatar}>{avatar}</div>
          <div className={classes.infoText}>
            <Card.Title className={classes.name}>{name}</Card.Title>
            <Card.Text>
              {role}, {status}
            </Card.Text>
          </div>
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
      background: 'black',
      color: 'white',
    },
    isUser: {
      background: '#cfdbff',
      color: 'black',
      '&::before': {
        content: '"(You)"',
        padding: '0.5rem',
        position: 'absolute',
        top: '-1px',
        right: '-1px',
        fontStyle: 'italic',
        background: 'red',
        color: 'yellow',
        borderRadius: '0 0.25rem 0 0.25rem',
      },
    },
    image: {
      width: '6rem',
      margin: 'auto',
      marginTop: '-1rem',
    },
    cardBody: {
      padding: '1rem',
    },
    infoGroup: {
      display: 'grid',
      gridTemplateColumns: '1fr 3fr',
      gridGap: '1em',
    },
    infoText: {
      margin: 'auto',
      overflowWrap: 'anywhere',
    },
    name: {
      overflowWrap: 'anywhere',
    },
    avatar: {
      padding: '1rem 0 0.25rem 1rem',
    },
    actionButton: {
      fontSize: '12px',
    },
  }),
);
