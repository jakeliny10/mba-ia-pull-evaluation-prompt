# Otimização e avaliação de prompts com LangChain e LangSmith

Entrega do desafio técnico do MBA em Engenharia de Software com IA.
O [fork público](https://github.com/jakeliny10/mba-ia-pull-evaluation-prompt)
contém o código Python, o prompt otimizado em YAML, os testes e as evidências.
A conta do GitHub é `jakeliny10`; o handle do LangSmith usado na avaliação é
`jakeliny`.

## O que foi implementado

- `src/pull_prompts.py` baixa `leonanluppi/bug_to_user_story_v1` do Prompt Hub
  e salva a versão local em `prompts/bug_to_user_story_v1.yml`.
- `prompts/bug_to_user_story_v2.yml` contém o prompt refatorado, com mensagens
  de sistema e usuário separadas.
- `src/push_prompts.py` valida o YAML e publica
  `jakeliny/bug_to_user_story_v2` como prompt público, com descrição e tags.
- `tests/test_prompts.py` implementa os seis testes de estrutura exigidos.
- `src/evaluate.py`, `src/metrics.py`, `src/utils.py` e o dataset de 15 bugs
  permanecem conforme o repositório base.

## Técnicas Aplicadas (Fase 2)

| Técnica | Aplicação e motivo |
| --- | --- |
| Few-shot Learning | Dois pares de entrada e saída mostram como escrever a história e os critérios de aceitação. Um deles também mostra como registrar uma informação ausente sem inventá-la. |
| Role Prompting | A mensagem de sistema define a persona de Product Manager para manter o foco no comportamento esperado e no benefício para a pessoa afetada. |
| Skeleton of Thought | O modelo organiza internamente ator, ação, resultado e critérios. A resposta segue uma estrutura Markdown com história e cenários Dado/Quando/Então. |

### Comparação entre v1 e v2

| Aspecto | v1 | v2 |
| --- | --- | --- |
| Relato do bug | Repetido nas mensagens de sistema e usuário | Informado uma vez, na mensagem de usuário |
| Orientação | Pedido genérico para criar uma história | Regras para preservar fatos, identificar impacto e produzir critérios verificáveis |
| Exemplos | Nenhum | Dois exemplos completos de entrada e saída |
| Casos incompletos | Sem tratamento | Lacunas vão para “Pontos a esclarecer”; relato vazio não gera história inventada |
| Formato | Livre | Markdown com história e critérios de aceitação |

A primeira publicação da v2 atingiu o mínimo exigido. Por isso, não foi
necessário alterar o prompt e repetir o experimento. As notas ilustrativas do
enunciado não foram usadas como resultados da v1.

## Resultados Finais

A avaliação de 27/09/2026 usou `gpt-4.1-mini` para geração e para as métricas.
O experimento executou os 15 exemplos do dataset. Todas as cinco médias e a
média geral superaram 0,8:

| Métrica | Média |
| --- | ---: |
| Helpfulness | 0,83 |
| Correctness | 0,83 |
| F1-Score | 0,81 |
| Clarity | 0,81 |
| Precision | 0,85 |
| Média geral | 0,8256 |

Evidências:

- [Dataset público com os 15 exemplos e o experimento](https://smith.langchain.com/public/e81f2e57-cdc6-4c2c-ac4f-4d8eec932115/d)
- [Captura do dashboard com as cinco métricas](evidencias/dataset-publico.png)
- [Experimento no workspace LangSmith](https://smith.langchain.com/o/a1a9be2d-b8a3-431d-b3c9-6d48d37c65af/datasets/2464de5d-3e55-4bb3-905f-7821fdc8291c/compare?selectedSessions=8b91dbdf-79e9-4834-bf18-262c686ad107)
- Traces individuais no workspace: [1](https://smith.langchain.com/o/a1a9be2d-b8a3-431d-b3c9-6d48d37c65af/projects/p/8b91dbdf-79e9-4834-bf18-262c686ad107/r/01a0e579-15e4-7770-a846-00dd9611ca62?poll=true), [2](https://smith.langchain.com/o/a1a9be2d-b8a3-431d-b3c9-6d48d37c65af/projects/p/8b91dbdf-79e9-4834-bf18-262c686ad107/r/01a0e579-0ee0-7fd0-a692-b391a2503dc6?poll=true), [3](https://smith.langchain.com/o/a1a9be2d-b8a3-431d-b3c9-6d48d37c65af/projects/p/8b91dbdf-79e9-4834-bf18-262c686ad107/r/01a0e579-07bc-75b0-a4cd-dfa33cda8a51?poll=true).

O dataset e a captura são públicos. Os links diretos do experimento e dos
traces exigem acesso ao workspace; as execuções podem ser abertas pelo dataset
público.

## Como Executar

Requer Python 3.10+, uma conta no LangSmith, handle público do Prompt Hub e
chave de API de um provedor de LLM. O projeto aceita OpenAI e Gemini. Escolha
modelos disponíveis nas páginas oficiais da
[OpenAI](https://developers.openai.com/api/docs/models) ou do
[Gemini](https://ai.google.dev/gemini-api/docs/models).

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha no `.env` local `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`,
`USERNAME_LANGSMITH_HUB`, `LLM_PROVIDER`, `LLM_MODEL`, `EVAL_MODEL` e
`OPENAI_API_KEY` ou `GOOGLE_API_KEY`. Para Gemini, use
`LLM_PROVIDER=google`. O `.env` está no `.gitignore`; nunca publique as
chaves. Crie o handle público no LangSmith antes de fazer o push.

```bash
python src/pull_prompts.py
pytest tests/test_prompts.py
python src/push_prompts.py
python src/evaluate.py
```

O pull substitui a cópia local da v1. O push publica a v2 definida no YAML.
Cada avaliação cria um experimento no LangSmith e imprime seu link. Se alguma
das cinco métricas ficar abaixo de 0,8, revise apenas a v2, faça novo push e
avalie novamente. Não altere o dataset nem os scripts de métricas para ajustar
o resultado. O dataset desta entrega já foi compartilhado; compartilhá-lo
novamente pode trocar o link público registrado acima.

Para entregar na plataforma do MBA, envie o link do fork público no início
deste README.
