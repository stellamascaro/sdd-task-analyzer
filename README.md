# sdd-taskanalyzer

Módulo **TaskAnalyzer** desenvolvido com *Spec-Driven Development* (SDD) e
assistentes de IA — Bootcamp III (CEUB EAD), Fase 2.

![CI](https://github.com/SEU_USUARIO/sdd-taskanalyzer/actions/workflows/ci.yml/badge.svg)

## Estrutura
```
sdd-taskanalyzer/
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── CONTEXT_RULES.md
├── specs/
│   ├── task_analyzer_spec.md
│   ├── requirements.yaml
│   └── system_design_document.pdf
├── tests/test_harness.py
├── src/task_analyzer.py
├── requirements.txt
└── README.md
```

## Como executar
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Executar com Docker
```bash
docker compose build
docker compose run --rm tests
```

## CI/CD
O workflow `.github/workflows/ci.yml` roda o pytest (Python 3.11, ubuntu-latest) em push e pull request nas branches `main` e `develop`.

## Uso
```python
from src.task_analyzer import analyze_tasks
metricas = analyze_tasks(lista_de_tarefas)
```

## Fluxo de trabalho
Contrato (`specs/`) + regras (`CONTEXT_RULES.md`) → IA gera código → testes
(pytest) → homologação humana → Pull Request → merge em `main`.

## Status
Fase 3 — CI/CD (GitHub Actions), Docker e governança de IA concluídos.

**Autora:** Stella Cardoso de Campos Mascaro — Ciência da Computação (Polo Asa Norte)
