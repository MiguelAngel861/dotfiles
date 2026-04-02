#!/usr/bin/env python3
import i3ipc
import sys
import time
import subprocess

def get_monitor_resolution(conn, window):
    outputs = conn.get_outputs()
    for output in outputs:
        if output.name == window.ipc_data['output']:
            return output.rect.width, output.rect.height
    return 1920, 1080

def force_resize_x11(window_id, width, height, x=None, y=None):
    """Fuerza el tamaño usando wmctrl/xdotool ignorando restricciones del programa"""
    # Obtener ID de ventana en formato hex
    win_id_hex = hex(window_id)
    
    # Primero intentar con wmctrl
    try:
        if x is not None and y is not None:
            subprocess.run(['wmctrl', '-i', '-r', str(window_id), '-e', f'0,{x},{y},{width},{height}'], 
                         check=False, capture_output=True)
        else:
            subprocess.run(['wmctrl', '-i', '-r', str(window_id), '-e', f'0,-1,-1,{width},{height}'], 
                         check=False, capture_output=True)
    except FileNotFoundError:
        pass
    
    # Refuerzo con xdotool si está disponible
    try:
        subprocess.run(['xdotool', 'windowsize', str(window_id), str(width), str(height)], 
                     check=False, capture_output=True)
        if x is not None and y is not None:
            subprocess.run(['xdotool', 'windowmove', str(window_id), str(x), str(y)], 
                         check=False, capture_output=True)
    except FileNotFoundError:
        pass

def main():
    if len(sys.argv) != 3:
        print("Uso: resize_focused.py <ancho_%> <alto_%>")
        sys.exit(1)

    width_pct = int(sys.argv[1])
    height_pct = int(sys.argv[2])

    conn = i3ipc.Connection()
    
    # Espera inicial para que la ventana exista
    time.sleep(0.2)
    
    tree = conn.get_tree()
    focused = tree.find_focused()
    
    if not focused:
        print("No hay ventana enfocada")
        sys.exit(1)
    
    # Guardar ID de ventana antes de cualquier operación
    window_id = focused.window
    
    mon_w, mon_h = get_monitor_resolution(conn, focused)
    
    new_w = int(mon_w * width_pct / 100)
    new_h = int(mon_h * height_pct / 100)
    
    # Calcular posición centrada
    pos_x = (mon_w - new_w) // 2
    pos_y = (mon_h - new_h) // 2
    
    print(f"Intentando redimensionar a {new_w}x{new_h} en posición {pos_x},{pos_y}")
    print(f"Window ID: {window_id} ({hex(window_id)})")
    
    # Paso 1: Hacer flotante con i3
    focused.command('floating enable')
    time.sleep(0.1)
    
    # Paso 2: Forzar tamaño con X11 (ignora restricciones del programa)
    force_resize_x11(window_id, new_w, new_h, pos_x, pos_y)
    time.sleep(0.1)
    
    # Paso 3: Re-intentar con i3 por si acaso
    focused.command(f'resize set {new_w} {new_h}')
    focused.command(f'move position {pos_x} {pos_y}')
    
    print(f"Redimensionado forzado a {new_w}x{new_h}")

if __name__ == '__main__':
    main()