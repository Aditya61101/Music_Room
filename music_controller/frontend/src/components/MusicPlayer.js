import React from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  LinearProgress,
} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import PauseIcon from "@material-ui/icons/Pause";
import SkipNextIcon from "@material-ui/icons/SkipNext";

export const MusicPlayer = (props) => {
  const songProgress = (props.song.time / props.song.duration) * 100;
  const playPauseSong = async () => {
    const requestOptions = {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
    };
    const url = props.is_playing ? "/spotify/play" : "/spotify/pause";
    const response = await fetch(url, requestOptions);
    console.log(response);
  };
  const skipSong = async () => {
    const requestOptions = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    };
    const response = await fetch("/spotify/skip", requestOptions);
    console.log(response);
  };
  return (
    <Card>
      <Grid container alignItems="center">
        <Grid item align="center" xs={4}>
          <img
            src={props.song.img_url}
            alt="Album Cover"
            height="100%"
            width="100%"
          />
        </Grid>
        <Grid item align="center" xs={8}>
          <Typography component="h5" variant="h5">
            {props.song.title}
          </Typography>
          <Typography color="textSecondary" variant="subtitle1">
            {props.song.artist}
            <div>
              <IconButton onClick={playPauseSong}>
                {props.song.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
              </IconButton>
              <IconButton onClick={skipSong}>
                <SkipNextIcon />{" "} {props.song.votes}/ {props.song.votes_required}
              </IconButton>
            </div>
          </Typography>
        </Grid>
      </Grid>
      <LinearProgress variant="determinate" value={songProgress} />
    </Card>
  );
};
