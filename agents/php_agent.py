"""
Agent spécialisé pour le développement PHP
Fournit des capacités spécifiques pour la création, le débogage et l'amélioration de code PHP
"""

import os
import re
import json
import subprocess
from typing import Dict, List, Any, Optional, Union

from agents.base_agent import BaseAgent
from api.communication import Priority, TaskStatus

class PHPDevAgent(BaseAgent):
    """
    Agent spécialisé dans le développement PHP
    
    Capacités:
    - Analyse et création de code PHP
    - Débogage d'applications PHP
    - Documentation de code PHP
    - Optimisation de code PHP
    - Sécurisation d'applications PHP
    """
    
    def __init__(
        self,
        name: str = "PHPDevAgent",
        model_name: str = "deepseek-coder",  # Modèle optimisé pour le code
        **kwargs
    ):
        super().__init__(
            name=name,
            model_name=model_name,
            **kwargs
        )
        
        # Base de connaissances PHP spécifique
        self.php_error_patterns = {
            "undefined_variable": r"Undefined variable: (\w+)",
            "undefined_function": r"Call to undefined function (\w+)",
            "syntax_error": r"syntax error, unexpected '(\w+)'",
            "missing_semicolon": r"syntax error, unexpected",
            "class_not_found": r"Class '(\w+)' not found",
            "fatal_error": r"Fatal error: (.+)"
        }
        
        # Initialiser la base de connaissances avec des exemples PHP courants
        self._initialize_php_knowledge()
    
    def _get_default_system_prompt(self) -> str:
        """Message système spécifique pour l'agent PHP"""
        return (
            f"Tu es {self.name}, un agent IA spécialisé dans le développement PHP. "
            f"Tu excelles dans l'analyse, la création, le débogage et l'optimisation de code PHP. "
            f"Tu connais les bonnes pratiques PHP, les frameworks populaires et les motifs de conception. "
            f"Réponds avec des explications concises et du code précis. "
            f"Pour les extraits de code, utilise la syntaxe de PHP 8.0+ et respecte les PSR (PHP Standards Recommendations). "
            f"Quand tu analyses des logs d'erreur, sois méthodique et propose des solutions claires."
        )
    
    def _get_default_capabilities(self) -> List[str]:
        """Capacités spécifiques pour l'agent PHP"""
        return [
            "php_development", 
            "code_analysis", 
            "debugging", 
            "optimization", 
            "security_review",
            "php_framework_knowledge",
            "documentation"
        ]
    
    def _initialize_php_knowledge(self) -> None:
        """Initialise la base de connaissances avec des informations PHP essentielles"""
        try:
            # Exemples de motifs d'erreurs PHP courants
            self._safe_add_knowledge(
                content="Les erreurs 'Undefined variable' en PHP se produisent quand on essaie d'utiliser une variable qui n'a pas été déclarée ou initialisée.",
                metadata={"type": "error_pattern", "category": "undefined_variable"}
            )
            
            self._safe_add_knowledge(
                content="Les erreurs 'Class not found' indiquent généralement un problème avec l'autoloader, un namespace incorrect ou un fichier manquant.",
                metadata={"type": "error_pattern", "category": "class_not_found"}
            )
            
            # Bonnes pratiques PHP
            self._safe_add_knowledge(
                content="PHP PSR-12: Les accolades de classe doivent être sur la ligne suivante, et les accolades de méthode et fonction doivent être sur la même ligne que la déclaration.",
                metadata={"type": "best_practice", "category": "coding_style"}
            )
            
            self._safe_add_knowledge(
                content="Validation des entrées: Toujours filtrer et valider les entrées utilisateur avec filter_var ou des bibliothèques de validation pour éviter les injections.",
                metadata={"type": "best_practice", "category": "security"}
            )
            
            # Frameworks PHP populaires
            self._safe_add_knowledge(
                content="Laravel est un framework PHP MVC moderne avec une syntaxe élégante et des fonctionnalités comme Eloquent ORM, Blade, etc.",
                metadata={"type": "framework", "category": "laravel"}
            )
            
            self._safe_add_knowledge(
                content="Symfony est un framework PHP modulaire et composants réutilisables, souvent utilisé pour des applications d'entreprise.",
                metadata={"type": "framework", "category": "symfony"}
            )
            
            self.logger.info("Base de connaissances PHP initialisée avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de la base de connaissances PHP: {e}")
    
    def _safe_add_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Ajoute une connaissance PHP en gérant les erreurs d'embedding
        
        Args:
            content: Contenu de la connaissance
            metadata: Métadonnées associées
            
        Returns:
            Index du document ajouté ou -1 en cas d'erreur
        """
        try:
            # Essayer d'obtenir un embedding (peut échouer si le modèle n'est pas disponible)
            embedding = None
            if self.llm:
                try:
                    embedding_result = self.llm.embedding(content)
                    if embedding_result and "embedding" in embedding_result:
                        embedding = embedding_result["embedding"]
                except Exception as e:
                    self.logger.warning(f"Impossible de générer l'embedding pour la connaissance PHP: {e}")
            
            # Utiliser la méthode safe_add du stockage vectoriel
            if hasattr(self.vector_store, "safe_add"):
                return self.vector_store.safe_add(content, embedding, metadata)
            else:
                # Fallback si safe_add n'existe pas (utiliser la méthode normale avec un embedding vide)
                if embedding is None:
                    embedding = [0.0]  # Embedding factice
                return self.vector_store.add(content, embedding, metadata)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de connaissance PHP: {e}")
            return -1
    
    def _process_message(self, message_data: Dict[str, Any]) -> None:
        """
        Traite un message reçu en utilisant l'expertise PHP
        
        Args:
            message_data: Données du message à traiter
        """
        try:
            sender = message_data.get("sender", "")
            content = message_data.get("content", "")
            
            # Vérifier s'il s'agit d'un message concernant du code PHP
            php_related = self._is_php_related(content)
            
            # Définir le prompt en fonction du type de contenu
            if self._contains_error_log(content):
                prompt = self._create_error_analysis_prompt(content)
                task_type = "analyse d'erreur PHP"
            elif self._contains_code(content):
                prompt = self._create_code_review_prompt(content)
                task_type = "revue de code PHP"
            else:
                prompt = self._create_general_php_prompt(content)
                task_type = "assistance PHP générale"
            
            # Générer une réponse
            self.logger.info(f"Génération d'une réponse pour une tâche de {task_type}")
            response = self.llm.generate(prompt)
            
            # Extraire et envoyer la réponse
            response_text = response.get("response", "")
            
            self.send_message(
                recipient=sender,
                content=response_text,
                priority=message_data.get("priority", Priority.MEDIUM.value)
            )
            
            self.logger.info(f"Réponse PHP envoyée à {sender}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message PHP: {e}")
            self.send_message(
                recipient=message_data.get("sender", ""),
                content=f"Désolé, je n'ai pas pu traiter votre demande PHP en raison d'une erreur: {str(e)}",
                priority=Priority.HIGH.value
            )
    
    def _process_task(self, task_data: Dict[str, Any]) -> None:
        """
        Traite une tâche PHP assignée
        
        Args:
            task_data: Données de la tâche à traiter
        """
        try:
            task_id = task_data.get("task_id", "")
            description = task_data.get("description", "")
            created_by = task_data.get("created_by", "")
            
            # Analyser le type de tâche PHP
            if "debug" in description.lower() or "erreur" in description.lower():
                task_type = "débogage"
                prompt = self._create_debugging_task_prompt(description)
            elif "optimis" in description.lower():
                task_type = "optimisation"
                prompt = self._create_optimization_task_prompt(description) 
            elif "sécuri" in description.lower():
                task_type = "sécurité"
                prompt = self._create_security_task_prompt(description)
            else:
                task_type = "développement"
                prompt = self._create_development_task_prompt(description)
            
            # Générer une solution
            self.logger.info(f"Travail sur une tâche PHP de {task_type}")
            response = self.llm.generate(prompt)
            
            # Extraire la réponse
            solution = response.get("response", "")
            
            # Envoyer la solution
            self.send_message(
                recipient=created_by,
                content=f"J'ai terminé la tâche PHP ({task_type}) #{task_id}.\n\n{solution}",
                priority=task_data.get("priority", Priority.MEDIUM.value),
                metadata={"task_id": task_id, "task_type": task_type}
            )
            
            # Marquer la tâche comme terminée
            self.comm_manager.update_task_status(task_id, TaskStatus.COMPLETED)
            
            self.logger.info(f"Tâche PHP {task_id} complétée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la tâche PHP: {e}")
            try:
                # Informer le créateur et marquer la tâche comme échouée
                self.send_message(
                    recipient=task_data.get("created_by", ""),
                    content=f"Je n'ai pas pu terminer la tâche PHP #{task_id} en raison d'une erreur: {str(e)}",
                    priority=Priority.HIGH.value,
                    metadata={"task_id": task_id}
                )
                self.comm_manager.update_task_status(task_id, TaskStatus.FAILED)
            except:
                pass
    
    def _is_php_related(self, content: str) -> bool:
        """Vérifie si le contenu est lié à PHP"""
        php_keywords = ["php", "laravel", "symfony", "composer", "psr", "wordpress", "drupal"]
        return any(keyword in content.lower() for keyword in php_keywords)
    
    def _contains_error_log(self, content: str) -> bool:
        """Vérifie si le contenu contient des logs d'erreur PHP"""
        error_patterns = [
            r"PHP (Warning|Notice|Fatal error|Parse error)",
            r"Exception|Error in",
            r"Stack trace",
            r"Call to undefined"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in error_patterns)
    
    def _contains_code(self, content: str) -> bool:
        """Vérifie si le contenu contient du code PHP"""
        code_patterns = [
            r"<\?php",
            r"function\s+\w+\s*\(",
            r"class\s+\w+",
            r"namespace\s+\w+",
            r"use\s+\w+\\",
            r"\$\w+\s*=",
            r"->|::"
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in code_patterns)
    
    def _create_error_analysis_prompt(self, content: str) -> str:
        """Crée un prompt pour l'analyse d'erreurs PHP"""
        return (
            f"Tu es un expert en débogage PHP. Analyse ce log d'erreur et propose une solution:\n\n"
            f"{content}\n\n"
            f"1. Identifie clairement l'erreur et sa cause probable\n"
            f"2. Propose une ou plusieurs solutions concrètes avec du code si nécessaire\n"
            f"3. Explique comment éviter ce type d'erreur à l'avenir\n"
            f"Sois précis et concis dans ton analyse."
        )
    
    def _create_code_review_prompt(self, content: str) -> str:
        """Crée un prompt pour la revue de code PHP"""
        return (
            f"Tu es un expert en développement PHP. Procède à une revue de code complète:\n\n"
            f"{content}\n\n"
            f"Dans ta revue, couvre ces aspects:\n"
            f"1. Problèmes potentiels ou bugs\n"
            f"2. Améliorations de la lisibilité et du style (conformité PSR)\n"
            f"3. Optimisations de performance\n"
            f"4. Problèmes de sécurité\n"
            f"5. Conseils pour améliorer la maintenabilité\n\n"
            f"Pour chaque point, propose du code corrigé si nécessaire. Sois précis mais concis."
        )
    
    def _create_general_php_prompt(self, content: str) -> str:
        """Crée un prompt pour une question PHP générale"""
        return (
            f"Tu es un expert en développement PHP. Réponds à cette question ou demande:\n\n"
            f"{content}\n\n"
            f"Fournis une réponse précise et pratique, avec des exemples de code si nécessaire. "
            f"Si la demande n'est pas claire, demande des précisions."
        )
    
    def _create_debugging_task_prompt(self, description: str) -> str:
        """Crée un prompt pour une tâche de débogage PHP"""
        return (
            f"Tu es un expert en débogage PHP. On t'a assigné cette tâche de débogage:\n\n"
            f"{description}\n\n"
            f"Développe une analyse complète qui:\n"
            f"1. Identifie les causes possibles du problème\n"
            f"2. Propose des méthodes de diagnostic et des outils\n"
            f"3. Suggère des solutions concrètes avec du code\n"
            f"4. Explique comment prévenir ce type de problème\n\n"
            f"Sois méthodique et précis dans ton analyse."
        )
    
    def _create_development_task_prompt(self, description: str) -> str:
        """Crée un prompt pour une tâche de développement PHP"""
        return (
            f"Tu es un expert en développement PHP. On t'a assigné cette tâche de développement:\n\n"
            f"{description}\n\n"
            f"Développe une solution complète qui:\n"
            f"1. Explique l'approche choisie et l'architecture\n"
            f"2. Fournit le code nécessaire, bien structuré et commenté\n"
            f"3. Suit les bonnes pratiques PHP modernes et les PSR\n"
            f"4. Inclut des considérations sur la testabilité et la maintenabilité\n\n"
            f"Le code doit être propre, efficace et bien documenté."
        )
    
    def _create_optimization_task_prompt(self, description: str) -> str:
        """Crée un prompt pour une tâche d'optimisation PHP"""
        return (
            f"Tu es un expert en optimisation PHP. On t'a assigné cette tâche d'optimisation:\n\n"
            f"{description}\n\n"
            f"Développe une stratégie d'optimisation qui:\n"
            f"1. Identifie les goulots d'étranglement potentiels\n"
            f"2. Propose des optimisations de code, de requêtes ou de configuration\n"
            f"3. Compare les approches possibles (bénéfices/inconvénients)\n"
            f"4. Inclut des exemples de code optimisé\n"
            f"5. Suggère des outils de profilage pour mesurer les améliorations\n\n"
            f"Concentre-toi sur des optimisations qui apportent un gain significatif."
        )
    
    def _create_security_task_prompt(self, description: str) -> str:
        """Crée un prompt pour une tâche de sécurité PHP"""
        return (
            f"Tu es un expert en sécurité PHP. On t'a assigné cette tâche de sécurité:\n\n"
            f"{description}\n\n"
            f"Développe une analyse de sécurité qui:\n"
            f"1. Identifie les vulnérabilités potentielles (OWASP Top 10)\n"
            f"2. Analyse le risque et l'impact de chaque problème\n"
            f"3. Propose des corrections concrètes avec du code\n"
            f"4. Suggère des mesures préventives et bonnes pratiques\n"
            f"5. Recommande des outils ou bibliothèques de sécurité pertinents\n\n"
            f"Sois particulièrement attentif aux injections, XSS, CSRF et autres vulnérabilités courantes."
        )
    
    def analyze_php_error(self, error_log: str) -> Dict[str, Any]:
        """
        Analyse un log d'erreur PHP et propose des solutions
        
        Args:
            error_log: Le log d'erreur à analyser
            
        Returns:
            Dictionnaire contenant l'analyse et les solutions proposées
        """
        try:
            prompt = self._create_error_analysis_prompt(error_log)
            response = self.llm.generate(prompt)
            
            # Structurer la réponse
            analysis = {
                "error_identified": True,
                "error_type": self._identify_error_type(error_log),
                "analysis": response.get("response", ""),
                "source": error_log
            }
            
            # Enregistrer cette analyse pour référence future
            self._safe_add_knowledge(
                content=f"Analyse d'erreur: {error_log}\n\nSolution: {analysis['analysis']}",
                metadata={"type": "error_analysis", "error_type": analysis["error_type"]}
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de l'erreur PHP: {e}")
            return {
                "error_identified": False,
                "error_type": "unknown",
                "analysis": f"Erreur lors de l'analyse: {str(e)}",
                "source": error_log
            }
    
    def _identify_error_type(self, error_log: str) -> str:
        """Identifie le type d'erreur PHP"""
        for error_type, pattern in self.php_error_patterns.items():
            if re.search(pattern, error_log, re.IGNORECASE):
                return error_type
        
        if "warning" in error_log.lower():
            return "warning"
        elif "notice" in error_log.lower():
            return "notice"
        elif "deprecated" in error_log.lower():
            return "deprecated"
        elif "parse error" in error_log.lower():
            return "syntax_error"
        else:
            return "unknown"
    
    def optimize_php_code(self, code: str) -> Dict[str, Any]:
        """
        Optimise du code PHP
        
        Args:
            code: Le code PHP à optimiser
            
        Returns:
            Dictionnaire contenant le code optimisé et les explications
        """
        try:
            prompt = (
                f"Tu es un expert en optimisation PHP. Optimise ce code PHP en te concentrant "
                f"sur la performance, la lisibilité et les bonnes pratiques modernes:\n\n"
                f"{code}\n\n"
                f"Fournis:\n"
                f"1. Le code optimisé complet\n"
                f"2. Une liste d'optimisations réalisées\n"
                f"3. L'impact estimé de chaque optimisation\n\n"
                f"Respecte la fonctionnalité d'origine tout en améliorant le code."
            )
            
            response = self.llm.generate(prompt)
            
            # Extraire le code optimisé de la réponse (approximatif)
            optimized_code = self._extract_code_blocks(response.get("response", ""))
            
            result = {
                "original_code": code,
                "optimized_code": optimized_code,
                "explanation": response.get("response", ""),
                "success": len(optimized_code) > 0
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'optimisation du code PHP: {e}")
            return {
                "original_code": code,
                "optimized_code": "",
                "explanation": f"Erreur lors de l'optimisation: {str(e)}",
                "success": False
            }
    
    def _extract_code_blocks(self, text: str) -> str:
        """Extrait les blocs de code d'un texte"""
        # Recherche les blocs de code entre ```php et ```
        matches = re.findall(r"```(?:php)?\s*([\s\S]*?)```", text)
        
        if matches:
            return "\n\n".join(matches)
        
        # Si pas de bloc de code formaté, essayer de trouver du code par heuristique
        if "<?php" in text:
            # Trouver la première occurrence de <?php et tout ce qui suit
            match = re.search(r"<\?php[\s\S]*", text)
            if match:
                return match.group(0)
        
        return ""
    
    def get_framework_knowledge(self, framework: str) -> str:
        """
        Récupère des connaissances sur un framework PHP spécifique
        
        Args:
            framework: Le nom du framework (laravel, symfony, etc.)
            
        Returns:
            Informations sur le framework demandé
        """
        try:
            # Rechercher dans la base de connaissances
            results = []
            for doc_idx, doc in enumerate(self.vector_store.documents):
                if framework.lower() in doc.lower():
                    metadata = self.vector_store.metadata[doc_idx]
                    if metadata.get("type") == "framework":
                        results.append(doc)
            
            # Si des résultats ont été trouvés dans la base de connaissances
            if results:
                return "\n\n".join(results)
            
            # Sinon, demander au modèle
            prompt = f"Décris le framework PHP {framework}, ses caractéristiques principales, avantages et cas d'utilisation typiques."
            response = self.llm.generate(prompt)
            
            # Enregistrer cette connaissance pour la prochaine fois
            knowledge = response.get("response", "")
            self._safe_add_knowledge(
                content=knowledge,
                metadata={"type": "framework", "category": framework.lower()}
            )
            
            return knowledge
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des connaissances sur {framework}: {e}")
            return f"Désolé, je n'ai pas pu récupérer d'informations sur {framework} en raison d'une erreur." 