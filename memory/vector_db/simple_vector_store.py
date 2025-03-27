"""
Une implémentation simple de stockage vectoriel qui fonctionne sans dépendances externes
Utilise un fichier JSON pour stocker les données et calcule les similarités en mémoire
"""

import os
import json
import math
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import pickle

# Configuration du logging
logger = logging.getLogger("simple_vector_store")

class SimpleVectorStore:
    """
    Un stockage vectoriel simple qui stocke les embeddings en mémoire et sur disque
    Permet la recherche par similarité de cosinus
    """
    
    def __init__(self, store_name: str, directory: str = "./memory/data"):
        """
        Initialise le stockage vectoriel
        
        Args:
            store_name: Nom du stockage (utilisé pour nommer le fichier)
            directory: Répertoire où stocker les données
        """
        self.store_name = store_name
        self.directory = directory
        self.data_file = os.path.join(directory, f"{store_name}.json")
        self.vectors_file = os.path.join(directory, f"{store_name}_vectors.pkl")
        self.documents = []  # Liste des documents
        self.vectors = []    # Liste des vecteurs correspondants
        self.metadata = []   # Liste des métadonnées
        
        # Créer le répertoire s'il n'existe pas
        os.makedirs(directory, exist_ok=True)
        
        # Charger les données existantes
        self._load()
    
    def _load(self):
        """Charge les données depuis le disque"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
            
            if os.path.exists(self.vectors_file):
                with open(self.vectors_file, 'rb') as f:
                    self.vectors = pickle.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            # Initialiser avec des listes vides en cas d'erreur
            self.documents = []
            self.vectors = []
            self.metadata = []
    
    def _save(self):
        """Sauvegarde les données sur le disque"""
        try:
            # Sauvegarder documents et métadonnées en JSON
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'documents': self.documents,
                    'metadata': self.metadata
                }, f, ensure_ascii=False, indent=2)
            
            # Sauvegarder les vecteurs en pickle (plus efficace pour les données numériques)
            with open(self.vectors_file, 'wb') as f:
                pickle.dump(self.vectors, f)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données: {e}")
    
    def add(self, document: str, embedding: List[float], metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Ajoute un document avec son embedding au stockage
        
        Args:
            document: Texte du document
            embedding: Vecteur d'embedding du document
            metadata: Métadonnées additionnelles (optionnel)
            
        Returns:
            Index du document ajouté
        """
        self.documents.append(document)
        self.vectors.append(embedding)
        self.metadata.append(metadata or {})
        
        # Sauvegarder les changements
        self._save()
        
        return len(self.documents) - 1
    
    def safe_add(self, document: str, embedding: Optional[List[float]] = None, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Ajoute un document au stockage de manière sécurisée, en gérant le cas où l'embedding est None
        
        Args:
            document: Texte du document
            embedding: Vecteur d'embedding du document (peut être None)
            metadata: Métadonnées additionnelles (optionnel)
            
        Returns:
            Index du document ajouté ou -1 en cas d'erreur
        """
        try:
            # Si l'embedding est None, utiliser un vecteur vide (ne sera pas retrouvable par recherche)
            if embedding is None:
                logger.warning(f"Ajout du document sans embedding: '{document[:50]}...'")
                embedding = [0.0]  # Vecteur vide qui ne sera pas retrouvable
            
            # Ajouter le document
            return self.add(document, embedding, metadata)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du document: {e}")
            return -1
    
    def add_batch(
        self, 
        documents: List[str], 
        embeddings: List[List[float]], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """
        Ajoute un lot de documents avec leurs embeddings
        
        Args:
            documents: Liste des textes
            embeddings: Liste des vecteurs d'embedding
            metadatas: Liste des métadonnées (optionnel)
            
        Returns:
            Liste des indices des documents ajoutés
        """
        if len(documents) != len(embeddings):
            raise ValueError("Le nombre de documents et d'embeddings doit être identique")
        
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]
        elif len(metadatas) != len(documents):
            raise ValueError("Le nombre de documents et de métadonnées doit être identique")
        
        start_idx = len(self.documents)
        self.documents.extend(documents)
        self.vectors.extend(embeddings)
        self.metadata.extend(metadatas)
        
        # Sauvegarder les changements
        self._save()
        
        return list(range(start_idx, start_idx + len(documents)))
    
    def safe_add_batch(
        self, 
        documents: List[str], 
        embeddings: Optional[List[List[float]]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[int]:
        """
        Ajoute un lot de documents de manière sécurisée, en gérant le cas où certains embeddings sont None
        
        Args:
            documents: Liste des textes
            embeddings: Liste des vecteurs d'embedding (peut être None)
            metadatas: Liste des métadonnées (optionnel)
            
        Returns:
            Liste des indices des documents ajoutés
        """
        try:
            # Si embeddings est None, créer une liste de vecteurs vides
            if embeddings is None:
                logger.warning("Ajout d'un lot de documents sans embeddings")
                embeddings = [[0.0] for _ in range(len(documents))]
            
            # Si certains embeddings individuels sont None, les remplacer par des vecteurs vides
            for i in range(len(embeddings)):
                if embeddings[i] is None:
                    logger.warning(f"Un embedding est None pour le document: '{documents[i][:50]}...'")
                    embeddings[i] = [0.0]
            
            # Ajouter le lot
            return self.add_batch(documents, embeddings, metadatas)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du lot de documents: {e}")
            return []
    
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche les documents les plus similaires au vecteur de requête
        
        Args:
            query_embedding: Vecteur d'embedding de la requête
            top_k: Nombre de résultats à retourner
            score_threshold: Seuil minimal de score (entre 0 et 1)
            
        Returns:
            Liste des résultats, chacun contenant document, score et métadonnées
        """
        if not self.vectors:
            return []
        
        # Calculer les similarités de cosinus
        scores = [self._cosine_similarity(query_embedding, doc_vec) for doc_vec in self.vectors]
        
        # Créer des tuples (indice, score)
        scored_indices = [(i, score) for i, score in enumerate(scores)]
        
        # Filtrer par seuil si nécessaire
        if score_threshold is not None:
            scored_indices = [(i, score) for i, score in scored_indices if score >= score_threshold]
        
        # Trier par score décroissant
        scored_indices.sort(key=lambda x: x[1], reverse=True)
        
        # Limiter au top-k
        scored_indices = scored_indices[:top_k]
        
        # Préparer les résultats
        results = []
        for idx, score in scored_indices:
            results.append({
                'document': self.documents[idx],
                'score': score,
                'metadata': self.metadata[idx],
                'id': idx
            })
        
        return results
    
    def safe_search(
        self, 
        query_embedding: Optional[List[float]] = None, 
        top_k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche sécurisée qui gère le cas où l'embedding de requête est None
        
        Args:
            query_embedding: Vecteur d'embedding de la requête (peut être None)
            top_k: Nombre de résultats à retourner
            score_threshold: Seuil minimal de score (entre 0 et 1)
            
        Returns:
            Liste des résultats ou liste vide en cas d'erreur
        """
        try:
            if query_embedding is None:
                logger.warning("Tentative de recherche avec un embedding None")
                return []
            
            return self.search(query_embedding, top_k, score_threshold)
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcule la similarité de cosinus entre deux vecteurs
        
        Args:
            vec1: Premier vecteur
            vec2: Deuxième vecteur
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if len(vec1) != len(vec2):
            raise ValueError("Les vecteurs doivent avoir la même dimension")
        
        # Produit scalaire
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        # Éviter la division par zéro
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def delete(self, idx: int) -> bool:
        """
        Supprime un document par son indice
        
        Args:
            idx: Indice du document à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        if 0 <= idx < len(self.documents):
            self.documents.pop(idx)
            self.vectors.pop(idx)
            self.metadata.pop(idx)
            
            # Sauvegarder les changements
            self._save()
            
            return True
        return False
    
    def clear(self) -> None:
        """Efface toutes les données du stockage"""
        self.documents = []
        self.vectors = []
        self.metadata = []
        
        # Sauvegarder les changements
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur le stockage
        
        Returns:
            Dictionnaire de statistiques
        """
        return {
            'name': self.store_name,
            'count': len(self.documents),
            'size_on_disk': os.path.getsize(self.data_file) + os.path.getsize(self.vectors_file) if all(
                os.path.exists(f) for f in [self.data_file, self.vectors_file]
            ) else 0,
            'last_modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                os.path.getmtime(self.data_file) if os.path.exists(self.data_file) else time.time()
            ))
        } 