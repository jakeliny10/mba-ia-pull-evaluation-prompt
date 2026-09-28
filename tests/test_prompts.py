"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        path = Path(__file__).resolve().parents[1] / "prompts" / "bug_to_user_story_v2.yml"
        self.prompt = load_prompts(path)["bug_to_user_story_v2"]

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert isinstance(self.prompt.get("system_prompt"), str)
        assert self.prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert "Você é" in self.prompt["system_prompt"]
        assert "Product Manager" in self.prompt["system_prompt"]

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        assert "Markdown" in self.prompt["system_prompt"]
        assert "Critérios de Aceitação" in self.prompt["system_prompt"]
        assert all(word in self.prompt["system_prompt"] for word in ("Dado", "Quando", "Então"))

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = self.prompt["system_prompt"]
        assert text.count("Entrada:") >= 2
        assert text.count("Saída:") >= 2
        assert text.count("Critérios de Aceitação:") >= 3

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "[TODO]" not in str(self.prompt)

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert "few-shot-learning" in techniques
        assert len(set(techniques)) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
