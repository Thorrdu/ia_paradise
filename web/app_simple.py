#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serveur web simplifié pour l'interface utilisateur de Paradis IA
"""

import os
import sys
import json
import random
import logging
import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/web_server.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("web_simple")

# Chemin absolu du répertoire web
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    # Importer les modules nécessaires
    from flask import Flask, jsonify, request, render_template
except ImportError as e:
    logger.error(f"Impossible d'importer les modules nécessaires: {e}")
    logger.error("Le serveur web ne peut pas démarrer")
    sys.exit(1)

# Initialisation de l'application Flask
app = Flask(__name__, 
           static_folder=os.path.join(WEB_DIR, "static"),
           template_folder=os.path.join(WEB_DIR, "templates"))

# Routes
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

# Point d'entrée principal
if __name__ == '__main__':
    logger.info("Serveur web simplifié démarré")
    # Le serveur sera accessible à l'adresse http://localhost:5000
    app.run(host='0.0.0.0', port=5000, debug=True)