# sdd-taskanalyzer

Módulo **TaskAnalyzer** desenvolvido com *Spec-Driven Development* (SDD) e
assistentes de IA — Bootcamp III (CEUB EAD), Fase 2.

![tests](https://img.shields.io/badge/tests-pytest-brightgreen)

## Estrutura
```
sdd-taskanalyzer/
├── README.md
├── CONTEXT_RULES.md
├── requirements.txt
├── specs/task_analyzer_spec.md
├── tests/test_harness.py
└── src/task_analyzer.py
```

## Como executar
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## Uso
```python
from src.task_analyzer import analyze_tasks
metricas = analyze_tasks(lista_de_tarefas)
```

## Fluxo de trabalho
Contrato (`specs/`) + regras (`CONTEXT_RULES.md`) → IA gera código → testes
(pytest) → homologação humana → Pull Request → merge em `main`.

## Status
Fase 2 — implementação e testes concluídos. Fase 3: CI/CD e Docker.

**Autora:** Stella Cardoso de Campos Mascaro — Ciência da Computação (Polo Asa Norte)
