# Recommended Filename

`BOOTSTRAP_PACKAGE_2026-10-20_K_TRADER_S1_INPUT_ADMISSION.md`

# Recovery Instructions

```text
Recovery Instructions

1. Read the entire Bootstrap Package.
2. Treat it as the authoritative entry point for project recovery.
3. Do not reconstruct previous chat history.
4. Do not make architectural assumptions.
5. Inspect Project Topology, Repositories, Repository Access, Source of Truth Map, Source of Truth Precedence, and any Workspaces or Runtime / Infrastructure sections.
6. Identify the Next Task and derive the minimum required components, sources and resources.
7. Check repository access independently for every REQUIRED repository.
8. For every accessible REQUIRED repository, verify provider, owner, repository name, full name, Default Branch and Active Recovery Branch when specified.
9. Use Active Recovery Branch for recovery when specified.
10. Stop recovery for a source if its identity does not match the Bootstrap Package.
11. Inform the user that repository access was found and identify each verified repository and branch.
12. Read only the Required Repository Resources needed for the Next Task.
13. Inform the user exactly which resources were read, grouped by repository.
14. If a REQUIRED source is unavailable, denied, incomplete or incorrectly identified, report the limitation, request only the minimum action required to restore access, use file upload only as fallback, and do not declare Recovery Complete.
15. OPTIONAL and REFERENCE_ONLY sources do not block recovery unless the Next Task makes them required.
16. Use the Source of Truth Map for domain authority and Source of Truth Precedence for conflicts.
17. If an authoritative implementation repository is accessible, do not infer current implementation behavior from documentation; read the implementation.
18. Do not infer project approval, roadmap or acceptance state solely from implementation code when an authoritative project-state source is available.
19. Revalidate REQUIRED volatile runtime/infrastructure state.
20. Do not assume source-session jobs, sessions, deploy IDs, signed URLs, locks, leases, queues or other ephemeral state remain current.
21. Perform a cross-source consistency check for domains required by the Next Task.
22. If authoritative sources disagree, report RECOVERY_CONSISTENCY_WARNING. Do not silently reconcile conflicting state.
23. Recovery is read-only. Do not modify repositories, workspaces, deployments or runtime state unless the user explicitly authorizes a write operation.
24. Report Project Topology, access status for each REQUIRED source, verified identities and branches, resources read, runtime verification, consistency result, unavailable REQUIRED resources, Combined Project Verification and Recovery status.
25. Combined Project Verification is PASS only when every REQUIRED source and verification condition for the Next Task has passed.
26. Continue from the Next Task only after Combined Project Verification is PASS and Recovery is complete.
```

# Project

K-Trader — дослідження стратегій на frozen історії KAI/MT4; виконання торгових угод належить окремому K_AI, до поточної задачі не входить.

# Project Topology

`LOCAL_PLUS_REMOTE`

# Current Phase

`S1_INPUT_ADMISSION`

# Current Objective

Завершений, перевірений S1-прогін на реальній історії ACHC.us після доказового допуску цінової геометрії та D1/W1 рівнів.

# Repositories

| Field | Value |
|---|---|
| Role | Project state, approved rules, implementation, evidence |
| Provider | GitHub |
| Owner | kolemasakar |
| Repository | K-Trader |
| Repository Full Name | kolemasakar/K-Trader |
| Default Branch | main |
| Active Recovery Branch | research/approved-strategies-readiness-20261011 |
| Repository URL | https://github.com/kolemasakar/K-Trader |
| Recovery Criticality | REQUIRED |
| Responsibilities | Rules, S1–S5 research implementation, admission gates, reproducible reports, checkpoints |

Інших репозиторіїв для Next Task не потрібно. Не залучати K_AI/KGM/KRC та не переносити їхні правила стратегій у K-Trader.

# Repository Access

| Repository Full Name | Access Method | Source Session Verification Status | Read Capability | Write Capability | Notes |
|---|---|---|---|---|---|
| kolemasakar/K-Trader | Connected GitHub tools | VERIFIED 20.10.2026 | YES: metadata, branch files, PR, CI | YES: tree/commit/ref publication | CLI push без авторизації не працював; конектор успішний. Не передавати credentials; повторно перевірити в новій сесії. |

# Source of Truth Map

| Engineering Domain | Authoritative Source |
|---|---|
| Current project state / acceptance | Active branch: docs/research/PROJECT_CHECKPOINT_20261020_PRE_TRANSITION.md |
| Execution and admission policy | Active branch: docs/research/APPROVED_BACKTEST_PROTOCOL_20261011.md |
| Approved S1 rules | Active branch: docs/research/GERCHIK_S1_REJECTION_APPROVED_2026-10-05.md |
| Actual profile/admission enforcement | Active branch: scripts/run_approved_backtest.py and src/ktrader/level_admission.py |
| Recorded public broker metadata | Active branch: docs/research/ACHC_US_GERCHIK_PUBLIC_SPEC_20261013.json |
| Terminal-specific Point/Digits and historical validity | Explicit broker/terminal evidence with provenance; currently NOT ESTABLISHED |
| Frozen candle content, if later needed | Read-only K-Trader server corpus, not local chat memory |

