# Documentação Técnica e Comparativo de Implementação — Projeto SENTINELA

Este documento apresenta uma análise comparativa detalhada das modificações introduzidas no repositório **SENTINELA** para a consolidação do **Motor de Reconciliação** no backend e o **Redesign UI/UX** no frontend, confrontando o estado anterior do código com a solução final homologada.

---

## 1. Tabela Comparativa: Estado Anterior vs. Estado Atual

| Área / Recurso | Estado Anterior (O que já tinha no repo) | Estado Atual (Implementado nesta fase) | Impacto e Benefício Técnico |
| :--- | :--- | :--- | :--- |
| **Arquitetura Visual** | Estética *glassmorphism* genérica, com fundos semi-transparentes (`backdrop-blur`), efeitos de brilho (`glow`), cantos muito arredondados e gradientes decorativos em roxo/azul. | Estética de **Console de Operações de Inteligência Policial**: superfícies opacas e sólidas, cantos retos/sutis (`rounded-sm`), divisórias finas de 1px e paleta cinza-chumbo neutra. | Reduz distração visual, aumenta a densidade de informação e melhora a legibilidade sob luz operacional. |
| **Tipografia** | Fontes padrão do navegador (sem definição estrita). Sem distinção entre títulos de seções, dados de auditoria e texto de leitura comum. | Integração de **três fontes otimizadas**: `IBM Plex Sans Condensed` (títulos de display em caixa alta), `Inter` (leitura geral e formulários) e `IBM Plex Mono` (dados numéricos e códigos de chaves). | Facilita a escaneabilidade rápida de dados sensíveis como números de Boletins de Ocorrência (BO), NICs e CADs. |
| **Fila de Auditoria** | Fila de alertas renderizada com cartões individuais (*grid* de cards), consumindo muita rolagem vertical e dificultando a visualização de longas listas. | Fila compacta em formato tabular denso usando o novo componente `DataTable`, com suporte a ordenação por clique no cabeçalho e marcações de prioridade por cores funcionais. | Permite ao analista gerenciar centenas de divergências de forma concentrada em uma única tela. |
| **Timeline de Caso** | Linha do tempo vertical tradicional com nós circulares genéricos e animações de ambiente redundantes do *Framer Motion*. | Timeline **horizontal compacta** (indicadora do fluxo operacional) com conectores de 1px sólidos. Nó do "IML" destaca-se em vermelho pulsante se houver sinalização de evolução de óbito. | Economia de espaço vertical na coluna central; destaque instantâneo para o evento crítico de óbito do necrotério. |
| **Qualidade das Fontes** | Três componentes de código duplicados (`NEACQualityCard`, `IMLQualityCard`, `DAASQualityCard`) replicando lógica de progresso em arquivos separados. | Componente único parametrizado `SourceQualityCard`, calculando integridade programaticamente e listando pendências críticas. | Redução de débito técnico, facilidade de manutenção e consistência visual de 100% nas três bases. |
| **Visualização de Mapa** | Mapa Leaflet utilizando estilos de satélite coloridos padrão, poluindo a visualização da mancha de criminalidade da cidade. | Mapa integrado com o Tile Layer escuro **CartoDB Dark Matter**, marcadores vermelhos para manchas de calor e marcador azul para o caso selecionado. | Foco total na geolocalização do caso atual; visual sóbrio condizente com telas de centrais de controle (CICC). |
| **Experiência de Polling** | O *polling* automático (busca de novos alertas) recarregava toda a interface da fila, exibindo um *spinner* a cada 30 segundos e fazendo a tela piscar. | Busca silenciosa em segundo plano. O estado de carregamento visual (`loading`) só é disparado no primeiro acesso ou na troca manual de filtros. | Fim da oscilação de tela, tornando a experiência de uso ininterrupta para o analista. |
| **Reconciliação Backend** | Sem capacidade de verificação automática pós-fato ou auditoria de divergências no IML e CAD. | **Motor de Reconciliação Delta**: comparador probabilístico CAD-PPE, detector de Maria da Penha, detector de Evolução de Óbito e tabelas de logs. | Automatização de auditoria diária de dados, removendo a necessidade de varredura manual de planilhas. |

---

## 2. Detalhamento Técnico das Implementações

### 2.1 Backend (Motor de Reconciliação e Auditoria)

