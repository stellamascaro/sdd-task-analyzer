# CONTEXT_RULES — Governança de Contexto e Regras para Agentes de IA

Estas regras devem ser injetadas no prompt do assistente de IA antes de qualquer
geração de código, servindo como limites inegociáveis. Contrato de negócio:
`specs/task_analyzer_spec.md`.

## Diretrizes Arquiteturais (Obrigatórias)
1. A versão mínima obrigatória da linguagem é Python 3.11+.
2. É obrigatório o uso rigoroso de type hints (anotações de tipo) em todas as funções, métodos e retornos.
3. O código deve seguir o princípio de Responsabilidade Única (SRP) e o guia de estilo PEP 8.
4. A documentação deve seguir o padrão "Google style docstrings" para todos os módulos, classes, funções e parâmetros.
5. As funções devem ser curtas, coesas e resolver apenas um problema específico.
6. O tratamento de exceções deve ser granular (evitar blocos genéricos `except Exception:`) e retornar mensagens claras ao usuário.
7. É obrigatório o uso do módulo padrão `logging` do Python para logs estruturados em vez de comandos `print`.
8. Variáveis e funções devem ter nomes descritivos em inglês ou português padronizado, priorizando a legibilidade.

## Proibições Explícitas (Regras Restritivas)
1. NÃO utilizar bibliotecas externas não autorizadas (apenas bibliotecas padrão do Python, exceto o pytest para testes).
2. NÃO alterar, remover ou adaptar os cenários de teste fornecidos.
3. NÃO modificar a estrutura de pastas definida na arquitetura do repositório.
4. NÃO persistir dados localmente (arquivos .txt, .csv) ou em bancos de dados. O processamento deve ser em memória.
5. NÃO alterar a assinatura (nome da função e parâmetros) das funções públicas estipuladas no contrato sem autorização.
6. NÃO gerar novo código de produção sem o correspondente teste unitário.
7. NÃO inserir código duplicado ou comentários excessivos/óbvios.
8. NÃO assumir ou inventar comportamentos que não foram explicitamente definidos no contrato de negócio.