# Source of Truth Precedence

- Нові явні рішення власника мають пріоритет над попередніми обмеженнями у відповідному домені; не припускати неотриманих рішень.
- Checkpoint20.10 уточнює стан, протокол11.10 визначає правила; історичні частини roadmap не скасовують їх.
- Для поведінки програми читати код; для приймання/затвердження — чинні документи, не сам факт існування коду.
- Вебsnapshot доводить отримані поточні значення на 13.10, але не historical constancy та не конкретний MT4/MT5 server/account.
- Tick size не є доказом Point. Розрядність CSV/OHLC не є достатнім доказом специфікації термінала.

# Current Status

- Remote checkpoint commit: `bb147abab7d006aa4b98f5bb2d615b9b6b3d0e45`; read-back PASS; local/remote tree `75f7f66f32e8aeeb58df930d9a7de9d1fdcff0bd` збіглося.
- CI run395 на цьому commit завершено SUCCESS: https://github.com/kolemasakar/K-Trader/actions/runs/39350104608. Це перевірений checkpoint до додавання bootstrap-файлу.
- PR96 відкритий draft, не merged; main не є recovery branch.
- Новий S1–S5 contour реалізований і перевірений fixtures; реальний S1 market acceptance не завершений.
- Preparation ACHC.us: 68 D1 +12 W1 кандидатів; допуск 0/80, market_trades=null, не «нуль угод після завершеного бектесту».
- Поточний public tick ACHC.us=0.01 USD знайдено; Point/Digits і застосовність до історії не підтверджені.
- Умовний broker wall clock дозволений для алгоритмічної роботи; невідома точність сесій не є блокером.
- Старий код заморожений і виключений із нового виконання; старі benchmark-результати не враховуються.

# Completed Work

- Інтегровано approved_models, approved_scheduler, approved_execution, level_admission, research_risk; підготовчі й replay scripts; W1 known_at без backdating; канонічні acquisition manifests.
- Раніше виконано 333 локальні тести PASS, 55 цільових PASS; ARM64 synthetic S1 A/B і повторний детермінізм PASS. Synthetic не є ринковим результатом.
- Реальна підготовка11.10: D1=2175/H1=2061/M5=2198; ATR5v2≈1.016; 6/6 вибіркових prefix checks. Не повний незалежний аудит.
- Публічний snapshot Gerchik13.10: ACHC.us, Acadia Healthcare Company, Inc.; tick_size=0.01, tick_value=0.01, contract_size=1; volume min1/max10000/step1; profit currency USD. Сесії не конвертувати в UTC без доказу timezone.
- Збережено snapshot з provenance і response SHA256; синхронізовано checkpoint, roadmap, current state, protocol у GitHub.

# Known Open Engineering Items

| Item | Status | Relevance |
|---|---|---|
| Point/Digits ACHC.us | OPEN | Відступ SL на 3 Point, точність геометрії |
| Historical validity / terminal-server binding | OPEN | Поточна вебспецифікація не доводить минулі налаштування |
| Independent D1/W1 admission | BLOCKED | 0/80; потрібні справжні review, source/evidence ID, causal known_at і посилювальні ознаки |
| Real S1 A/B deterministic lifecycle acceptance | RELEASE_GATE | Немає прийнятого market replay; fixtures недостатньо |
| Verified historical contract/cost profile | DEFERRED | Для monetary/net; явний price/R звіт не вимагає вигаданого net |

# Next Task

Провести доказовий аудит цінової геометрії ACHC.us для S1: перевірити збережену специфікацію та фактичні вимоги profile gate, знайти підтвердження Point/Digits і історичної застосовності у дозволених джерелах; результат — підтверджений профіль або точний перелік відсутніх доказів. Не прирівнювати tick до Point, не вигадувати historical verification і не запускати бектест до відповідного допуску. Recovery read-only; цей запис не є новим дозволом на writes після відновлення.

# Required Repository Resources

Repository: `kolemasakar/K-Trader`.
Branch: `research/approved-strategies-readiness-20261011`.
Recovery Criticality: `REQUIRED`.

- State: docs/research/PROJECT_CHECKPOINT_20261020_PRE_TRANSITION.md.
- Policy: docs/research/APPROVED_BACKTEST_PROTOCOL_20261011.md.
- Broker evidence: docs/research/ACHC_US_GERCHIK_PUBLIC_SPEC_20261013.json.
- S1 approved rules: docs/research/GERCHIK_S1_REJECTION_APPROVED_2026-10-05.md.
- Profile implementation: scripts/run_approved_backtest.py.
- Admission implementation: src/ktrader/level_admission.py.
- Point/tick use: src/ktrader/approved_models.py; relevant assertions tests/test_approved_models.py.
- Metadata: repository identity/default branch/active branch HEAD; PR96 when assessing acceptance state.

Не читати весь архів чи всі історичні benchmark-документи. Не додавати джерела інших проєктів за схожістю назв.

