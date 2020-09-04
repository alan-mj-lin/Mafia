import React from "react";
import { createStyles, makeStyles, Theme } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';

export const StartPage = () => {
    const classes = useStyles();

    return(
        <Container maxWidth="sm">
            <Typography variant="h2">Mafia</Typography>
            <form className={classes.root} noValidate autoComplete="off">
                <TextField id="gamename" label="Display Name" />
                <TextField id="room" label="Room ID" />
                <Button variant="contained" color="primary">
                    Join Room
                </Button>
                <Button variant="contained" color="primary">
                    Create Room
                </Button>
            </form>
        </Container>
    )
} 

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      '& > *': {
        margin: theme.spacing(1),
      },
    },
  }),
);