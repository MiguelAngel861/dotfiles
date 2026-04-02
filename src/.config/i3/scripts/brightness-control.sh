#!/usr/bin/env bash

STEP=5      # porcentaje de cambio
MIN=1       # evita apagar completamente la pantalla
MAX=100

direction="$1"

get_brightness() {
    # brightnessctl devuelve valores absolutos, no porcentaje directo
    current=$(brightnessctl get)
    max=$(brightnessctl max)

    echo $(( current * 100 / max ))
}

set_brightness() {
    brightnessctl set "$1%"
}

case "$direction" in
    up)
        current=$(get_brightness)
        target=$((current + STEP))
        [ "$target" -gt "$MAX" ] && target="$MAX"

        set_brightness "$target"
        ;;
    down)
        current=$(get_brightness)
        target=$((current - STEP))
        [ "$target" -lt "$MIN" ] && target="$MIN"

        set_brightness "$target"
        ;;
    *)
        echo "Uso: $0 {up|down}"
        exit 1
        ;;
esac