# Recovery Verification Requirements

- Перевірити identity GitHub/kolemasakar/K-Trader, default main, active recovery branch та її поточний HEAD.
- Прочитати мінімальні ресурси вище; повідомити користувачу точний перелік і доступ.
- Застосувати доменні authoritative sources; порівняти snapshot, S1 rules і фактичні gate/code requirements.
- Не вважати historical flags підтвердженими лише через наявність current tick. За конфлікту — RECOVERY_CONSISTENCY_WARNING.
- Для Next Task runtime не обов'язковий: використовувати repo evidence і відкриті джерела. Якщо обраний метод потребує конкретного термінала/сервера, він стає REQUIRED і потребує нового підтвердження доступу; недоступність не обходити.
- Відсутній REQUIRED repository/resource або нерозв'язана суперечність: Combined Project Verification=FAILED, Recovery=BLOCKED; не оголошувати повне відновлення.
- Усі REQUIRED джерела/умови перевірено: Combined Project Verification=PASS, Recovery=COMPLETE; тільки тоді перейти до Next Task.

# Recovery Status

```text
[ ] Bootstrap Loaded
[ ] Project Topology Identified
[ ] Required Sources Identified
[ ] Required Repository Access Checked
[ ] Required Repository Identities Verified
[ ] Required Resources Loaded
[ ] Runtime Revalidated If Required
[ ] Cross-Source Consistency Checked
[ ] Recovery Verification Reported
[ ] Recovery Complete
```

# Workspaces

- `/workspace/scratch/5458615f1954/K-Trader-implementation`: source-session git checkout; branch research/approved-strategies-readiness-20261011. Local commit SHA відрізняються від connector-created remote SHA; звіряти дерева/вміст. OPTIONAL, новій сесії шлях не гарантовано доступний; GitHub — recovery entry.

# Runtime / Infrastructure

- Provider: Oracle OCI; service/host k-trader-prod-vnic; SentinelX host ID `host_8c63c46648154724`; environment K-Trader isolated research.
- Access observed previously: SentinelX → `sudo docker exec k-trader-ktrader-1 python …`, default UID1002; не розширювати sudo/привілеї.
- Host corpus: `/opt/k-trader/data/kif_research/external/kai_mt4_20261009`; container `/data/kif_research/external/kai_mt4_20261009`.
- Historical inventory: 280 assets, 840 canonical D1/H1/M5 series, 3,881,201 candles; previous hash/count verification840/840 PASS. Два додаткові normalized acquisition-файли виключені.
- Responsibility: frozen candles for later replay. Recovery Criticality: REFERENCE_ONLY for current Next Task.
- Source Session Verified At: preparation/isolation11.10, public website query route13.10; live server/corpus state20.10 NOT REVALIDATED. Requires Revalidation: YES before runtime use.

# Deployment Boundary

- Active Test Target: isolated research only, immutable source.
- Production Target: running K-Trader service; не deployment target цього пакета.
- Public Release Target: none; PR draft, no merge/deploy authorization implied.
- Allowed Recovery Target: read-only repository/open broker metadata; runtime only after explicit revalidation within existing scope.
- Prohibited Targets: HP-OMEN for K-Trader without separate explicit authorization; K_AI broker dispatch; KGM/KRC infrastructure; changing source candles; paid services (FREE_ONLY).

# Ephemeral / Expiring Resources

| Identifier | Type / classification | Source-session state | Recovery Rule |
|---|---|---|---|
| /tmp/ktrader-approved-20261011 | Isolated code; TEMPORARY_BUT_ACTIVE at last use | Used11.10; not checked20.10; may expire | Do Not Assume Current; verify before reuse |
| /data/research/approved-preparation-20261011 | Result directory; PERSISTENT by design | Prior reports/witness panels recorded; live existence unverified20.10 | Do Not Assume Current; verify before reuse |
| GitHub checkpoints and spec snapshot | PERSISTENT | Published/read-back20.10 | Revalidate branch/current contents |

Втрата /tmp не означає втрати canonical code: відновлювати з GitHub лише після дозволу на необхідні writes. Не переносити sessions, signed URLs чи credentials.

# Pull Request State

Repository kolemasakar/K-Trader; PR96 https://github.com/kolemasakar/K-Trader/pull/96; source-session state OPEN; Draft YES; Base main; Head research/approved-strategies-readiness-20261011; Merged NO. Revalidate before any acceptance/merge statement.

# Cross-Source Consistency

- Repo checkpoint20.10 і broker snapshot13.10 узгоджені: поточний tick знайдено, Point/Digits/historical validity не доведені.
- Preparation11.10 залишається історичним звітом 0/80; публічна специфікація не переписує його admission results автоматично.
- Номенклатура за затвердженими файлами K-Trader: S1 відбій, S2 пробій, S3 пробій-ретест, S4 однобарний хибний пробій, S5 багатобарний хибний пробій, канал окремо. Інші перекази не authoritative.
- За нової суперечності: RECOVERY_CONSISTENCY_WARNING; не редагувати джерела під час recovery.
