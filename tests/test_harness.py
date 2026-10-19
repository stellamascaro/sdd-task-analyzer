"""Test Harness (pytest) do TaskAnalyzer.

Traduz os cenários de aceite Dado-Quando-Então da Fase 1 em testes
automatizados: Cenário 1 (sucesso), Cenário 2 (erro) e casos de borda.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from src.task_analyzer import TaskValidationError, analyze_tasks

BASE = datetime(2026, 3, 2, 8, 0, tzinfo=timezone.utc)


def _tarefa(
    id_tarefa: int | str,
    prioridade: str,
    status: str,
    conclusao_h: float | None = None,
    prazo_h: float = 24,
) -> dict[str, Any]:
    """Cria uma tarefa de teste com datas relativas a ``BASE`` (em horas)."""
    return {
        "id": id_tarefa,
        "titulo": f"Tarefa {id_tarefa}",
        "prioridade": prioridade,
        "data_criacao": BASE,
        "data_conclusao": (
            BASE + timedelta(hours=conclusao_h) if conclusao_h is not None else None
        ),
        "prazo": BASE + timedelta(hours=prazo_h),
        "status": status,
    }


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    """Conjunto de tarefas válidas (concluídas e pendentes) para o Cenário 1."""
    return [
        _tarefa(1, "alta", "concluida", conclusao_h=4, prazo_h=6),
        _tarefa(2, "alta", "concluida", conclusao_h=10, prazo_h=8),
        _tarefa(3, "media", "concluida", conclusao_h=6, prazo_h=12),
        _tarefa(4, "baixa", "pendente"),
        _tarefa(5, "media", "pendente"),
    ]


# ---------------- Cenário 1: sucesso ----------------
def test_cenario1_totais(tarefas_validas: list[dict[str, Any]]) -> None:
    """Dado tarefas válidas, quando analisadas, então os totais estão corretos."""
    r = analyze_tasks(tarefas_validas)
    assert r["total_tarefas"] == 5
    assert r["total_concluidas"] == 3
    assert r["total_pendentes"] == 2


def test_cenario1_tempo_medio_geral(tarefas_validas: list[dict[str, Any]]) -> None:
    """Tempo médio geral = (4 + 10 + 6) / 3 = 6.67 horas."""
    assert analyze_tasks(tarefas_validas)["tempo_medio_conclusao_horas"] == 6.67


def test_cenario1_taxa_atraso_geral(tarefas_validas: list[dict[str, Any]]) -> None:
    """1 de 3 concluídas após o prazo = 33.33%."""
    assert analyze_tasks(tarefas_validas)["taxa_atraso_percentual"] == 33.33


def test_cenario1_indicadores_por_prioridade(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Valida tempo médio e atraso agrupados por prioridade."""
    ind = analyze_tasks(tarefas_validas)["indicadores_por_prioridade"]
    assert ind["alta"]["tempo_medio_conclusao_horas"] == 7.0
    assert ind["alta"]["taxa_atraso_percentual"] == 50.0
    assert ind["media"]["tempo_medio_conclusao_horas"] == 6.0
    assert ind["media"]["taxa_atraso_percentual"] == 0.0
    assert ind["baixa"]["tempo_medio_conclusao_horas"] == 0.0
    assert ind["baixa"]["total_pendentes"] == 1


def test_cenario1_nomes_da_fase1_sao_aliases(
    tarefas_validas: list[dict[str, Any]],
) -> None:
    """Os nomes do contrato da Fase 1 retornam os mesmos valores."""
    r = analyze_tasks(tarefas_validas)
    assert r["tempo_medio_conclusao_global"] == r["tempo_medio_conclusao_horas"]
    assert r["taxa_atraso_global"] == r["taxa_atraso_percentual"]


def test_id_pode_ser_texto() -> None:
    """O contrato aceita id inteiro ou string."""
    assert analyze_tasks([_tarefa("T-1", "alta", "pendente")])["total_tarefas"] == 1


def test_datas_naive_sao_tratadas_como_utc() -> None:
    """Datas sem fuso são interpretadas como UTC."""
    tarefa = _tarefa(1, "baixa", "concluida", conclusao_h=2, prazo_h=4)
    tarefa["data_criacao"] = tarefa["data_criacao"].replace(tzinfo=None)
    assert analyze_tasks([tarefa])["tempo_medio_conclusao_horas"] == 2.0


