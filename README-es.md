# dsh-safety-brief-check — Comprobación de la completitud del registro de instrucción técnica de seguridad y del cierre de firmas

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-safety-brief-check` lee un registro de 安全技术交底记录 —sus campos de cabecera, sus listas de 被交底人 y de 签字, y sus listas de 工种— y comprueba la completitud y el cierre de ese propio registro: que estén rellenas las columnas que exige su formulario, que toda persona instruida figure entre los firmantes y que nadie firme dos veces, que la 交底日期 no sea posterior a la 施工日期, que los oficios que ejecutan el trabajo aparezcan en la lista de 工种 instruidos, que el registro identifique su 工程部位 y su 交底人, y que reserve un lugar para las firmas del 交底人, del 被交底人 y del 专职安全员.

## Cómo se ve la salida

![Terminal demo of dsh-safety-brief-check: real output over its SB-002 fixture](https://raw.githubusercontent.com/PerryLink/dsh-safety-brief-check/main/docs/assets/dsh-safety-brief-check-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `SB-002` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Una de las personas instruidas nunca firmó. ¿Qué dice el informe? | `SB-002` —la única regla de nivel `error` del paquete— compara la lista de 被交底人 con la lista de 签字 e informa de cada persona que no aparece en ella; un nombre que aparece dos veces en la lista de firmas se informa por separado, porque ambas lagunas se corrigen de forma distinta. Solo compara las dos listas: no puede saber si una firma es de la propia persona y no exige firma individual — si su institución admite una firma colectiva, indíquelo en el material o incluya la regla en `disabledRules`. |
| La 交底日期 es posterior a la 施工日期. ¿Es un error? | `SB-003` lo informa, y el mismo día cuenta como no posterior. La regla está limitada a `warn`: 第二十七条 da 施工前 como premisa temporal pero no enuncia esa comparación, así que el hallazgo es una pista para revisión — una instrucción añadida a mitad de obra por un peligro detectado después es legítimamente posterior y el registro debería decirlo. Una fecha que no se puede analizar se informa por sí sola en lugar de omitirse en silencio. |
| ¿Qué columnas debe rellenar el registro para pasar la comprobación? | `SB-001` lee `requiredFields`, que el paquete trae vacío, así que informa de `skipped` (未配置) en lugar de pasar. Cuando indique las columnas de su formulario, informa de cada una que falte o esté vacía — una cadena vacía cuenta como no rellenada — y no juzga si lo escrito en ellas es correcto. |
| El registro tiene columna de 被交底人 pero ningún sitio para el 专职安全员. | `SB-006` comprueba en la cabecera que haya un sitio para las tres partes — 交底人, 被交底人 y 专职安全员 — e informa de las que no tienen columna; los nombres de las columnas pueden sustituirse según su formulario. Sigue en `warn` porque el 第3.1.3条 de JGJ 59-2011 es una cláusula recomendatoria de evaluación (sus únicas disposiciones obligatorias, 第4.0.1、5.0.3条, fueron derogadas por el 住房和城乡建设部公告 2022 年第 164 号). Pregunta si el sitio existe, no si alguien firmó allí: eso es la pregunta de `SB-002`. |
| Los oficios que trabajaron en esa parte no figuran en la lista de 工种 de la instrucción. | `SB-005` compara los oficios que ejecutan el trabajo con la lista de 工种 del registro e informa de los que no aparecen. Está limitada a `warn` porque JGJ 59-2011 pide instrucciones 分部分项 pero no fija ninguna tabla obligatoria de correspondencia con los oficios, e informa de `skipped` cuando ni el material ni el parámetro `workTrades` nombran los oficios que trabajan, ya que no codifica ninguna lista de oficios. Solo compara nombres, de modo que 钢筋工 y 钢筋班组 cuentan como distintos, y no juzga si el contenido de la instrucción aborda ese oficio. |
| El registro no dice qué 工程部位 cubre ni quién dio la instrucción. | `SB-004` exige que la cabecera identifique el 工程部位 (`subject`) y el 交底人 (`briefer`), e informa del que falte; con `requireHeader` en false la regla no se ejecuta. Está limitada a `warn` porque el 第8.2.1条 de GB 50870-2013 no enuncia campos de cabecera: sin ellos el registro no puede mostrar quién instruyó a quién sobre qué parte, así que el hallazgo es una pista de trazabilidad y no la afirmación de que la cláusula se haya incumplido. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-safety-brief-check
dsh --profile <name> --dump-config | grep 'dsh-safety-brief-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/safety-brief-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-safety-brief-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-safety-brief-check contributors.
