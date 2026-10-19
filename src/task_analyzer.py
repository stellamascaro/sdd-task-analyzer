"""Módulo TaskAnalyzer.

Calcula métricas de produtividade (totais, tempo médio de conclusão e taxa de
atraso) a partir de uma lista de tarefas, conforme o contrato definido em
``specs/task_analyzer_spec.md`` e as regras de ``CONTEXT_RULES.md``.

Código gerado com assistente de IA e homologado por revisão humana.
"""

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: tuple[str, ...] = ("baixa", "media", "alta")
STATUS_VALIDOS: tuple[str, ...] = ("pendente", "concluida")
CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
    "id",
    "titulo",
    "prioridade",
    "data_criacao",
    "prazo",
    "status",
)
SEGUNDOS_POR_HORA: float = 3600.0


class TaskValidationError(ValueError):
    """Erro de validação dos dados de entrada do TaskAnalyzer.

    Disparado quando uma tarefa possui campos ausentes, tipos inválidos,
    valores fora do domínio ou datas inconsistentes.
    """


def _para_utc(valor: Any, campo: str, indice: int) -> datetime:
    """Valida um datetime e o converte para UTC (datetime naive é tratado como UTC).

    Args:
        valor: Valor bruto da data.
        campo: Nome do campo, usado na mensagem de erro.
        indice: Posição da tarefa na lista de entrada.

    Returns:
        Datetime com fuso UTC.

    Raises:
        TaskValidationError: Se o valor não for um datetime.
    """
    if not isinstance(valor, datetime):
        raise TaskValidationError(
            f"Tarefa #{indice}: o campo '{campo}' deve ser datetime."
        )
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def _validar_identificacao(tarefa: dict[str, Any], indice: int) -> None:
    """Valida os campos ``id`` (inteiro ou string) e ``titulo`` (string).

    Args:
        tarefa: Dicionário com os dados da tarefa.
        indice: Posição da tarefa na lista de entrada.

    Raises:
        TaskValidationError: Se ``id`` ou ``titulo`` tiverem tipo inválido.
    """
    identificador = tarefa["id"]
    id_valido = isinstance(identificador, str) or (
        isinstance(identificador, int) and not isinstance(identificador, bool)
    )
    if not id_valido:
        raise TaskValidationError(f"Tarefa #{indice}: 'id' deve ser inteiro ou texto.")
    if not isinstance(tarefa["titulo"], str):
        raise TaskValidationError(f"Tarefa #{indice}: 'titulo' deve ser texto.")


def _validar_dominio(tarefa: dict[str, Any], indice: int) -> tuple[str, str]:
    """Valida ``prioridade`` e ``status`` contra os valores permitidos.

    Args:
        tarefa: Dicionário com os dados da tarefa.
        indice: Posição da tarefa na lista de entrada.

    Returns:
        Tupla ``(prioridade, status)`` validada.

    Raises:
        TaskValidationError: Se algum valor estiver fora do domínio permitido.
    """
    prioridade = tarefa["prioridade"]
    status = tarefa["status"]
    if prioridade not in PRIORIDADES_VALIDAS:
        raise TaskValidationError(
            f"Tarefa #{indice}: prioridade inválida {prioridade!r}; "
            f"use {PRIORIDADES_VALIDAS}."
        )
    if status not in STATUS_VALIDOS:
        raise TaskValidationError(
            f"Tarefa #{indice}: status inválido {status!r}; use {STATUS_VALIDOS}."
        )
    return prioridade, status


def _calcular_conclusao(tarefa: dict[str, Any], indice: int) -> tuple[float, bool]:
    """Calcula duração (horas) e atraso de uma tarefa concluída.

    Args:
        tarefa: Tarefa com ``status == "concluida"``.
        indice: Posição da tarefa na lista de entrada.

    Returns:
        Tupla ``(duracao_em_horas, atrasada)``.

    Raises:
        TaskValidationError: Se ``data_conclusao`` faltar, for inválida ou
            anterior à ``data_criacao``.
    """
    conclusao_bruta = tarefa.get("data_conclusao")
    if conclusao_bruta is None:
        raise TaskValidationError(
            f"Tarefa #{indice}: tarefa concluída exige 'data_conclusao'."
        )
    criacao = _para_utc(tarefa["data_criacao"], "data_criacao", indice)
    prazo = _para_utc(tarefa["prazo"], "prazo", indice)
    conclusao = _para_utc(conclusao_bruta, "data_conclusao", indice)
    if conclusao < criacao:
        raise TaskValidationError(
            f"Tarefa #{indice}: 'data_conclusao' anterior a 'data_criacao'."
        )
    duracao_horas = (conclusao - criacao).total_seconds() / SEGUNDOS_POR_HORA
    return duracao_horas, conclusao > prazo


