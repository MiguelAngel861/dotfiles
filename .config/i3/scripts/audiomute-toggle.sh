#!/usr/bin/env bash

SINK="@DEFAULT_SINK@"
LED="platform::mute"

if [ "$1" = "toggle" ]; then
    pactl set-sink-mute "$SINK" toggle
elif [ "$1" = "off" ]; then
    pactl set-sink-mute "$SINK" 0
fi

sleep 0.3

if pactl get-sink-mute "$SINK" | grep -q "yes"; then
    brightnessctl -d "$LED" set 1
else
    brightnessctl -d "$LED" set 0
fi
