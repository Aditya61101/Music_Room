import React, { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";
import { Home } from "./components/Home";
import { CreateRoom } from "./components/CreateRoom";
import { JoinRoom } from "./components/JoinRoom";
import { Room } from "./components/Room";
import Info from "./components/Info";

const App = () => {
  const [roomCode, setRoomCode] = useState(null);
  const userInRoom = async () => {
    try {
      const response = await fetch("/api/user-in-room");
      if (response.ok) {
        const data = await response.json();
        console.log(data);
        if (data.code) {
          setRoomCode(data.code);
        }
      } else {
        throw new Error("Something went wrong!");
      }
    } catch (error) {
      alert(error.message);
    }
  };
  const clearRoomCode = () => {
    setRoomCode(null);
  };
  useEffect(() => {
    userInRoom();
  }, []);
  return (
    <Router>
      <Switch>
        <Route
          exact
          path="/"
          render={() =>
            roomCode ? <Redirect to={`/room/${roomCode}`} /> : <Home />
          }
        />
        <Route path="/join" component={JoinRoom} />
        <Route path="/info" component={Info} />
        <Route path="/create" component={CreateRoom} />
        <Route
          path="/room/:roomCode"
          render={(props) => {
            return <Room {...props} leaveRoomCallback={clearRoomCode} />;
          }}
        />
      </Switch>
    </Router>
  );
};
export default App;
