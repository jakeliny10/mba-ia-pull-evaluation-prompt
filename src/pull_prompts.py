import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "leonanluppi/bug_to_user_story_v1"
DESTINATION = ROOT / "prompts" / "bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
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
