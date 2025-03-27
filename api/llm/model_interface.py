"""
Interface standardisée pour les modèles de langage
Compatible avec Ollama et d'autres fournisseurs de LLM
"""

import os
import json
import subprocess
import requests
from typing import Dict, List, Optional, Union, Any

class ModelConfig:
    """Configuration pour les modèles LLM"""
    def __init__(
        self,
        model_name: str,
        provider: str = "ollama",
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        context_window: int = 4096,
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.model_name = model_name
        self.provider = provider.lower()
        self.api_base = api_base or self._get_default_api_base(provider)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.system_prompt = system_prompt
        self.api_key = api_key or os.environ.get(f"{provider.upper()}_API_KEY")
    
    def _get_default_api_base(self, provider: str) -> str:
        """Récupère l'URL de base par défaut pour un fournisseur"""
        provider_bases = {
            "ollama": "http://localhost:11434",
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com",
            "mistral": "https://api.mistral.ai/v1"
        }
        return provider_bases.get(provider.lower(), "")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "api_base": self.api_base,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_window": self.context_window,
            "system_prompt": self.system_prompt
        }

class ModelInterface:
    """Interface générique pour interagir avec différents modèles LLM"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self._validate_configuration()
        
    def _validate_configuration(self):
        """Vérifie que la configuration est valide"""
        if not self.config.model_name:
            raise ValueError("Le nom du modèle doit être spécifié")
        
        if self.config.provider not in ["ollama", "openai", "anthropic", "mistral"]:
            raise ValueError(f"Fournisseur non pris en charge: {self.config.provider}")
        
        if not self.config.api_base:
            raise ValueError(f"Base API non spécifiée pour {self.config.provider}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Génère une réponse à partir d'un prompt en utilisant le modèle configuré
        
        Args:
            prompt: Le texte d'entrée pour le modèle
            system_prompt: Message système optionnel (remplace celui de la config)
            temperature: Température optionnelle (remplace celle de la config)
            max_tokens: Nombre maximal de tokens (remplace celui de la config)
            stop_sequences: Séquences de stop optionnelles
            stream: Si True, la réponse sera streamée
            
        Returns:
            Dictionnaire contenant la réponse du modèle
        """
        if self.config.provider == "ollama":
            return self._generate_ollama(
                prompt=prompt,
                system_prompt=system_prompt or self.config.system_prompt,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                stop_sequences=stop_sequences,
                stream=stream
            )
        
        elif self.config.provider == "openai":
            return self._generate_openai(
                prompt=prompt,
                system_prompt=system_prompt or self.config.system_prompt,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
                stop_sequences=stop_sequences,
                stream=stream
            )
        
        else:
            raise NotImplementedError(f"Génération pour {self.config.provider} pas encore implémentée")
    
    def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[List[str]],
        stream: bool
    ) -> Dict[str, Any]:
        """Génère une réponse en utilisant Ollama"""
        
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": stream
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if stop_sequences:
            payload["stop"] = stop_sequences
        
        try:
            response = requests.post(
                f"{self.config.api_base}/api/generate",
                json=payload,
                stream=stream
            )
            
            if stream:
                # Traitement du stream
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        full_response += chunk.get("response", "")
                        if chunk.get("done", False):
                            break
                
                return {
                    "response": full_response,
                    "model": self.config.model_name,
                    "provider": "ollama"
                }
            else:
                # Traitement de la réponse complète
                response_json = response.json()
                return {
                    "response": response_json.get("response", ""),
                    "model": self.config.model_name,
                    "provider": "ollama"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "response": "",
                "model": self.config.model_name,
                "provider": "ollama"
            }
    
    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
        stop_sequences: Optional[List[str]],
        stream: bool
    ) -> Dict[str, Any]:
        """Génère une réponse en utilisant l'API OpenAI"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        if stop_sequences:
            payload["stop"] = stop_sequences
            
        try:
            response = requests.post(
                f"{self.config.api_base}/chat/completions",
                headers=headers,
                json=payload,
                stream=stream
            )
            
            if stream:
                # Traitement du stream
                full_response = ""
                for line in response.iter_lines():
                    if line and line.strip() != b'':
                        if line.startswith(b'data: '):
                            line = line[6:]  # Enlever le préfixe 'data: '
                        if line.strip() == b'[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                content = chunk['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    full_response += content
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "response": full_response,
                    "model": self.config.model_name,
                    "provider": "openai"
                }
            else:
                # Traitement de la réponse complète
                response_json = response.json()
                return {
                    "response": response_json.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "model": self.config.model_name,
                    "provider": "openai"
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "response": "",
                "model": self.config.model_name,
                "provider": "openai"
            }

    def embedding(self, text: str) -> List[float]:
        """
        Génère un embedding pour le texte donné
        
        Args:
            text: Le texte à encoder
            
        Returns:
            Liste de valeurs représentant l'embedding
        """
        if self.config.provider == "ollama":
            return self._embedding_ollama(text)
        else:
            raise NotImplementedError(f"Embedding pour {self.config.provider} pas encore implémenté")
    
    def _embedding_ollama(self, text: str) -> List[float]:
        """Génère un embedding en utilisant Ollama"""
        try:
            response = requests.post(
                f"{self.config.api_base}/api/embeddings",
                json={
                    "model": self.config.model_name,
                    "prompt": text
                }
            )
            
            response_json = response.json()
            return response_json.get("embedding", [])
            
        except Exception as e:
            print(f"Erreur lors de la génération de l'embedding: {e}")
            return []

# Fonction utilitaire pour créer facilement une interface de modèle
def create_model_interface(
    model_name: str,
    provider: str = "ollama",
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> ModelInterface:
    """
    Crée une interface de modèle avec des paramètres simplifiés
    
    Args:
        model_name: Nom du modèle
        provider: Fournisseur du modèle (ollama, openai, etc.)
        temperature: Température pour la génération
        system_prompt: Message système par défaut
        
    Returns:
        Instance de ModelInterface configurée
    """
    config = ModelConfig(
        model_name=model_name,
        provider=provider,
        temperature=temperature,
        system_prompt=system_prompt
    )
    
    return ModelInterface(config) 