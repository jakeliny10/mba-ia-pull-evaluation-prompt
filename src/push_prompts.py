import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])
    tags = list(dict.fromkeys(prompt_data.get("tags", []) + prompt_data["techniques_applied"]))
    try:
        url = Client().push_prompt(
            prompt_name,
            object=prompt,
            is_public=True,
            description=prompt_data["description"],
            tags=tags,
        )
    except Exception as exc:
        print(f"❌ Falha no push de {prompt_name}: {exc}")
        return False
    print(f"✓ Prompt publicado: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    _, errors = validate_prompt_structure(prompt_data)
    if not isinstance(prompt_data.get("user_prompt"), str) or not prompt_data["user_prompt"].strip():
        errors.append("user_prompt está vazio")
    if not errors:
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", prompt_data["system_prompt"]),
                ("user", prompt_data["user_prompt"]),
            ])
            if set(prompt.input_variables) != {"bug_report"}:
                errors.append("O template deve receber apenas {bug_report}")
        except Exception as exc:
            errors.append(f"Template inválido: {exc}")
    return not errors, errors


def main():
    print_section_header("Push do prompt otimizado")
    load_dotenv(ROOT / ".env")
    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1
    data = load_yaml(str(SOURCE))
    if not isinstance(data, dict) or not isinstance(data.get(PROMPT_KEY), dict):
        print(f"❌ Campo {PROMPT_KEY} ausente em {SOURCE}")
        return 1
    prompt_data = data[PROMPT_KEY]
    valid, errors = validate_prompt(prompt_data)
    if not valid:
        for error in errors:
            print(f"❌ {error}")
        return 1
    handle = os.environ["USERNAME_LANGSMITH_HUB"].strip()
    if not handle or "/" in handle:
        print("❌ USERNAME_LANGSMITH_HUB deve conter apenas o handle público")
        return 1
    name = f"{handle}/{PROMPT_KEY}"
    return 0 if push_prompt_to_langsmith(name, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
