#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script alternatif pour créer un logo PNG simple sans dépendance à Cairo.
Utilise uniquement la bibliothèque Pillow (PIL).
"""

import os
from PIL import Image, ImageDraw

def create_simple_logo(output_path, size=(200, 200), bg_color=(255, 255, 255), 
                       main_color=(74, 107, 255), accent_colors=None):
    """
    Crée un logo simple directement en PNG sans conversion à partir de SVG.
    """
    if accent_colors is None:
        accent_colors = [
            (40, 167, 69),   # vert
            (23, 162, 184),   # bleu
            (220, 53, 69)     # rouge
        ]
    
    # Créer une image avec fond blanc
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Dimensions
    width, height = size
    center_x, center_y = width // 2, height // 2
    
    # Dessiner un cercle de fond
    draw.ellipse(
        [(center_x - 90, center_y - 90), (center_x + 90, center_y + 90)],
        fill=(main_color[0], main_color[1], main_color[2], 25)  # Couleur principale avec transparence
    )
    
    # Dessiner deux ellipses (orbites)
    for angle in [30, 150]:
        draw.arc(
            [(center_x - 80, center_y - 30), (center_x + 80, center_y + 30)],
            start=0, end=360, fill=main_color, width=2
        )
    
    # Dessiner le nœud central
    draw.ellipse(
        [(center_x - 20, center_y - 20), (center_x + 20, center_y + 20)],
        fill=main_color
    )
    
    # Dessiner les nœuds satellites
    satellite_positions = [
        (center_x + 60, center_y),      # droite
        (center_x - 30, center_y + 60),  # bas gauche
        (center_x - 40, center_y - 50)   # haut gauche
    ]
    
    for i, (x, y) in enumerate(satellite_positions):
        color = accent_colors[i % len(accent_colors)]
        draw.ellipse([(x - 10, y - 10), (x + 10, y + 10)], fill=color)
        
        # Ligne de connexion au centre
        draw.line([(center_x, center_y), (x, y)], fill=main_color, width=2)
    
    # Enregistrer l'image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Logo créé et enregistré dans : {output_path}")
    return True

if __name__ == "__main__":
    # Chemin de sortie pour le logo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "logo.png")
    
    # Couleurs de Paradis IA
    main_color = (74, 107, 255)  # Bleu primaire
    accent_colors = [
        (40, 167, 69),  # Vert
        (23, 162, 184),  # Bleu ciel
        (220, 53, 69)   # Rouge
    ]
    
    # Créer le logo
    success = create_simple_logo(
        output_path, 
        size=(200, 200), 
        bg_color=(255, 255, 255, 0),  # Transparent
        main_color=main_color,
        accent_colors=accent_colors
    )
    
    if success:
        print("Logo PNG généré avec succès!")
    else:
        print("Erreur lors de la création du logo") 