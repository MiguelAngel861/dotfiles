#!/usr/bin/env python3
import i3ipc
import re
import sys
import time
import subprocess


def find_window_by_mark(conn, mark):
    pattern = f'^{re.escape(mark)}$'
    for con in conn.get_tree().find_marked(pattern):
        if con.window is not None:
            return con
    return None

def get_monitor_resolution(conn, window):
    outputs = conn.get_outputs()
    for output in outputs:
        if output.name == window.ipc_data['output']:
            return output.rect.width, output.rect.height
    return 1920, 1080

def force_resize_x11(window_id, width, height, x=None, y=None):
    """Fuerza el tamaño usando wmctrl ignorando restricciones del programa"""
    wmctrl_id = hex(window_id)

    # Primero intentar con wmctrl; si funciona, evitamos lanzar xdotool.
    try:
        wmctrl_args = ['wmctrl', '-i', '-r', wmctrl_id, '-e']
        if x is not None and y is not None:
            wmctrl_args.append(f'0,{x},{y},{width},{height}')
        else:
            wmctrl_args.append(f'0,-1,-1,{width},{height}')

        wmctrl_result = subprocess.run(
            wmctrl_args,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if wmctrl_result.returncode == 0:
            return
    except FileNotFoundError:
        pass

def main():
    if len(sys.argv) not in (3, 4):
        print("Uso: resize-window.py <ancho_%> <alto_%> [marca_i3]")
        sys.exit(1)

    width_pct = int(sys.argv[1])
    height_pct = int(sys.argv[2])
    target_mark = sys.argv[3] if len(sys.argv) == 4 else None

    conn = i3ipc.Connection()

    target_window = None

    if target_mark:
        # Usar la marca directamente para evitar depender de la ventana enfocada.
        target_window = find_window_by_mark(conn, target_mark)

        # Pequeño reintento por si el árbol aún no reflejó el mark.
        if not target_window:
            time.sleep(0.02)
            target_window = find_window_by_mark(conn, target_mark)
    else:
        target_window = conn.get_tree().find_focused()

    if not target_window:
        if target_mark:
            print(f"No se encontró ventana con mark '{target_mark}'")
        else:
            print("No hay ventana enfocada")
        sys.exit(1)

    if not target_window.window:
        print("La ventana objetivo no tiene ID X11")
        sys.exit(1)

    # Guardar ID de ventana antes de cualquier operación
    window_id = target_window.window

    mon_w, mon_h = get_monitor_resolution(conn, target_window)
    
    new_w = int(mon_w * width_pct / 100)
    new_h = int(mon_h * height_pct / 100)
    
    # Calcular posición centrada
    pos_x = (mon_w - new_w) // 2
    pos_y = (mon_h - new_h) // 2
    
    print(f"Intentando redimensionar a {new_w}x{new_h} en posición {pos_x},{pos_y}")
    print(f"Window ID: {window_id} ({hex(window_id)})")

    # Paso 1: Hacer flotante con i3 y dejar el tamaño/posición como respaldo.
    commands = [
        'floating enable',
        f'resize set {new_w} {new_h}',
        f'move position {pos_x} {pos_y}',
    ]
    if target_mark:
        commands.append(f'unmark {target_mark}')

    target_window.command('; '.join(commands))

    # Paso 2: Forzar tamaño con X11 (ignora restricciones del programa)
    force_resize_x11(window_id, new_w, new_h, pos_x, pos_y)

    print(f"Redimensionado forzado a {new_w}x{new_h}")

if __name__ == '__main__':
    main()