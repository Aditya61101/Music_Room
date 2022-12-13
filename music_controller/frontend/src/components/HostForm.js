import React, { useState } from "react";
import {
  Button,
  Grid,
  Typography,
  TextField,
  FormHelperText,
  FormControl,
  Radio,
  RadioGroup,
  FormControlLabel,
  Collapse,
} from "@material-ui/core";
import { Alert } from "@material-ui/lab";
import { Link, useHistory } from "react-router-dom";

export const HostRoom = (props) => {
  let pauseVal = props.update ? props.guestCanPause.toString() : "true";
  const history = useHistory();
  const defaultVotes = 2;
  const [guestCanPause, setGuestCanPause] = useState(true);
  const [votesToSkip, setVotesToSkip] = useState(defaultVotes);
  const [message, setMessage] = useState("");

  const handleChangePause = (e) => {
    if (e.target.value == "true") {
      setGuestCanPause(true);
    } else {
      setGuestCanPause(false);
    }
  };
  const handleRoom = async () => {
    let requestBody;
    if (props.update) {
      requestBody = {
        votes_to_skip: votesToSkip,
        guest_can_pause: guestCanPause,
        code: props.roomCode,
      };
    } else {
      requestBody = {
        votes_to_skip: votesToSkip,
        guest_can_pause: guestCanPause,
      };
    }
    const requestOptions = {
      method: props.update ? "PATCH" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    };
    try {
      let url;
      if (props.update) {
        url = "/api/update-room";
      } else {
        url = "/api/create-room";
      }
      const response = await fetch(url, requestOptions);
      const data = await response.json();
      console.log(response);
      console.log(data);
      if (response.ok) {
        if (!props.update) {
          history.push(`/room/${data.code}`);
        }
        setMessage("Room Updated Successfully");
      } else {
        setMessage("Something went wrong:(");
      }
    } catch (error) {
      console.log(error.message);
    }
  };
  return (
    <Grid container spacing={1}>
      <Grid item xs={12} align="center">
        <Collapse in={message}>
          <Alert
            severity="success"
            onClose={() => {
              setMessage("");
            }}
          >
            {message}
          </Alert>
        </Collapse>
      </Grid>
      <Grid item xs={12} align="center">
        <Typography component={"h4"} variant="h4">
          {props.update ? "Update the Room" : "Create a Room"}
        </Typography>
      </Grid>
      <Grid item xs={12} align="center">
        <FormControl component={"fieldset"}>
          <FormHelperText>
            <div align="center">Guest control of Playback state</div>
          </FormHelperText>
          <RadioGroup row defaultValue={pauseVal} onChange={handleChangePause}>
            <FormControlLabel
              value="true"
              control={<Radio color="primary" />}
              label="Play/Pause"
              labelPlacement="bottom"
            />
            <FormControlLabel
              value="false"
              control={<Radio color="secondary" />}
              label="No control"
              labelPlacement="bottom"
            />
          </RadioGroup>
        </FormControl>
      </Grid>
      <Grid item xs={12} align="center">
        <FormControl>
          <TextField
            required={true}
            type="number"
            defaultValue={props.update ? props.votesToSkip : defaultVotes}
            inputProps={{
              min: 1,
              style: { textAlign: "center" },
            }}
            onChange={(e) => {
              setVotesToSkip(e.target.value);
            }}
          />
          <FormHelperText>
            <div align="center">Votes Required to Skip the current song!</div>
          </FormHelperText>
        </FormControl>
      </Grid>
      <Grid item xs={12} align="center">
        <Button color="primary" variant="contained" onClick={handleRoom}>
          {props.update ? "Update the Room" : "Create a Room"}
        </Button>
      </Grid>
      {!props.update && (
        <Grid item xs={12} align="center">
          <Button color="secondary" variant="contained" to="/" component={Link}>
            Back
          </Button>
        </Grid>
      )}
    </Grid>
  );
};
