#!/usr/bin/env bash

# ============================================
# launch.sh - Polybar launcher con Autorandr
# ============================================

# Termina instancias previas de polybar
killall -q polybar 2>/dev/null

# Esperar a que terminen
while pgrep -u "$UID" -x polybar >/dev/null; do 
    sleep 0.2
done

# ============================================
# DETECCIÓN DE MONITORES
# ============================================

# Guardar salida de xrandr una sola vez
XRANDR_OUTPUT=$(xrandr --query)

# Obtener monitores conectados
mapfile -t connected < <(awk '/ connected/{print $1}' <<< "$XRANDR_OUTPUT")
count=${#connected[@]}

# Si no hay monitores, salir
if (( count == 0 )); then
    echo "Error: No se detectaron monitores" >&2
    exit 1
fi

# ============================================
# FUNCIÓN: Lanzar polybar en un monitor
# ============================================
launch_polybar() {
    local monitor=$1
    local bar_name=${2:-main}
    
    echo "Lanzando polybar '$bar_name' en monitor: $monitor"
    MONITOR="$monitor" polybar "$bar_name" --reload &
}

# ============================================
# CASO 1: Solo un monitor
# ============================================
if (( count == 1 )); then
    launch_polybar "${connected[0]}" "main"
    exit 0
fi

# ============================================
# CASO 2: Múltiples monitores - Detectar modo
# ============================================

# Obtener posiciones de cada monitor (formato: +X+Y)
positions=()
for m in "${connected[@]}"; do
    # Extraer la posición absoluta (ej: +1920+0)
    pos=$(awk -v mon="$m" '
        $1 == mon {
            # Buscar el patrón +num+num que indica posición absoluta
            if (match($0, /\+[0-9]+\+[0-9]+/)) {
                print substr($0, RSTART, RLENGTH)
            }
        }
    ' <<< "$XRANDR_OUTPUT")
    positions+=("$pos")
done

# Contar posiciones únicas
unique_positions=$(printf "%s\n" "${positions[@]}" | sort -u | grep -c '^+')

# ============================================
# DETECCIÓN: Espejo vs Extendido
# ============================================

if (( unique_positions < count )); then
    # ========================================
    # MODO ESPEJO (monitores comparten posición)
    # ========================================
    
    echo "Modo detectado: ESPEJO"
    
    # Buscar el monitor primario
    primary=$(awk '/ connected primary/{print $1; exit}' <<< "$XRANDR_OUTPUT")
    
    # Si no hay primario definido, usar el primero de la lista
    [[ -z "$primary" ]] && primary="${connected[0]}"
    
    # En modo espejo, solo lanzar una barra en el monitor primario
    launch_polybar "$primary" "main"
    
else
    # ========================================
    # MODO EXTENDIDO (posiciones diferentes)
    # ========================================
    
    echo "Modo detectado: EXTENDIDO"
    
    # Lanzar barra en cada monitor conectado
    for m in "${connected[@]}"; do
        launch_polybar "$m" "main"
    done
    
fi

echo "Polybar lanzado correctamente en $count monitor(es)"
