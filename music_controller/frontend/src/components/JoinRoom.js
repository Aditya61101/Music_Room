import React, { useState } from "react";
import { TextField, Button, Grid, Typography } from "@material-ui/core";
import { Link, useHistory } from "react-router-dom";

export const JoinRoom = () => {
  const history = useHistory();
  const [roomCode, setRoomCode] = useState("");
  const [error, setError] = useState("");
  const handleEnterRoom = async () => {
    console.log(roomCode);
    try {
      const response = await fetch("/api/join-room", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: roomCode,
        }),
      });
      const data = await response.json();
      console.log(data);
      if (response.status === 200) {
        history.push(`/room/${roomCode}`);
      } else {
        throw new Error(data.message);
      }
    } catch (error) {
      setError(error.message);
      setRoomCode("");
    }
  };
  const handleChangeCode = (e) => {
    setRoomCode(e.target.value);
  };
  return (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Typography variant="h4" component="h4">
          Join a Room
        </Typography>
      </Grid>
      <Grid item xs={12} align="center">
        <TextField
          error={error}
          label="Code"
          placeholder="Enter a Room code"
          value={roomCode}
          helperText={error}
          variant="outlined"
          onChange={handleChangeCode}
        />
      </Grid>
      <Grid item xs={12} align="center">
        <Button variant="contained" color="primary" onClick={handleEnterRoom}>
          Enter Room
        </Button>
      </Grid>
      <Grid item xs={12} align="center">
        <Button variant="contained" color="secondary" to="/" component={Link}>
          Back
        </Button>
      </Grid>
    </Grid>
  );
};
