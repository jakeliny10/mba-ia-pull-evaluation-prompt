import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup_prompt(self):
        path = Path(__file__).resolve().parents[1] / "prompts" / "bug_to_user_story_v2.yml"
        self.prompt = load_prompts(path)["bug_to_user_story_v2"]

    def test_prompt_has_system_prompt(self):
        assert isinstance(self.prompt.get("system_prompt"), str)
        assert self.prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self):
        assert "Você é" in self.prompt["system_prompt"]
        assert "Product Manager" in self.prompt["system_prompt"]

    def test_prompt_mentions_format(self):
        assert "Markdown" in self.prompt["system_prompt"]
        assert "Critérios de Aceitação" in self.prompt["system_prompt"]
        assert all(word in self.prompt["system_prompt"] for word in ("Dado", "Quando", "Então"))

    def test_prompt_has_few_shot_examples(self):
        text = self.prompt["system_prompt"]
        assert text.count("Entrada:") >= 2
        assert text.count("Saída:") >= 2
        assert text.count("Critérios de Aceitação:") >= 3

    def test_prompt_no_todos(self):
        assert "[TODO]" not in str(self.prompt)

    def test_minimum_techniques(self):
        techniques = self.prompt.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert "few-shot-learning" in techniques
        assert len(set(techniques)) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
