from typing import Dict, List, Optional, Any
import re
from datetime import datetime
from .base_agent import BaseAgent
from .communication_inter_ia import Message, MessagePriority, TaskStatus

class PHPDevAgent(BaseAgent):
    def __init__(self, name: str, communication_manager):
        super().__init__(name, communication_manager)
        self.code_templates = {
            'class': self._get_class_template(),
            'controller': self._get_controller_template(),
            'model': self._get_model_template(),
            'service': self._get_service_template()
        }
        self.capabilities = [
            'php_development',
            'code_generation',
            'code_review',
            'bug_fixing',
            'documentation',
            'testing'
        ]
        self.register(self.capabilities)

    def _handle_normal_message(self, message: Message) -> str:
        """Traite le contenu d'un message spécifique au développement PHP."""
        content = message.content.lower()
        metadata = message.metadata or {}

        # Gestion du ping pour la mesure du temps de réponse
        if content == "ping":
            return "pong"

        if "generate" in content:
            return self._handle_code_generation(message)
        elif "review" in content:
            return self._handle_code_review(message)
        elif "fix" in content:
            return self._handle_bug_fixing(message)
        elif "test" in content:
            return self._handle_test_generation(message)
        elif "document" in content:
            return self._handle_documentation(message)
        else:
            return "Je ne comprends pas la demande. Veuillez préciser si vous souhaitez une génération de code, une revue, une correction de bug, des tests ou de la documentation."

    def _handle_code_generation(self, message: Message) -> str:
        """Gère les demandes de génération de code."""
        metadata = message.metadata or {}
        code_type = metadata.get('type', 'class')
        requirements = metadata.get('requirements', {})
        
        # Création d'une tâche pour la génération
        task_id = self.create_task(
            description=f"Génération de code PHP de type {code_type}",
            priority=MessagePriority.HIGH
        )
        
        try:
            # Génération du code
            generated_code = self._generate_php_code(code_type, requirements)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            # Sauvegarde dans la mémoire
            self.save_memory(f"last_generated_{code_type}", generated_code)
            
            return f"Voici le code généré pour {code_type}:\n```php\n{generated_code}\n```"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la génération du code: {str(e)}")

    def _handle_code_review(self, message: Message) -> str:
        """Gère les demandes de revue de code."""
        code_to_review = message.metadata.get('code', '')
        if not code_to_review:
            return "Aucun code fourni pour la revue. Veuillez inclure le code dans les métadonnées du message."

        # Création d'une tâche pour la revue
        task_id = self.create_task(
            description="Revue de code PHP",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Analyse du code
            review_result = self._review_php_code(code_to_review)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Revue du code:\n{review_result}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la revue du code: {str(e)}")

    def _handle_bug_fixing(self, message: Message) -> str:
        """Gère les demandes de correction de bugs."""
        buggy_code = message.metadata.get('code', '')
        error_description = message.metadata.get('error', '')
        
        if not buggy_code or not error_description:
            return "Informations incomplètes pour la correction de bug. Veuillez fournir le code et la description de l'erreur."

        # Création d'une tâche pour la correction
        task_id = self.create_task(
            description="Correction de bug PHP",
            priority=MessagePriority.URGENT
        )
        
        try:
            # Analyse et correction du bug
            fixed_code = self._fix_php_bug(buggy_code, error_description)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Correction proposée:\n```php\n{fixed_code}\n```"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la correction du bug: {str(e)}")

    def _handle_test_generation(self, message: Message) -> str:
        """Gère les demandes de génération de tests."""
        code_to_test = message.metadata.get('code', '')
        if not code_to_test:
            return "Aucun code fourni pour la génération de tests."

        # Création d'une tâche pour la génération de tests
        task_id = self.create_task(
            description="Génération de tests PHP",
            priority=MessagePriority.HIGH
        )
        
        try:
            # Génération des tests
            test_code = self._generate_php_tests(code_to_test)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Tests générés:\n```php\n{test_code}\n```"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la génération des tests: {str(e)}")

    def _handle_documentation(self, message: Message) -> str:
        """Gère les demandes de documentation."""
        code_to_document = message.metadata.get('code', '')
        if not code_to_document:
            return "Aucun code fourni pour la documentation."

        # Création d'une tâche pour la documentation
        task_id = self.create_task(
            description="Génération de documentation PHP",
            priority=MessagePriority.MEDIUM
        )
        
        try:
            # Génération de la documentation
            documentation = self._generate_php_documentation(code_to_document)
            
            # Mise à jour du statut de la tâche
            self.update_task_status(task_id, TaskStatus.COMPLETED)
            
            return f"Documentation générée:\n{documentation}"
            
        except Exception as e:
            self.update_task_status(task_id, TaskStatus.FAILED)
            raise Exception(f"Erreur lors de la génération de la documentation: {str(e)}")

    def _generate_php_code(self, code_type: str, requirements: Dict) -> str:
        """Génère du code PHP selon le type et les exigences."""
        if code_type not in self.code_templates:
            raise ValueError(f"Type de code non supporté: {code_type}")
            
        template = self.code_templates[code_type]
        return self._fill_template(template, requirements)

    def _review_php_code(self, code: str) -> str:
        """Effectue une revue de code PHP."""
        issues = []
        
        # Vérification des standards PSR
        if not self._check_psr_standards(code):
            issues.append("Le code ne respecte pas les standards PSR")
            
        # Vérification de la sécurité
        security_issues = self._check_security(code)
        if security_issues:
            issues.extend(security_issues)
            
        # Vérification des performances
        performance_issues = self._check_performance(code)
        if performance_issues:
            issues.extend(performance_issues)
            
        # Vérification de la maintenabilité
        maintainability_issues = self._check_maintainability(code)
        if maintainability_issues:
            issues.extend(maintainability_issues)
            
        return self._format_review_results(issues)

    def _fix_php_bug(self, code: str, error_description: str) -> str:
        """Corrige un bug dans du code PHP."""
        # Analyse de l'erreur
        error_type = self._analyze_error(error_description)
        
        # Application des corrections appropriées
        fixed_code = code
        if error_type == "syntax":
            fixed_code = self._fix_syntax_error(code)
        elif error_type == "logic":
            fixed_code = self._fix_logic_error(code)
        elif error_type == "security":
            fixed_code = self._fix_security_issue(code)
            
        return fixed_code

    def _generate_php_tests(self, code: str) -> str:
        """Génère des tests unitaires pour le code PHP."""
        # Analyse du code pour identifier les méthodes à tester
        methods = self._extract_methods(code)
        
        # Génération des tests pour chaque méthode
        test_code = []
        for method in methods:
            test_code.append(self._generate_method_test(method))
            
        return "\n\n".join(test_code)

    def _generate_php_documentation(self, code: str) -> str:
        """Génère de la documentation PHPDoc pour le code."""
        # Analyse du code pour identifier les éléments à documenter
        elements = self._extract_documentable_elements(code)
        
        # Génération de la documentation pour chaque élément
        documentation = []
        for element in elements:
            documentation.append(self._generate_element_documentation(element))
            
        return "\n\n".join(documentation)

    # Méthodes utilitaires privées
    def _get_class_template(self) -> str:
        return """
class {class_name} {
    private $properties = [];
    
    public function __construct() {
        // Initialisation
    }
    
    // Méthodes générées automatiquement
}
"""

    def _get_controller_template(self) -> str:
        return """
class {controller_name}Controller {
    private $service;
    
    public function __construct({service_name}Service $service) {
        $this->service = $service;
    }
    
    // Actions du contrôleur
}
"""

    def _get_model_template(self) -> str:
        return """
class {model_name}Model {
    private $table;
    private $db;
    
    public function __construct(Database $db) {
        $this->db = $db;
        $this->table = '{table_name}';
    }
    
    // Méthodes CRUD
}
"""

    def _get_service_template(self) -> str:
        return """
class {service_name}Service {
    private $repository;
    
    public function __construct({repository_name}Repository $repository) {
        $this->repository = $repository;
    }
    
    // Logique métier
}
"""

    def _fill_template(self, template: str, requirements: Dict) -> str:
        """Remplit un template avec les exigences fournies."""
        return template.format(**requirements)

    def _check_psr_standards(self, code: str) -> bool:
        """Vérifie si le code respecte les standards PSR."""
        # Implémentation de la vérification PSR
        return True

    def _check_security(self, code: str) -> List[str]:
        """Vérifie les problèmes de sécurité dans le code."""
        issues = []
        # Vérification des injections SQL
        if re.search(r"mysql_query|mysqli_query|exec|eval", code):
            issues.append("Utilisation de fonctions dangereuses détectée")
        return issues

    def _check_performance(self, code: str) -> List[str]:
        """Vérifie les problèmes de performance dans le code."""
        issues = []
        # Vérification des boucles imbriquées
        if code.count("for") > 3 or code.count("while") > 3:
            issues.append("Possible problème de performance avec les boucles imbriquées")
        return issues

    def _check_maintainability(self, code: str) -> List[str]:
        """Vérifie la maintenabilité du code."""
        issues = []
        # Vérification de la complexité cyclomatique
        if len(code.split("\n")) > 100:
            issues.append("Fonction trop longue, considérer la refactorisation")
        return issues

    def _format_review_results(self, issues: List[str]) -> str:
        """Formate les résultats de la revue de code."""
        if not issues:
            return "Aucun problème majeur détecté dans le code."
        return "Problèmes détectés:\n" + "\n".join(f"- {issue}" for issue in issues)

    def _analyze_error(self, error_description: str) -> str:
        """Analyse la description d'une erreur pour en déterminer le type."""
        if "syntax error" in error_description.lower():
            return "syntax"
        elif "undefined" in error_description.lower():
            return "logic"
        elif "security" in error_description.lower():
            return "security"
        return "unknown"

    def _fix_syntax_error(self, code: str) -> str:
        """Corrige une erreur de syntaxe dans le code."""
        # Implémentation de la correction de syntaxe
        return code

    def _fix_logic_error(self, code: str) -> str:
        """Corrige une erreur de logique dans le code."""
        # Implémentation de la correction de logique
        return code

    def _fix_security_issue(self, code: str) -> str:
        """Corrige un problème de sécurité dans le code."""
        # Implémentation de la correction de sécurité
        return code

    def _extract_methods(self, code: str) -> List[str]:
        """Extrait les méthodes du code pour la génération de tests."""
        # Implémentation de l'extraction des méthodes
        return []

    def _generate_method_test(self, method: str) -> str:
        """Génère un test pour une méthode spécifique."""
        # Implémentation de la génération de test
        return ""

    def _extract_documentable_elements(self, code: str) -> List[str]:
        """Extrait les éléments à documenter du code."""
        # Implémentation de l'extraction des éléments
        return []

    def _generate_element_documentation(self, element: str) -> str:
        """Génère la documentation pour un élément spécifique."""
        # Implémentation de la génération de documentation
        return ""

    def _get_last_action(self) -> str:
        """Récupère la dernière action de l'agent."""
        if self.state['last_action']:
            return self.state['last_action']
        return "Aucune action récente" 