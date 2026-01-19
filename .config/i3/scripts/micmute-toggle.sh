#!/usr/bin/env bash

SOURCE="@DEFAULT_SOURCE@"
LED="platform::micmute"

pactl set-source-mute "$SOURCE" toggle
sleep 0.3

if pactl get-source-mute "$SOURCE" | grep -q "yes"; then
    brightnessctl -d "$LED" set 1
else
    brightnessctl -d "$LED" set 0
fi