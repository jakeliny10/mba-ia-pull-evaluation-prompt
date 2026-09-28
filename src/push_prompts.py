"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

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
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
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
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
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
