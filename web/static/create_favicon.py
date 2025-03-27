#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour créer un favicon pour l'interface web Paradis IA.
Utilise la bibliothèque Pillow (PIL).
"""

import os
from PIL import Image, ImageDraw

def create_favicon(output_path, size=(32, 32), main_color=(74, 107, 255), bg_color=(255, 255, 255, 0)):
    """
    Crée un favicon simple pour l'interface web.
    
    Args:
        output_path (str): Chemin de sortie pour le favicon
        size (tuple): Dimensions du favicon (par défaut 32x32)
        main_color (tuple): Couleur principale (RGB)
        bg_color (tuple): Couleur de fond (RGBA, transparent par défaut)
    
    Returns:
        bool: True si la création a réussi, False sinon
    """
    try:
        # Créer une image avec fond transparent
        img = Image.new('RGBA', size, bg_color)
        draw = ImageDraw.Draw(img)
        
        # Dimensions
        width, height = size
        center_x, center_y = width // 2, height // 2
        
        # Dessiner un cercle de fond avec contour
        outer_radius = min(width, height) // 2 - 1
        draw.ellipse(
            [(center_x - outer_radius, center_y - outer_radius), 
             (center_x + outer_radius, center_y + outer_radius)],
            fill=(main_color[0], main_color[1], main_color[2], 80),  # Semi-transparent
            outline=main_color
        )
        
        # Dessiner le cercle central
        inner_radius = outer_radius // 2
        draw.ellipse(
            [(center_x - inner_radius, center_y - inner_radius), 
             (center_x + inner_radius, center_y + inner_radius)],
            fill=main_color
        )
        
        # Dessiner trois petits points en orbite
        orbit_radius = (outer_radius + inner_radius) // 2
        for angle in [30, 150, 270]:
            import math
            radian = math.radians(angle)
            x = center_x + int(orbit_radius * math.cos(radian))
            y = center_y + int(orbit_radius * math.sin(radian))
            
            dot_size = max(2, min(width, height) // 10)
            draw.ellipse(
                [(x - dot_size, y - dot_size), (x + dot_size, y + dot_size)],
                fill=(255, 255, 255)
            )
        
        # Enregistrer l'image en tant que favicon.ico
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Pour le format ICO, nous devons d'abord enregistrer en PNG puis convertir
        png_path = output_path.replace('.ico', '.png')
        img.save(png_path)
        
        # Convertir le PNG en ICO
        img = Image.open(png_path)
        img.save(output_path)
        
        # Supprimer le fichier PNG temporaire
        if os.path.exists(png_path) and png_path != output_path:
            os.remove(png_path)
        
        print(f"Favicon créé et enregistré dans : {output_path}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la création du favicon: {e}")
        return False

if __name__ == "__main__":
    # Chemin de sortie pour le favicon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "favicon.ico")
    
    # Couleur principale de Paradis IA
    main_color = (74, 107, 255)  # Bleu primaire
    
    # Créer le favicon
    success = create_favicon(
        output_path, 
        size=(32, 32), 
        main_color=main_color
    )
    
    if success:
        print("Favicon généré avec succès!")
    else:
        print("Erreur lors de la création du favicon") 