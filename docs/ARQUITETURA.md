# Arquitetura do Sistema SENTINELA

O Módulo SENTINELA atua como uma camada analítica e de orquestração sobre o banco de dados Oracle transacional (Schema NEAC).

## 1. Princípios de Arquitetura

1. **Non-Blocking (Read-Only)**: O banco principal recebe milhares de registros do Pentaho (ETL). Para não competir com esse fluxo (locks ou deadlocks), o SENTINELA lê os dados de **Views Materializadas** criadas especificamente para ele (`VW_SENTINELA_CASO_COMPLETO`). Nenhuma operação do sistema fará `UPDATE` ou `INSERT` nos dados sensíveis.
2. **Desacoplamento por Eventos (Deltas)**: O Sentinela não consulta o banco a todo momento. Ele utiliza o **Agente Delta** num scheduler (Celery) que desperta imediatamente após a conclusão do Pentaho, identifica apenas o que foi alterado (`ALTER_DATE` ou `LOG_SISTEMA`) e joga a tarefa numa fila (Redis) para avaliação.
3. **Segurança por Design (LGPD)**: O mascaramento de PII ocorre **antes** dos dados chegarem à API. O Agente LGPD utiliza o Dicionário SQL (`SENTINELA_MASCARAMENTO`) para suprimir nomes, endereços e textos nas próprias Views ou nos serializers do backend.

## 2. Mapa de Schemas (Oracle)

- **NEAC**: Schema principal da aplicação. Contém as tabelas `CONTROLE_MORTE`, `DADOS_AUTOR`, `CONTROLE_ARMA`. O Sentinela criará suas tabelas de controle aqui (ex: `SENTINELA_FILA_ALERTAS`).
- **DAAS**: Schema da Polícia Civil. Fonte vital da `VW_BOLETIM_OCORRENCIA` e da base de elucidação `VW_PROCEDIMENTOS_DAAS`. Integrado via `BO_PC`.
- **SGOU**: Schema da Polícia Científica. Fonte vital da `VIEW_IML_NEAC_CADAVERICO`. Integrado via `NIC`.

## 3. Fluxo de Dados (A "Evolução para Óbito")

A regra de negócio mais importante do Sentinela funciona da seguinte forma:

1. O Pentaho roda de madrugada e popula a `NEAC.CONTROLE_MORTE` com novos CVLIs ou Tentativas (Vindos do CAD PM).
2. O Pentaho popula a `SGOU.VIEW_IML_NEAC_CADAVERICO` com os mortos que deram entrada no necrotério no último turno.
3. O Pentaho finaliza o ETL e dispara o gatilho para o **Agente Delta** (FastAPI / Celery).
4. O Agente Delta executa o script de cruzamento de `TENTATIVAS`. Ele olha para todos os registros em `CONTROLE_MORTE` que **não possuem NIC**, mas possuem `BO_PC` ou `NOME`. Ele varre a `VIEW_IML` procurando esses IDs.
5. Achando o `NIC` na base do IML, o Agente Delta registra um alerta "CRÍTICO" na `SENTINELA_FILA_ALERTAS`: *"Vítima da tentativa X evoluiu para Óbito e já possui NIC Y no IML"*.
6. O Analista, às 08:00, acessa o painel (Next.js). A API carrega o alerta através do Redis (extremamente rápido). O frontend exibe a linha do tempo e exige que o analista verifique o caso e o classifique.

## 4. Stack Tecnológico

| Camada | Tecnologia | Motivo |
|---|---|---|
| **Frontend** | Next.js (React), Tailwind v4, Framer Motion | Renderização híbrida (SEO/SSR para algumas rotas) e extrema facilidade na criação de interfaces Premium (Glassmorphism). |
| **Backend / API** | FastAPI (Python) | Alta performance (assíncrono nativo `asyncio`), autogeração de Swagger e tipagem estrita com Pydantic. |
| **Integração Oracle** | `oracledb` (Thin mode) | Dispensa a instalação pesada do Oracle Client na maioria dos casos, usando o protocolo nativo de rede. |
| **Filas e Cache** | Redis | Altíssimo throughput. Permite que os 8 Agentes distribuam tarefas entre si sem enfileirar consultas custosas no Oracle. |
| **Workers** | Celery | Orquestra e paralisa o poder de processamento do Agente de Qualidade e do Agente Científico (testes de hipótese robustos) sem travar a interface web. |
| **Containerização** | Docker, Docker Compose | Replica o ambiente idêntico (Prod/Staging/Dev) na SSP sem poluir os pacotes do Windows Server/Linux host. |