# ---------------- Cenário 2: exceção/erro ----------------
def test_cenario2_conclusao_antes_da_criacao() -> None:
    """Dado data_conclusao < data_criacao, então dispara TaskValidationError."""
    tarefa = _tarefa(1, "alta", "concluida", conclusao_h=-2)
    with pytest.raises(TaskValidationError, match="anterior a 'data_criacao'"):
        analyze_tasks([tarefa])


def test_cenario2_excecao_e_um_value_error() -> None:
    """TaskValidationError é um ValueError (compatível com o contrato da Fase 1)."""
    with pytest.raises(ValueError):
        analyze_tasks([_tarefa(1, "alta", "concluida", conclusao_h=-1)])


def test_concluida_sem_data_conclusao() -> None:
    """Tarefa concluída sem data de conclusão é inválida."""
    with pytest.raises(TaskValidationError, match="data_conclusao"):
        analyze_tasks([_tarefa(1, "alta", "concluida")])


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("id", None),
        ("id", 1.5),
        ("id", True),
        ("titulo", 123),
        ("prioridade", "urgente"),
        ("prioridade", 3),
        ("status", "cancelada"),
        ("status", "em_andamento"),
        ("data_criacao", "2026-03-02"),
        ("prazo", None),
    ],
)
def test_campos_invalidos(campo: str, valor: Any) -> None:
    """Campos fora do domínio ou do tipo disparam TaskValidationError."""
    tarefa = _tarefa(1, "alta", "pendente")
    tarefa[campo] = valor
    with pytest.raises(TaskValidationError):
        analyze_tasks([tarefa])


def test_data_conclusao_com_tipo_invalido() -> None:
    """data_conclusao que não é datetime dispara TaskValidationError."""
    tarefa = _tarefa(1, "alta", "concluida", conclusao_h=2)
    tarefa["data_conclusao"] = "ontem"
    with pytest.raises(TaskValidationError, match="datetime"):
        analyze_tasks([tarefa])


def test_campo_obrigatorio_ausente() -> None:
    """Ausência de campo obrigatório dispara TaskValidationError."""
    tarefa = _tarefa(1, "alta", "pendente")
    del tarefa["titulo"]
    with pytest.raises(TaskValidationError, match="ausentes"):
        analyze_tasks([tarefa])


@pytest.mark.parametrize("entrada", [None, "tarefas", {"a": 1}, [1], [None]])
def test_entrada_com_tipo_invalido(entrada: Any) -> None:
    """Entradas que não são lista de dicionários disparam o erro."""
    with pytest.raises(TaskValidationError):
        analyze_tasks(entrada)


# ---------------- Casos de borda ----------------
def test_borda_entrada_vazia() -> None:
    """Lista vazia retorna zeros, sem exceção (divisão por zero prevenida)."""
    r = analyze_tasks([])
    assert r["total_tarefas"] == 0
    assert r["tempo_medio_conclusao_horas"] == 0.0
    assert r["taxa_atraso_percentual"] == 0.0
    assert r["indicadores_por_prioridade"]["alta"]["total_tarefas"] == 0


def test_borda_apenas_pendentes() -> None:
    """Somente pendentes: médias e taxas 0.0 sem exceção."""
    r = analyze_tasks([_tarefa(1, "alta", "pendente"), _tarefa(2, "baixa", "pendente")])
    assert r["total_pendentes"] == 2
    assert r["total_concluidas"] == 0
    assert r["tempo_medio_conclusao_horas"] == 0.0
    assert r["taxa_atraso_percentual"] == 0.0


def test_borda_pendentes_sao_ignoradas_nas_medias() -> None:
    """Tarefas pendentes não afetam tempo médio nem taxa de atraso."""
    r = analyze_tasks(
        [_tarefa(1, "alta", "pendente"), _tarefa(2, "alta", "concluida", conclusao_h=3)]
    )
    assert r["tempo_medio_conclusao_horas"] == 3.0
    assert r["taxa_atraso_percentual"] == 0.0


def test_borda_conclusao_exatamente_no_prazo_nao_e_atraso() -> None:
    """Conclusão igual ao prazo não é considerada atraso."""
    r = analyze_tasks([_tarefa(1, "alta", "concluida", conclusao_h=5, prazo_h=5)])
    assert r["taxa_atraso_percentual"] == 0.0


def test_borda_conclusao_igual_a_criacao() -> None:
    """Conclusão no mesmo instante da criação é válida (duração 0.0)."""
    r = analyze_tasks([_tarefa(1, "media", "concluida", conclusao_h=0)])
    assert r["tempo_medio_conclusao_horas"] == 0.0
