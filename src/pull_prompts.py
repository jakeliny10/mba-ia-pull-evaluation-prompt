"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "leonanluppi/bug_to_user_story_v1"
DESTINATION = ROOT / "prompts" / "bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """Busca a v1 pública e salva as mensagens em YAML legível."""
    prompt = Client().pull_prompt(SOURCE, dangerously_pull_public_prompt=True)
    messages = {}
    for message in prompt.messages:
        role = message.__class__.__name__.replace("MessagePromptTemplate", "").lower()
        if role not in {"system", "human"}:
            raise ValueError(f"Tipo de mensagem não suportado: {role}")
        key = "user_prompt" if role == "human" else "system_prompt"
        if key in messages:
            raise ValueError(f"Mensagem duplicada para {key}")
        messages[key] = message.prompt.template
    if set(messages) != {"system_prompt", "user_prompt"}:
        raise ValueError("O prompt semente precisa ter mensagens system e user")
    data = {"bug_to_user_story_v1": {
        "description": "Prompt semente obtido do LangSmith Prompt Hub",
        "system_prompt": messages["system_prompt"],
        "user_prompt": messages["user_prompt"],
        "version": "v1",
        "source": SOURCE,
    }}
    return save_yaml(data, str(DESTINATION))


def main():
    print_section_header("Pull do prompt semente")
    load_dotenv(ROOT / ".env")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1
    try:
        if not pull_prompts_from_langsmith():
            return 1
    except Exception as exc:
        print(f"❌ Falha no pull: {exc}")
        return 1
    print(f"✓ Prompt salvo em {DESTINATION}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
