#!/usr/bin/env bash

# -------------------------------------------------
# Polybar launch script
# -------------------------------------------------

# Termina instancias previas de polybar
killall -q polybar

# Espera hasta que polybar haya muerto completamente
while pgrep -u "$UID" -x polybar >/dev/null; do
    sleep 0.2
done

# Detecta monitores usando xrandr
if command -v xrandr >/dev/null; then
    for monitor in $(xrandr --query | grep " connected" | cut -d" " -f1); do
        MONITOR=$monitor polybar main &
    done
else
    polybar main &
fi

exit 0

