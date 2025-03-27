#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour convertir le logo SVG en PNG.
Dépendances : cairosvg
Installation : pip install cairosvg
"""

import os
import sys
import cairosvg

def convert_svg_to_png(svg_path, png_path, width=None, height=None):
    """Convertit un fichier SVG en PNG."""
    try:
        # Vérifier que le fichier SVG existe
        if not os.path.exists(svg_path):
            print(f"Erreur: Le fichier {svg_path} n'existe pas.")
            return False
        
        # Créer le répertoire de destination si nécessaire
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        
        # Conversion avec cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, parent_width=width, parent_height=height)
        
        print(f"Conversion réussie: {svg_path} -> {png_path}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la conversion: {e}")
        return False

if __name__ == "__main__":
    # Chemins relatifs par rapport au script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(script_dir, "logo.svg")
    png_path = os.path.join(script_dir, "logo.png")
    
    # Taille du PNG de sortie
    width = 200
    height = 200
    
    # Effectuer la conversion
    if not convert_svg_to_png(svg_path, png_path, width, height):
        sys.exit(1)
    
    print("Logo PNG généré avec succès!")
    sys.exit(0) 