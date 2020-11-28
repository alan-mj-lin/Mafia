import React from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { QueryCache, ReactQueryCacheProvider } from 'react-query';
import './index.css';

// pages
import { StartPage, NotFound, GameRoom } from './pages';

const queryCache = new QueryCache();

export const App = () => {
  return (
    <ReactQueryCacheProvider queryCache={queryCache}>
      <Router>
        <Switch>
          <Route exact path="/" component={StartPage} />
          <Route path="/room/:roomId" component={GameRoom} />
          <Route component={NotFound} />
        </Switch>
      </Router>
    </ReactQueryCacheProvider>
  );
};