def _validar_tarefa(tarefa: Any, indice: int) -> dict[str, Any]:
    """Valida uma tarefa e devolve uma versão normalizada para cálculo.

    Args:
        tarefa: Dicionário com os dados da tarefa.
        indice: Posição da tarefa na lista de entrada.

    Returns:
        Dicionário com ``prioridade``, ``status``, ``duracao_horas``
        (``None`` se pendente) e ``atrasada``.

    Raises:
        TaskValidationError: Se algum campo for inválido ou as datas forem
            inconsistentes.
    """
    if not isinstance(tarefa, dict):
        raise TaskValidationError(f"Tarefa #{indice}: deve ser um dicionário.")
    ausentes = [c for c in CAMPOS_OBRIGATORIOS if c not in tarefa]
    if ausentes:
        raise TaskValidationError(
            f"Tarefa #{indice}: campos obrigatórios ausentes: {ausentes}."
        )
    _validar_identificacao(tarefa, indice)
    prioridade, status = _validar_dominio(tarefa, indice)
    _para_utc(tarefa["data_criacao"], "data_criacao", indice)
    _para_utc(tarefa["prazo"], "prazo", indice)

    duracao_horas: float | None = None
    atrasada = False
    if status == "concluida":
        duracao_horas, atrasada = _calcular_conclusao(tarefa, indice)
    return {
        "prioridade": prioridade,
        "status": status,
        "duracao_horas": duracao_horas,
        "atrasada": atrasada,
    }


def _media(valores: list[float]) -> float:
    """Calcula a média com 2 casas decimais, retornando 0.0 se a lista for vazia.

    Args:
        valores: Lista de números.

    Returns:
        Média arredondada ou 0.0 (prevenção de divisão por zero).
    """
    if not valores:
        return 0.0
    return round(sum(valores) / len(valores), 2)


def _taxa_atraso(concluidas: list[dict[str, Any]]) -> float:
    """Calcula o percentual de tarefas concluídas após o prazo.

    Args:
        concluidas: Tarefas normalizadas com status ``concluida``.

    Returns:
        Percentual com 2 casas decimais, ou 0.0 se não houver concluídas.
    """
    if not concluidas:
        return 0.0
    atrasadas = sum(1 for t in concluidas if t["atrasada"])
    return round(atrasadas / len(concluidas) * 100, 2)


def _resumir(tarefas: list[dict[str, Any]]) -> dict[str, Any]:
    """Gera o conjunto de métricas para um grupo de tarefas normalizadas.

    Args:
        tarefas: Tarefas normalizadas (qualquer status).

    Returns:
        Dicionário com totais, tempo médio (horas) e taxa de atraso (%).
    """
    concluidas = [t for t in tarefas if t["status"] == "concluida"]
    return {
        "total_tarefas": len(tarefas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(tarefas) - len(concluidas),
        "tempo_medio_conclusao_horas": _media(
            [t["duracao_horas"] for t in concluidas]
        ),
        "taxa_atraso_percentual": _taxa_atraso(concluidas),
    }


def analyze_tasks(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Analisa tarefas e retorna métricas de produtividade.

    Args:
        tasks: Lista de dicionários com as chaves ``id``, ``titulo``,
            ``prioridade`` ("baixa", "media", "alta"), ``data_criacao``,
            ``prazo``, ``status`` ("pendente", "concluida") e
            ``data_conclusao`` (obrigatória quando ``status == "concluida"``).

    Returns:
        Dicionário com ``total_tarefas``, ``total_concluidas``,
        ``total_pendentes``, ``tempo_medio_conclusao_horas`` (alias
        ``tempo_medio_conclusao_global``), ``taxa_atraso_percentual`` (alias
        ``taxa_atraso_global``) e ``indicadores_por_prioridade`` (baixa,
        media, alta). Médias e taxas sem tarefas concluídas retornam 0.0.

    Raises:
        TaskValidationError: Se a entrada for inválida (tipos, domínio ou
            datas inconsistentes).
    """
    if not isinstance(tasks, list):
        raise TaskValidationError("A entrada deve ser uma lista de tarefas.")

    normalizadas = [_validar_tarefa(t, i) for i, t in enumerate(tasks)]

    resultado = _resumir(normalizadas)
    resultado["tempo_medio_conclusao_global"] = resultado["tempo_medio_conclusao_horas"]
    resultado["taxa_atraso_global"] = resultado["taxa_atraso_percentual"]
    resultado["indicadores_por_prioridade"] = {
        prioridade: _resumir([t for t in normalizadas if t["prioridade"] == prioridade])
        for prioridade in PRIORIDADES_VALIDAS
    }
    logger.info("Análise concluída: %d tarefas processadas.", len(normalizadas))
    return resultado
