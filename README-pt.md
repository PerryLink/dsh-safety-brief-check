# dsh-safety-brief-check — Verificação da completude do registo de instrução técnica de segurança e do fecho de assinaturas

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-safety-brief-check` lê um registo de 安全技术交底记录 —os seus campos de cabeçalho, as suas listas de 被交底人 e de 签字, e as suas listas de 工种— e verifica a completude e o fecho desse próprio registo: se estão preenchidas as colunas que o seu formulário exige, se cada pessoa instruída consta dos signatários e ninguém assina duas vezes, se a 交底日期 não é posterior à 施工日期, se os ofícios que executam o trabalho constam da lista de 工种 instruídos, se o registo identifica o seu 工程部位 e o seu 交底人, e se reserva um lugar para as assinaturas do 交底人, do 被交底人 e do 专职安全员.

## Como é a saída

![Terminal demo of dsh-safety-brief-check: real output over its SB-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-safety-brief-check/main/docs/assets/dsh-safety-brief-check-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `SB-002` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Uma das pessoas instruídas nunca assinou. O que diz o relatório? | `SB-002` —a única regra de nível `error` do pacote— compara a lista de 被交底人 com a lista de 签字 e reporta cada pessoa que não aparece nela; um nome que aparece duas vezes na lista de assinaturas é reportado em separado, porque as duas falhas se corrigem de maneira diferente. Compara apenas as duas listas: não consegue saber se uma assinatura é da própria pessoa e não exige assinatura individual — se a sua instituição admite uma assinatura coletiva, indique-o no material ou inclua a regra em `disabledRules`. |
| A 交底日期 é posterior à 施工日期. É um erro? | `SB-003` reporta-o, e o mesmo dia conta como não posterior. A regra está limitada a `warn`: 第二十七条 dá 施工前 como premissa temporal mas não enuncia essa comparação, pelo que o achado é uma pista para revisão — uma instrução acrescentada a meio da obra por um perigo detetado mais tarde é legitimamente posterior e o registo deve dizê-lo. Uma data que não se consegue analisar é reportada por si, em vez de ser omitida em silêncio. |
| Que colunas tem o registo de preencher para passar a verificação? | `SB-001` lê `requiredFields`, que o pacote traz vazio, pelo que reporta `skipped` (未配置) em vez de passar. Quando indicar as colunas do seu formulário, reporta cada uma que falte ou esteja vazia — uma cadeia vazia conta como não preenchida — e não julga se o que nelas está escrito é correto. |
| O registo tem coluna de 被交底人 mas nenhum lugar para o 专职安全员. | `SB-006` verifica no cabeçalho se há um lugar para as três partes — 交底人, 被交底人 e 专职安全员 — e reporta as que não têm coluna; os nomes das colunas podem ser substituídos conforme o seu formulário. Mantém-se em `warn` porque o 第3.1.3条 da JGJ 59-2011 é uma cláusula recomendatória de avaliação (as suas únicas disposições obrigatórias, 第4.0.1、5.0.3条, foram revogadas pelo 住房和城乡建设部公告 2022 年第 164 号). Pergunta se o lugar existe, não se alguém ali assinou: essa é a pergunta do `SB-002`. |
| Os ofícios que trabalharam nessa parte não constam da lista de 工种 da instrução. | `SB-005` compara os ofícios que executam o trabalho com a lista de 工种 do registo e reporta os que não aparecem. Está limitada a `warn` porque a JGJ 59-2011 pede instruções 分部分项 mas não fixa nenhuma tabela obrigatória de correspondência com ofícios, e reporta `skipped` quando nem o material nem o parâmetro `workTrades` nomeiam os ofícios que trabalham, pois não codifica nenhuma lista de ofícios. Compara apenas nomes, pelo que 钢筋工 e 钢筋班组 contam como diferentes, e não julga se o conteúdo da instrução aborda esse ofício. |
| O registo não diz que 工程部位 abrange nem quem deu a instrução. | `SB-004` exige que o cabeçalho identifique o 工程部位 (`subject`) e o 交底人 (`briefer`), e reporta o que faltar; com `requireHeader` em false a regra não é executada. Está limitada a `warn` porque o 第8.2.1条 da GB 50870-2013 não enuncia campos de cabeçalho: sem eles o registo não pode mostrar quem instruiu quem sobre que parte, pelo que o achado é uma pista de rastreabilidade e não a afirmação de que a cláusula foi incumprida. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《建筑施工安全技术统一规范》 | GB 50870-2013 | SB-001, SB-002, SB-004, SB-007 |
| 《建筑施工安全检查标准》 | JGJ 59-2011 | SB-001, SB-002, SB-005, SB-006, SB-007 |
| 《建设工程安全生产管理条例》 | 国务院令第393号 | SB-002, SB-003 |

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

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/safety-brief-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

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
