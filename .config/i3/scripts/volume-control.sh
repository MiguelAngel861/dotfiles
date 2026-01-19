#!/usr/bin/env bash

SINK="@DEFAULT_SINK@"
STEP=5
MAX=100

direction="$1"
MUTE_SCRIPT="$HOME/.config/i3/scripts/audiomute-toggle.sh"

get_volume() {
    pactl get-sink-volume "$SINK" \
        | grep -o '[0-9]\+%' \
        | head -n1 \
        | tr -d '%'
}

case "$direction" in
    up)
        "$MUTE_SCRIPT" off

        current=$(get_volume)
        target=$((current + STEP))
        [ "$target" -gt "$MAX" ] && target="$MAX"

        pactl set-sink-volume "$SINK" "${target}%"
        ;;
    down)
        "$MUTE_SCRIPT" off

        current=$(get_volume)
        target=$((current - STEP))
        [ "$target" -lt 0 ] && target=0

        pactl set-sink-volume "$SINK" "${target}%"
        ;;
esac
