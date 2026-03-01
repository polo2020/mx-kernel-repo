#!/usr/bin/env python3
"""
Generador de imagen de tema para ShieldLinux
Crea un fondo cybersecurity estilo matrix/shield
"""

import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    import random
    import math
except ImportError:
    print("Instalando Pillow...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont

def create_cybersecurity_theme(width=1920, height=1080):
    """Crear imagen de tema cybersecurity"""
    
    # Crear imagen base oscura
    img = Image.new('RGB', (width, height), color='#0a0a14')
    draw = ImageDraw.Draw(img)
    
    # Gradiente de fondo
    for y in range(height):
        r = int(10 + 5 * math.sin(y / 100))
        g = int(10 + 8 * math.sin(y / 150))
        b = int(20 + 10 * math.sin(y / 80))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Efecto matrix - caracteres cayendo
    matrix_chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    columns = width // 20
    
    for col in range(columns):
        x = col * 20
        # Caracteres matrix
        for i in range(random.randint(5, 20)):
            y = random.randint(0, height)
            char = random.choice(matrix_chars)
            # Color verde matrix con variaciones
            green = random.randint(100, 255)
            alpha = random.randint(50, 200)
            color = (0, green, random.randint(50, 150))
            
            try:
                # Intentar usar fuente pequeña
                draw.text((x, y), char, fill=color)
            except:
                draw.rectangle([x, y, x+10, y+15], fill=color)
    
    # Escudo central (forma geométrica)
    center_x, center_y = width // 2, height // 2
    
    # Escudo exterior
    shield_points = [
        (center_x, center_y - 150),  # Top
        (center_x + 120, center_y - 80),  # Top right
        (center_x + 120, center_y + 50),  # Right
        (center_x, center_y + 120),  # Bottom
        (center_x - 120, center_y + 50),  # Left
        (center_x - 120, center_y - 80),  # Top left
    ]
    
    # Dibujar escudo con gradiente
    for i, point in enumerate(shield_points):
        next_point = shield_points[(i + 1) % len(shield_points)]
        draw.line([point, next_point], fill=(0, 255, 136), width=3)
    
    # Líneas de conexión internas
    for i in range(len(shield_points)):
        for j in range(i + 1, len(shield_points)):
            if abs(i - j) != 1 and abs(i - j) != len(shield_points) - 1:
                draw.line([shield_points[i], shield_points[j]], 
                         fill=(0, 100, 50), width=1)
    
    # Círculos concéntricos
    for r in range(50, 200, 30):
        draw.ellipse([
            center_x - r, center_y - r,
            center_x + r, center_y + r
        ], outline=(0, 80, 40), width=1)
    
    # Texto SHIELD
    try:
        font_size = 48
        draw.text((center_x - 150, center_y + 180), 
                 "SHIELD LINUX", 
                 fill=(0, 255, 136))
    except:
        pass
    
    # Puntos de conexión (nodos)
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.ellipse([x-2, y-2, x+2, y+2], fill=(0, 255, 136))
    
    # Guardar imagen
    output_path = "/home/jean/Música/seguridad/tema.jpg"
    img.save(output_path, "JPEG", quality=90)
    print(f"✓ Imagen creada: {output_path}")
    print(f"  Tamaño: {width}x{height}")
    return output_path

if __name__ == "__main__":
    create_cybersecurity_theme()
