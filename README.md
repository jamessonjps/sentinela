# SENTINELA - Módulo de Inteligência e Integração de CVLI

O **SENTINELA** é uma plataforma analítica robusta para a Secretaria de Segurança Pública (SSP), desenhada para processar, integrar e monitorar os dados de Crimes Violentos Letais Intencionais (CVLI) unindo dados da Polícia Civil, Polícia Militar e Polícia Científica (IML) sob estrita governança LGPD.

## 🚀 Visão Geral
O sistema funciona através de cruzamentos assíncronos (pós-ETL Pentaho) operados por 8 Agentes de IA Especializados. A lógica central da aplicação prevê o monitoramento de vítimas e agressores, identificando, por exemplo, quando uma "Tentativa de Homicídio" evolui para um "Óbito" dentro do Instituto Médico Legal (IML).

## 📁 Estrutura do Projeto

```text
SENTINELA/
│
├── agents/                  # Motor dos 8 Agentes Especializados (Microsserviços Python)
│   ├── delta_agent/         # Identifica "Tentativa -> Óbito" e cruza BOs
│   ├── lgpd_agent/          # Motor de Mascaramento, Supressão e Pseudonimização (PII)
│   ├── science_agent/       # Análise de perfil criminoso (Autoria) e Estatísticas de tempo
│   ├── quality_agent/       # Monitora o preenchimento das chaves universais (NIC, CAD, BO_PC)
│   ├── security_agent/      # Validação de queries, garantindo acesso READ ONLY ao banco
│   ├── structuring_agent/   # Normalização de dados e textos (TRATAR_BAIRROS, TRATAR_CIDADES)
│   ├── documentation_agent/ # Gera dicionários dinâmicos
│   └── testing_agent/       # Testes unitários e scanner de vazamento de PII
│
├── api/                     # Backend FastAPI
│   ├── main.py              # Ponto de entrada REST, CORS
│   ├── database.py          # Conexão oracledb (cx_Oracle)
│   └── routes/              # Endpoints consumidos pelo frontend
│
├── app/                     # Frontend UI (Next.js + Tailwind v4 + Framer Motion)
│   ├── src/app/             # Páginas (Dashboard Split-screen, Mapas)
│   └── src/components/      # Componentes Visuais (Timeline, AlertQueue)
│
├── database/                # Scripts SQL
│   ├── ddl/                 # Estruturas internas (Filas de Alerta, Checkpoints, Auditoria)
│   └── views/               # Views Materializadas Seguras de leitura não bloqueante
│
├── docs/                    # Documentação extensa do projeto (Arquitetura, Status)
│
├── scripts/anonimizacao/    # Scripts SQL geradores de amostras limitadas (Mock) e Mascaramento
│
├── docker-compose.yml       # Orquestrador de contêineres (Redis, FastAPI, Next.js, Celery)
├── Dockerfile.api           # Build do backend
└── Dockerfile.frontend      # Build do frontend
```

## 🔐 Integração e Segurança
O projeto está configurado para operar primordialmente sobre Views. Os únicos objetos de escrita são as tabelas internas `SENTINELA_*` (Fila, Checkpoint, Atribuição, Máscaras). Todos os acessos às tabelas de negócio (`NEAC`, `DAAS`, `SGOU`) operam em **READ ONLY**, prevenindo concorrência com o fluxo OLTP principal.

## 🛠️ Como Iniciar Localmente (Ambiente Dev)

Para subir todos os microsserviços integrados de forma simulada:

1. Assegure-se de que o Docker está instalado.
2. Na raiz do projeto, execute:
   ```bash
   docker-compose up --build
   ```
3. Acesso aos serviços:
   - **Frontend (Painel)**: [http://localhost:3000](http://localhost:3000)
   - **Backend API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

Consulte a pasta `docs/` para seções mais detalhadas sobre a Arquitetura e o Status atual da implantação.
