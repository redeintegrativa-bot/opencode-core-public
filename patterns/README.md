# Content Pipeline Patterns

Patterns extracted from `/root/maia-content-engine` for reusable content generation workflows.

## Content Pipeline Pattern

**Flow**: `Fetch → Analyze → Transform → Store → Serve`

A structured pipeline that retrieves raw data, processes it through analysis and transformation stages, persists results, and exposes them via API.

### Pipeline Steps

| Step | Function | Description |
|------|----------|-------------|
| **FETCH** | `montarBlocoBase()` | Retrieve raw Tzolkin calendar data (Kin number, archetype, seal, tones) |
| **ANALYZE** | `gerarInterpretacao()` | Generate human-readable interpretation with reflections and CTAs |
| **TRANSFORM** | `adaptarFormatos()` | Convert to platform-specific formats (WhatsApp, Instagram, YouTube) |
| **STORE** | `db.insert()` | Persist to SQLite via Drizzle ORM (dias → conteudoDiario → conteudoPlataforma) |
| **SERVE** | `NextResponse.json()` | Expose via Next.js API routes (POST/GET) |

### Pipeline Execution (`content-pipeline.ts:37`)

```typescript
async function executarPipeline(options: PipelineOptions): Promise<PipelineResult> {
  // 1. Cache check - skip if content exists
  // 2. Calculate Kin (FETCH)
  // 3. Generate interpretation (ANALYZE)
  // 4. Generate adaptations (TRANSFORM)
  // 5. Generate platform content (TRANSFORM)
  // 6. Save to DB (STORE)
}
```

### Data Flow

```
Input: { data: "2024-01-15", plataformas: ['whatsapp', 'instagram'] }
   │
   ▼
┌─────────────────────────────────────────────────────────┐
│ 1. FETCH: montarBlocoBase(date)                        │
│    → BlocoBase { kin, archetype, seal, colors, ... }   │
├─────────────────────────────────────────────────────────┤
│ 2. ANALYZE: gerarInterpretacao(bloco)                   │
│    → InterpretacaoHumana { reflexao, cta }              │
├─────────────────────────────────────────────────────────┤
│ 3. TRANSFORM: adaptarFormatos(bloco, interpretacao)     │
│    → AdaptacaoFormato { legenda, texto, roteiro }      │
├─────────────────────────────────────────────────────────┤
│ 4. PLATFORM: gerarConteudo{WhatsApp|Instagram|YouTube} │
│    → Platform-specific content objects                  │
├─────────────────────────────────────────────────────────┤
│ 5. STORE: db.insert(dias, conteudoDiario, plataformas)  │
│    → Persisted with UUIDs, status tracking              │
└─────────────────────────────────────────────────────────┘
   │
   ▼
Output: PipelineResult { bloco, interpretacao, adaptacoes, plataformas }
```

## DB Lazy-Loading Pattern

**File**: `lib/db/client.ts`

Connection established on first query, not at import time. Uses `Proxy` pattern for transparent lazy initialization.

### Implementation

```typescript
let _db: BetterSQLite3Database | null = null;

export function getDb(): BetterSQLite3Database {
  if (_db) return _db;
  // Dynamic import avoids build-time native module loading
  const DatabaseImpl = require('better-sqlite3');
  const { drizzle } = require('drizzle-orm/better-sqlite3');
  const sqlite = new DatabaseImpl('maia.db');
  _db = drizzle(sqlite, { schema });
  return _db;
}

// Lazy proxy — db.xxx calls getDb().xxx at runtime
export const db = new Proxy({} as BetterSQLite3Database, {
  get(_target, prop) {
    const dbInstance = getDb();
    const val = dbInstance[prop];
    if (typeof val === 'function') {
      return val.bind(dbInstance);
    }
    return val;
  },
});
```

### Key Benefits

1. **No build-time errors**: Dynamic `require()` prevents native module issues during Next.js build
2. **Transparent usage**: `db.select()` works exactly like a direct connection
3. **Singleton pattern**: Single connection instance reused across app
4. **Test-friendly**: Can mock `getDb()` independently

## Schema Structure

Three-table hierarchical design:

```
dias (day record)
  └── conteudoDiario (daily content)
        └── conteudoPlataforma (platform-specific content)
              └── media (generated assets)
```

### Table Relationships

| Table | FK | Purpose |
|-------|-----|---------|
| `dias` | — | Primary day record with Tzolkin data |
| `conteudoDiario` | `dias.id` | Generated content (reflections, CTAs, adaptations) |
| `conteudoPlataforma` | `conteudoDiario.id` | Platform-specific formatted content |
| `media` | `conteudoDiario.id` | Generated images/audio/video |
| `historicoGeracao` | `conteudoDiario.id` | Audit log of generation attempts |

### Status Workflow

```
conteudoDiario.status:  rascunho → revisao → aprovado → publicado
conteudoPlataforma.status: pendente → agendado → publicado | erro
media.status: pendente → gerando → concluido | erro
```

## API Layer Pattern

**File**: `app/api/gerar-conteudo/route.ts`

### POST /api/gerar-conteudo

```typescript
{
  data?: string,           // ISO date (defaults to today)
  plataformas?: string[],  // ['whatsapp', 'instagram', 'youtube']
  forcarRegeneracao?: boolean  // Skip cache check
}
```

### Response

```typescript
{
  blocoBase: BlocoBase,
  interpretacao: InterpretacaoHumana,
  adaptacoes: AdaptacaoFormato,
  plataformas: Record<string, unknown>,
  salvoNoDb: boolean,
  meta: { geradoEm: string, versaoPipeline: string }
}
```

## Reuse Checklist

When applying this pattern to new projects:

- [ ] Define `FETCH` function for your data source
- [ ] Create `ANALYZE` function for insight extraction
- [ ] Implement `TRANSFORM` for output formatting
- [ ] Design schema with hierarchical FK relationships
- [ ] Add lazy DB connection with Proxy pattern
- [ ] Expose via REST API with error handling
- [ ] Implement cache-first logic (check DB before generation)
- [ ] Track status transitions for content lifecycle
