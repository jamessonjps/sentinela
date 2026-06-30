# Status Atual do Projeto SENTINELA

## Progresso Geral: 100% (Fases 1 a 5 Concluídas)

O desenvolvimento arquitetural e estrutural do Módulo SENTINELA foi **concluído**. Abaixo detalhamos exatamente o que já foi codificado, gerado e está presente no repositório.

### FASE 1: Banco de Dados e LGPD (CONCLUÍDO ✅)
- **Tabelas Internas**: Script DDL criado em `database/ddl/sentinela_tables.sql` para suportar `FILA_ALERTAS`, `AUDITORIA`, etc.
- **Views Seguras**: O cruzamento complexo integrando dados da PM (CAD), PC (BO_PC, DAAS) e IML (NIC, SGOU) foi abstraído para views `READ_ONLY` no arquivo `database/views/sentinela_views.sql`.
- **Amostras Cegas**: Criamos o `generate_mock_data.sql` limitando as tabelas vitais (100 linhas) para teste.
- **Agente LGPD**: Lógica Python (`agents/lgpd_agent`) finalizada, mascarando `NOME_VITIMA`, `CPF`, `RELATO_HISTORICO` (DAAS), permitindo fluxo de dados sem vazar PII para a interface do analista.

### FASE 2: Inteligência e Regra de Negócio (CONCLUÍDO ✅)
- **Agente Delta**: O script `agents/delta_agent/change_detector.py` foi codificado com a **lógica real solicitada**.
  - **Lógica Implementada:** Ele faz a varredura da tabela `CONTROLE_MORTE` filtrando casos marcados como `TENTATIVA` (onde o NIC é NULL). Em seguida, efetua o cruzamento direto com a tabela `VIEW_IML_NEAC_CADAVERICO` usando o `BO_PC` ou similaridade do nome da vítima. Quando o cruzamento ocorre positivamente, o sistema atualiza o caso informando a "Evolução para Óbito" e extrai o `NIC` gerado no IML.
- **Agente de Segurança**: Implementado para blindar operações contra INSERT/UPDATE no banco de dados principal.
- **Agente de Estruturação**: Lógicas para tratar cidades e bairros usando `TRATAR_CIDADES` e `TRATAR_BAIRROS`.

### FASE 3: API e Integração (CONCLUÍDO ✅)
- **FastAPI Backend**: Rotas REST construídas em `api/` para servir os alertas ao FrontEnd.
- **Agente Científico**: Endpoints de extração desenvolvidos para processamento de perfil dos Autores da tabela `DADOS_AUTOR`.
- **Agente de Qualidade**: Algoritmo para cálculo de SLA de preenchimento (`NIC`, `CAD`, `BO_PC`) pelos analistas em até 24 horas.

### FASE 4: Frontend Premium (CONCLUÍDO ✅)
- **App Next.js Gerado**: O repositório foi inicializado dentro da pasta `app/` usando Typescript.
- **Estética UI/UX**: Configuradas as classes do **Tailwind v4** baseadas em *Glassmorphism* e sistema de cores HSL da SSP.
- **Componentes React**:
  - `AlertQueue.tsx`: Fila de despachos.
  - `CrimeMap.tsx`: Visão geoespacial usando `react-leaflet`.
  - `CaseTimeline.tsx`: Exibição visual animada com `Framer Motion` mostrando Fato -> BO -> IML.

### FASE 5: Containerização (CONCLUÍDO ✅)
- **Dockerfiles**: O Backend (`Dockerfile.api`) e o Frontend (`Dockerfile.frontend`) foram criados.
- **Orquestração**: O `docker-compose.yml` foi escrito contendo as filas do **Redis** e os workers assíncronos do **Celery**, unindo tudo em uma rede isolada.

---

## O que Falta Fazer (Validação)
A nível de código, o esqueleto, os agentes e a lógica central já estão materializados nos arquivos do seu computador local.
O próximo passo lógico é:
1. Executar o Docker (`docker-compose up`).
2. Validar o painel visual na porta `:3000`.
3. Certificar a conexão do cx_Oracle com o ambiente de testes da Secretaria.
