import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import "./index.css";

// pages
import {StartPage, NotFound, GameRoom} from "./pages"

export const App = () => {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={StartPage}/>
        <Route path="/room/:roomId" component={GameRoom}/>
        <Route component={NotFound} />
      </Switch>
    </Router>
  );
}
