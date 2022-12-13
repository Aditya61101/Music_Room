import React, { useState, useEffect } from "react";
import { Button, Grid, Typography } from "@material-ui/core";
import { useHistory } from "react-router-dom";
import { HostRoom } from "./HostForm";
import { MusicPlayer } from "./MusicPlayer";

export const Room = (props) => {
  const history = useHistory();
  console.log(props.match.params);
  const roomCode = props.match.params.roomCode;
  console.log(roomCode);
  const [guestCanPause, setGuestCanPause] = useState(true);
  const [isHost, setIsHost] = useState(false);
  const [votesToSkip, setVotesToSkip] = useState(2);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [spotifyAuth, setSpotifyAuth] = useState(false);
  const [song, setSong] = useState({});

  const getCurrentSong = async () => {
    const res = await fetch("/spotify/curr-song");
    if (res.status===200) {
      const data = await res.json();
      setSong(data);
    } else {
      console.log(res);
    }
  };
  const authSpotify = async () => {
    const response = await fetch("/spotify/check-auth");
    const data = await response.json();
    setSpotifyAuth(data.isAuth);
    if (!data.isAuth) {
      const res = await fetch("/spotify/get-auth");
      const dat = await res.json();
      // this will redirect to authentication url of spotify
      window.location.replace(dat.url);
    }
  };
  const getRoomDetails = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/get-room?code=${roomCode}`);
      if (response.status === 200) {
        const data = await response.json();
        setVotesToSkip(data.votes_to_skip);
        setGuestCanPause(data.guest_can_pause);
        setIsHost(data.is_host);
        setIsLoading(false);
        if (data.is_host) {
          authSpotify();
        }
      } else {
        props.leaveRoomCallback();
        history.push("/");
        throw new Error(
          "Room is closed by the creator, please click on OK to go to the homepage :("
        );
      }
    } catch (error) {
      alert(error.message);
    }
  };
  useEffect(() => {
    getRoomDetails();
    const interval = setInterval(() => {
      getCurrentSong();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleLeaveRoom = async () => {
    try {
      const response = await fetch("/api/leave-room", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await response.json();
      console.log(data);
      if (response.ok) {
        props.leaveRoomCallback();
        history.push("/");
      } else {
        throw new Error("Something went wrong!");
      }
    } catch (error) {
      alert(error.message);
    }
  };
  const handleBack = () => {
    getRoomDetails();
    setShowSettings(false);
  };
  let content = null;
  if (isLoading) {
    content = <p>Loading....</p>;
  } else if (!isLoading && !showSettings) {
    content = (
      <>
        <Grid container spacing={1}>
          <Grid item xs={12} align="center">
            <Typography variant="h4" component="h4">
              Code: {roomCode}
            </Typography>
          </Grid>
          <Grid item xs={12} align="center">
            <MusicPlayer song={song}/>
          </Grid>
          {/* <Grid item xs={12} align="center">
            <Typography variant="h6" component="h6">
              Votes To Skip: {votesToSkip}
            </Typography>
          </Grid>
          <Grid item xs={12} align="center">
            <Typography variant="h6" component="h6">
              Guest Can Pause: {guestCanPause.toString()}
            </Typography>
          </Grid>
          <Grid item xs={12} align="center">
            <Typography variant="h6" component="h6">
              Are you the Host? : {isHost.toString()}
            </Typography>
          </Grid> */}
          <Grid item xs={12} align="center" spacing={4}>
            {isHost && (
              <Button
                variant="contained"
                color="primary"
                onClick={() => {
                  setShowSettings(true);
                }}
              >
                Settings
              </Button>
            )}
            <Button
              variant="contained"
              color="secondary"
              onClick={handleLeaveRoom}
            >
              Leave Room
            </Button>
          </Grid>
        </Grid>
      </>
    );
  } else if (!isLoading && showSettings) {
    content = (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <HostRoom
            update={true}
            votesToSkip={votesToSkip}
            guestCanPause={guestCanPause}
            roomCode={roomCode}
            updateCallback={getRoomDetails}
          />
        </Grid>
        <Grid item xs={12} align="center">
          <Button color="secondary" variant="contained" onClick={handleBack}>
            Back
          </Button>
        </Grid>
      </Grid>
    );
  }
  return content;
};
