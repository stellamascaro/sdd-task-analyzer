# Especificação SDD — TaskAnalyzer

Autora: Stella Cardoso de Campos Mascaro — Ciência da Computação — Polo Asa Norte
Contrato transposto da Fase 1, com os ajustes de alinhamento da Fase 2 marcados como **[Fase 2]**.

## 1. Propósito
Processar um conjunto de tarefas executadas e gerar métricas de desempenho: tempo
médio de conclusão, taxa de atraso (tarefas concluídas após o prazo) e indicadores
por prioridade (baixa, media, alta).

## 2. Contrato executável de interface
```python
def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]
class TaskValidationError(ValueError)
```

### 2.1 Entradas
Lista de dicionários; cada tarefa contém:
| Campo | Tipo | Regra |
|---|---|---|
| id | int ou str | obrigatório |
| titulo | str | obrigatório |
| prioridade | str | "baixa", "media" ou "alta" |
| data_criacao | datetime | obrigatório |
| data_conclusao | datetime | obrigatória se status = "concluida"; ignorada se "pendente" |
| prazo | datetime | obrigatório |
| status | str | "pendente" ou "concluida" |

Datas sem fuso (naive) são tratadas como UTC.

### 2.2 Saídas
| Campo | Tipo | Descrição |
|---|---|---|
| total_tarefas | int | **[Fase 2]** total de tarefas |
| total_concluidas | int | **[Fase 2]** tarefas concluídas |
| total_pendentes | int | **[Fase 2]** tarefas pendentes |
| tempo_medio_conclusao_horas | float | **[Fase 2]** média em horas (data_conclusao − data_criacao) |
| tempo_medio_conclusao_global | float | nome da Fase 1; alias de tempo_medio_conclusao_horas |
| taxa_atraso_percentual | float | **[Fase 2]** % de concluídas com data_conclusao > prazo |
| taxa_atraso_global | float | nome da Fase 1; alias de taxa_atraso_percentual |
| indicadores_por_prioridade | dict | chaves "baixa", "media", "alta", cada uma com total_tarefas, total_concluidas, total_pendentes, tempo_medio_conclusao_horas e taxa_atraso_percentual |

### 2.3 Restrições de negócio
- Tempo médio e taxa de atraso consideram apenas tarefas "concluida"; "pendente" é ignorada.
- `data_conclusao` anterior à `data_criacao` dispara `TaskValidationError`.
- Campos ausentes, tipos ou valores inválidos disparam `TaskValidationError`.
- Divisão por zero prevenida: sem tarefas concluídas (inclusive lista vazia), médias e taxas valem `0.0`.
- Valores float arredondados em 2 casas decimais.

## 3. Cenários de aceite (BDD)
**Cenário 1 — Sucesso:** Dado um conjunto de tarefas válidas, com diferentes prioridades, prazos e status, quando o TaskAnalyzer for executado, então deve retornar as métricas corretas (global e por prioridade).

**Cenário 2 — Exceção/Erro:** Dada uma entrada com dados inconsistentes (ex.: data_conclusao anterior à data_criacao), quando o TaskAnalyzer for executado, então deve disparar exceção específica e tratada (`TaskValidationError`, subclasse de `ValueError`) com mensagem descritiva.

**Casos de borda [Fase 2]:** entrada vazia ou só com pendentes não dispara exceção: a divisão por zero é prevenida e as métricas retornam `0.0`.

## 4. Test Harness
Cenários → fixtures → `tests/test_harness.py` (pytest, `pytest.raises` para os erros) → homologação do código gerado pela IA.
