# VendaMais — Plataforma de Inteligência Operacional

> **Disciplina:** Design e Arquitetura de Software II · UNIVILLE · 2026/1
> **Projeto Integrador:** VendaMais Distribuidora Ltda.

---

## Descrição do Projeto

A **VendaMais Distribuidora Ltda.** é uma empresa de médio porte com operações em quatro estados do Sul e Sudeste do Brasil, processando cerca de 3.500 pedidos/mês com 18 representantes comerciais. Desde 2019, opera um ERP proprietário que centraliza todas as transações, porém sem capacidade analítica adequada. Relatórios levam até 2 dias úteis para serem compilados manualmente e a diretoria toma decisões com dados de até 30 dias de defasagem.

Este repositório documenta a **arquitetura da Plataforma de Inteligência Operacional** que resolve esse problema, automatizando o pipeline de dados do ERP até o Power BI via Azure Cloud:

```
ERP Proprietário → Azure Functions (Ingestão) → Azure Blob Storage → Azure Functions (Transformação) → Azure SQL Database → Power BI Service
```

Ao final do projeto, a VendaMais poderá consultar seus indicadores operacionais com **defasagem máxima de 24 horas**, sem intervenção manual.

---

## Dashboard — Power BI

O dashboard **VendaMais** foi desenvolvido no Power BI Desktop e consome os dados processados pelo pipeline de transformação. Ele oferece visibilidade em tempo quase real sobre os principais indicadores comerciais da distribuidora.

### Preview

<img width="1407" height="782" alt="image" src="https://github.com/user-attachments/assets/737bb124-2875-4a50-8a2a-df9eee22476c" />


### Principais Indicadores

| Indicador | Descrição |
|-----------|-----------|
| **Valor Bruto** | Soma total dos pedidos antes de descontos |
| **Valor com Desconto** | Total de descontos aplicados nos pedidos |
| **Valor Líquido** | Receita efetiva após descontos |
| **Número Total de Pedidos** | Contagem de pedidos no período selecionado |

### Visualizações Disponíveis

- **Valor Líquido por Região** — comparativo entre Região Centro MS, Sudeste SP e Sul SC
- **Status por Pedido** — distribuição em gráfico de pizza (Faturado · Aberto · Cancelado)
- **Valor Líquido por Representante** — ranking de desempenho dos representantes comerciais
- **Valor Líquido por Cliente** — top clientes por volume faturado
- **Mapa Geográfico** — distribuição dos pedidos pelos estados atendidos
- **Observação por Pedido** — painel de anotações vinculadas a cada pedido
- **Filtro por Pedido** — seleção individual ou geral via painel lateral

### Arquivo Power BI

O arquivo fonte do dashboard está disponível em:

📊 [`VendaMais_Dashboard.pbix`](./docs/assets/VendaMais_Dashboard.pbix)

> **Requisito:** Power BI Desktop (gratuito) — [Download aqui](https://powerbi.microsoft.com/pt-br/desktop/)

Para abrir localmente:
1. Instale o Power BI Desktop
2. Abra o arquivo `VendaMais_Dashboard.pbix`
3. Na aba **Página Inicial**, clique em **Atualizar** para recarregar os dados (requer conexão com o Azure SQL configurada)

---

## Integrantes da Equipe

| Nome | GitHub |
|------|--------|
| Integrante 1 | [@Christyassolini](https://github.com/Christyassolini/) |
| Integrante 2 | [@IsabeleVitoriaPires](https://github.com/IsabeleVitoriaPires) |
| Integrante 3 | [@vitorhugoramosd](https://github.com/vitorhugoramosd) |
| Integrante 4 | [@julial0pes](https://github.com/julial0pes) |

---

## Estrutura do Repositório

```
vendamais-plataforma/
│
├── README.md                        ← Este arquivo — visão geral e navegação
│
└── docs/
    ├── assets/
    │   ├── dashboard_vendamais.png  ← Screenshot do dashboard Power BI
    │   └── VendaMais_Dashboard.pbix ← Arquivo fonte do dashboard Power BI
    │
    ├── c4/
    │   ├── 01-context.md            ← C4 Nível 1: Diagrama de Contexto do Sistema
    │   └── 02-container.md          ← C4 Nível 2: Diagrama de Containers
    │
    └── adr/
        ├── ADR-001.md               ← Decisão: Estratégia de Ingestão (Azure Functions)
        └── ADR-002.md               ← Decisão: Estratégia de Armazenamento (Azure SQL Database)
```

---

## Como Navegar na Documentação

### 1. Entenda o contexto do sistema

Comece pelo **[C4 Nível 1 — Diagrama de Contexto](docs/c4/01-context.md)** para entender quem usa o sistema, quais sistemas externos estão envolvidos e qual é o escopo da solução.

### 2. Veja como o sistema é decomposto

Em seguida, acesse o **[C4 Nível 2 — Diagrama de Containers](docs/c4/02-container.md)** para entender os cinco containers da solução, suas tecnologias, responsabilidades e como eles se comunicam.

### 3. Entenda as decisões técnicas

- **[ADR-001 — Estratégia de Ingestão](docs/adr/ADR-001.md):** Por que usamos Azure Functions serverless para extrair dados do ERP.
- **[ADR-002 — Estratégia de Armazenamento](docs/adr/ADR-002.md):** Por que usamos Azure SQL Database como repositório analítico central.

### 4. Explore o dashboard

Abra o **[arquivo .pbix](docs/assets/VendaMais_Dashboard.pbix)** no Power BI Desktop para navegar pelo dashboard interativo com todos os filtros e visuais disponíveis.

---

*Joinville, SC · 2026*
