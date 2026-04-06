# VendaMais — Plataforma de Inteligência Operacional

> **Disciplina:** Design e Arquitetura de Software II · UNIVILLE · 2026/1  
> **Projeto Integrador:** VendaMais Distribuidora Ltda.  

---

## Descrição do Projeto

A **VendaMais Distribuidora Ltda.** é uma empresa de médio porte com operações em quatro estados do Sul e Sudeste do Brasil, processando cerca de 3.500 pedidos/mês com 18 representantes comerciais. Desde 2019, opera um ERP proprietário que centraliza todas as transações, porém sem capacidade analítica adequada — relatórios levam até 2 dias úteis para serem compilados manualmente e a diretoria toma decisões com dados de até 30 dias de defasagem.

Este repositório documenta a **arquitetura da Plataforma de Inteligência Operacional** que resolve esse problema, automatizando o pipeline de dados do ERP até o Power BI via Azure Cloud:

```
ERP Proprietário → Azure Functions (Ingestão) → Azure Blob Storage → Azure Functions (Transformação) → Azure SQL Database → Power BI Service
```

Ao final do projeto, a VendaMais poderá consultar seus indicadores operacionais com **defasagem máxima de 24 horas**, sem intervenção manual.

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

---

*Joinville, SC · 2026*