1. **Modelagem de Dados de Auditoria**:
   * Criação do script DDL [sentinela_reconciliacao.sql](file:///c:/Users/james/OneDrive/Documentos/GitHub/sentinela/database/ddl/sentinela_reconciliacao.sql) definindo a tabela `SENTINELA_RECONCILIACAO_LOG`.
   * Criação do modelo ORM correspondente `SentinelaReconciliacaoLog` no arquivo [models.py](file:///c:/Users/james/OneDrive/Documentos/GitHub/sentinela/api/models.py).
2. **Implementação de Agentes Comparadores** (`agents/reconciliation_agent/`):
   * `iml_comparator.py`: Identifica corpos sem Declaração de Óbito (DO) e detecta evoluções de **Tentativa para Óbito** ocorridas em uma janela temporal retroativa de 30 dias.
   * `cad_comparator.py`: Algoritmo de cruzamento probabilístico entre ocorrências despachadas pela PM no CAD e boletins registrados pela PC no PPE baseando-se no endereço textual (descrição PPE) e coordenadas GPS CAD. Dispara a sinalização de *"GPS Disponível para Validação"* se as coordenadas forem preenchidas.
   * `ppe_comparator.py`: Audita alterações de tipificação (ex: tentativas reclassificadas como homicídio consumado no PPE) e analisa boletins em busca do agravante de feminicídio/violência doméstica (Lei Maria da Penha).
   * `orchestrator.py`: Orquestrador central que executa as cargas incrementais (delta) salvando os logs e gerando alertas na fila operacional do Sentinela.
3. **Serviços REST API**:
   * Implementação de rotas dedicadas em [reconciliacao.py](file:///c:/Users/james/OneDrive/Documentos/GitHub/sentinela/api/routes/reconciliacao.py) para expor estatísticas, listagem e resolução manual de divergências diretamente no painel.

### 2.2 Frontend (Redesenho UX/UI e Limpeza)

1. **Organização de Pastas e Componentização**:
   * Criados 5 componentes reutilizáveis sob [app/src/components/ui/](file:///c:/Users/james/OneDrive/Documentos/GitHub/sentinela/app/src/components/ui/):
     * `Card.tsx` (Contêiner sólido)
     * `Badge.tsx` (Pills de prioridade e status funcionais)
     * `DataTable.tsx` (Tabela rápida com cabeçalho ordenável)
     * `StatBlock.tsx` (Estatísticas e KPIs densos)
     * `SourceQualityCard.tsx` (Card de qualidade com progresso de preenchimento)
   * Remoção definitiva dos 3 arquivos legados duplicados: `NEACQualityCard.tsx`, `IMLQualityCard.tsx` e `DAASQualityCard.tsx`.
2. **Substituição de Estética e Estilização**:
   * Atualização de [globals.css](file:///c:/Users/james/OneDrive/Documentos/GitHub/sentinela/app/src/app/globals.css) para abolir blurs de vidro e injetar variáveis de cores sólidas e fontes institucionais.
   * Configuração de tipografia moderna do Google Fonts no arquivo [layout.tsx](file:///c:/Users/james/OneDrive/Documentos/GitHub/sentinela/app/src/app/layout.tsx).
3. **Página Principal do Dashboard (`page.tsx`)**:
   * Reformulação da tela dividindo a interface em 3 colunas fixas e simétricas:
     1. **Fila de Auditoria (Esquerda)**: Listagem unificada e rápida.
     2. **Linha do Tempo e Detalhes do Caso (Centro)**: Visualização horizontal do ciclo do fato com ações de resolução.
     3. **Mapa e Qualidade das Fontes (Direita)**: Geolocalização de manchas de calor criminais e integridade das tabelas de dados.

---

## 3. Manual de Execução e Homologação Local

### 3.1 Inicialização Automatizada (Ambiente Completo)
Para colocar os servidores no ar rapidamente, utilize o executável batch na raiz do projeto:
```powershell
.\start_ssp_sentinela.bat
```
*(Este script verifica a existência do banco local, inicia a API FastAPI na porta `8000`, inicializa o frontend Next.js na porta `3000` e abre o navegador automaticamente).*

### 3.2 Execução Manual de Etapas

1. **Sementeira de Dados e Teste do Motor**:
   ```bash
   python scripts/db_seeder.py
   ```
   *(Popula o banco SQLite local `sentinela.db` com dados realistas de teste, incluindo 410 registros de histórico operacional).*

2. **Inicialização Individual do Backend (FastAPI)**:
   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```
   * Documentação interativa (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

3. **Inicialização Individual do Frontend (Next.js)**:
   ```bash
   cd app
   npm run dev
   ```
   * Painel de Controle UI: [http://localhost:3000](http://localhost:3000)
