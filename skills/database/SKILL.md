# Database

## Description
Ajuda com banco de dados: SQL queries, migrations, models, otimização.

## Activation
Slash command: `/database` ou quando o usuário falar de banco de dados, SQL, migrations.

## Parameters
- `action`: O que fazer (`query`, `model`, `migration`, `optimize`, `design`)
- `db_type`: Tipo de banco (`sqlite`, `postgres`, `mysql`, `mongodb`)

## Actions

### Query
- Escreve consultas SQL
- Explica queries complexas
- Otimiza queries lentas
- Traduz entre dialetos SQL

### Model
- Gera modelos ORM (SQLAlchemy, Prisma, TypeORM, Mongoose)
- Define relacionamentos
- Cria schemas de validação

### Migration
- Gera migrations a partir de modelos
- Explica migrações existentes
- Ajuda a resolver conflitos de migration

### Optimize
- Analisa EXPLAIN plans
- Sugere índices
- Recomenda refatorações de schema
- Identifica N+1 queries

### Design
- Modelagem entidade-relacionamento
- Normalização de dados
- Estratégias de indexação
- Padrões de nomenclatura

## Examples

```
User: "Preciso de uma query SQL pra buscar usuários com pedidos nos últimos 30 dias"
Agent: Gera a query SQL explicada

User: "Cria um modelo SQLAlchemy para Product com categorias e tags"
Agent: Gera o modelo Python completo

User: "Como otimizar essa query? [query aqui]"
Agent: Analisa e sugere índices + refatoração
```

## Rules
- Prefira SQLite exemplos (funciona em qualquer lugar, inclusive Termux)
- Mostre sempre o schema esperado
- Explique decisões de design
- Inclua exemplos de uso
