# dsh-safety-brief-check

**Boundary:** this plugin checks one **安全技术交底记录** for what a record can be held to — that the
columns your form requires are filled, that **everyone briefed appears as having signed**, that the
briefing is dated no later than the work, that the briefed trades cover the trades doing the work, and
that the record identifies its location and briefer. It does **not** judge whether the briefing content
was adequate, whether it was targeted at the right hazards, or whether a signature is genuine.

> ### ⚠️ One `error`, and two annulled mandatory provisions the pack refuses to misuse
>
> **`SB-002` is the only `error`-level rule**, and it rests on an administrative regulation:
> 《建设工程安全生产管理条例》**第二十七条** requires the briefing to be given "并由双方签字确认", with
> 第六十四条第（一）项 as its penalty. Everything else is capped at `warn` or `info`.
>
> The pack records two corrections that a reader would otherwise get wrong:
>
> **1. JGJ 59-2011's clause 3.1.3 — this plugin's closest fit — is a *recommendatory* assessment clause.**
> The standard's only mandatory provisions were 4.0.1 and 5.0.3, and **both were annulled** by
> 住房和城乡建设部公告 2022 年第 164 号 (effective 2023-06-01). So `SB-006` (three-party signatures) is
> `warn`, and its note says why.
>
> **2. GB 50656-2011's clause 10.0.6 lost its mandatory status by the same公告, and its "班前安全操作规程交底"
> wording sits in the 条文说明, not in a clause.** So this pack **does not cite that standard at all** —
> a test asserts the number never appears.
>
> **National law has no provision on pre-shift meetings.** 《安全生产法》's 119 articles contain no
> occurrence of 班前; neither the law, an administrative regulation, a departmental rule nor a national
> standard addresses it. Provincial documents (Shandong's 班前"晨会" guidance, for instance) exist but are
> **local, not national** — so any pre-shift check ships unconfigured and the pack says so.
>
> Stated limits: the signature check **compares name lists only** and cannot tell whether a signature is
> the person's own; the content check is a **literal word-occurrence test** and cannot tell whether a
> briefing was any good — JGJ 59-2011's own scoring table deducts points for "针对性不强", a judgement no
> string operation can make.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-safety-brief-check
dsh --profile <name> --dump-config | grep 'dsh-safety-brief-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`. As chaves e os parâmetros de cada regra estão em [README.md](README.md#configuration) (versão principal em inglês).

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-safety-brief-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-safety-brief-check contributors.
