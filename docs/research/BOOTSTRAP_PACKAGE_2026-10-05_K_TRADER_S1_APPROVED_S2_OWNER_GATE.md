№120. Recommended Filename

BOOTSTRAP_PACKAGE_2026-10-05_K_TRADER_S1_APPROVED_S2_OWNER_GATE.md

## Recovery Instructions

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

## Project

K-Trader — дослідження рівнів і торгових стратегій за матеріалами Герчика.

## Project Topology

LOCAL_PLUS_REMOTE

Логічний проєкт має GitHub, сервер K-Trader та локальні робочі копії. Для визначеного Next Task потрібен лише GitHub із документами; runtime та локальна копія не потрібні для відновлення.

## Current Phase

STRATEGY_OWNER_APPROVAL — S1 затверджена, S2 очікує погодження.

## Current Objective

Сформувати перевірювану методику рівнів і послідовно погодити стратегії перед їх реалізацією та історичним тестуванням, з обліком ризику, витрат і похибки виконання.

## Repositories

| Поле | Значення |
|---|---|
| Role | Project state, methodology, strategy specifications and implementation |
| Provider | GitHub |
| Owner | kolemasakar |
| Repository | K-Trader |
| Repository Full Name | kolemasakar/K-Trader |
| Default Branch | main |
| Active Recovery Branch | research/dual-market-historical-levels-v0-1 |
| Repository URL | https://github.com/kolemasakar/K-Trader |
| Recovery Criticality | REQUIRED |
| Responsibilities | Погодження стратегій, методика рівнів, дослідницький код та звіти |

K_AI, KGM та інші репозиторії не потрібні для Next Task; доступ до них не перевірявся і не припускається.

## Repository Access

| Поле | Значення |
|---|---|
| Repository Full Name | kolemasakar/K-Trader |
| Access Method | Підключений GitHub connector |
| Source Session Verification Status | VERIFIED: identity, main metadata, active branch, PR94 and required state documents |
| Read Capability | VERIFIED — metadata and files read |
| Write Capability | VERIFIED у цій сесії — documentation commits and non-forced branch update |
| Notes | Перевірити незалежно в новій сесії; credentials не передаються |

Стан гілки перед створенням цього пакета: **74fe67bf655037e0b39b2ee032c45685a0e9a1f5**. Коміт пакета є наступним документаційним комітом; отримати його з актуального ref, не вважати наведений SHA поточним head назавжди.

## Source of Truth Map

| Engineering Domain | Authoritative Source |
|---|---|
| Контрольна точка та пауза | GitHub active branch: PROJECT_CHECKPOINT_2026-10-05_S1_APPROVED_HANDOFF_PAUSE.md |
| Поточне затвердження S1 та стан S2 | GitHub active branch: GERCHIK_STRATEGY_OWNER_GATE_2026-10-04.json |
| Правила затвердженої S1 | GitHub active branch: GERCHIK_S1_REJECTION_APPROVED_2026-10-05.md |
| Історія пропозицій S2 | GitHub active branch: GERCHIK_STRATEGY_RULES_FOR_APPROVAL_2026-10-04.md |
| Книжкова відповідність S2 | Наданий PDF «Курс активного трейдера (Александр Герчик) (2).pdf», актуальне читання розділу пробою |
| Реальне поточне виконання коду, якщо стане потрібним | Код GitHub active branch; не висновки зі специфікації |
| Runtime, якщо стане потрібним | Безпосередня нова read-only перевірка сервера; для Next Task не потрібна |

## Source of Truth Precedence

- Поточні явні рішення власника мають пріоритет над попередніми пропозиціями.
- Зведена затверджена S1 має пріоритет над старими суперечливими пунктами журналу.
- Для S2 книжкові правила звіряти з PDF; числові доповнення подавати як пропозиції до погодження.
- Затвердження S1 не є затвердженням S2–S6.
- Код підтверджує реалізацію, а gate — погодження. Не підміняти одне іншим.
- Старі записи roadmap/пам'яті, включно з нібито остаточним погодженням усіх стратегій, не переважають актуальний gate.
- Конфлікт актуальних авторитетних джерел → RECOVERY_CONSISTENCY_WARNING, без прихованого виправлення.

## Current Status

- Власник затвердив S1 і сценарій05.10.2026 о05:20:43 Київ.
- S1 збережено окремим документом; контрольна точка й gate синхронізовані.
- S2–S6 у поточній редакції не затверджені.
- Код S1 ще не перенесений на остаточну специфікацію; бектест цієї редакції не проводився.
- Проєкт призупинено для переходу; пакет не запускає тести,deploy,merge чи ордери.
- PR94 перевірено open,draft,unmerged; base main,head research/dual-market-historical-levels-v0-1.
- Точні брокерські календарі/специфікації залишені відкритими за рішенням власника.
- Інженерний аудит рівнів дозволив перейти до стратегій, але незалежна наукова перевірка й прибутковість не підтверджені.

## Completed Work

- Затверджена S1: M5,підтверджений D1/W1+≥1посилювальна ознака за погодженою методикою.
- Напрям: два останні підтверджені максимуми/мінімуми; pivot2ліворуч/2праворуч; узгодження D1H1M5під час підходу.
- Піджаття3Close; вирівнювання строго далі. Зниження волатильності не є критерієм відбою.
- Запас≥60%ATR5відPза останнім завершенимM5Close.
- Шкала активності1,5/2; БПУ2≥2середніх20попередніхM5—пропуск.
- Вхід ліміт за30секдо закриттяБПУ2; Forexдопуск першого торкання2Pointбез проникнення.
- Стопи/люфти: золото3/.15,нафта.20/.03,Forex20/3Point,GBPUSD25/3Point; стопдо додаваннялюфту.
- Акції S=.002P,люфт.0004P,технічний пріоритет,відступ3Point,повний технічний стоп≤розрахункового.
- Ризик одиничної угоди0,5%депозиту з оціненими витратами; ціль3R,крипта1,5R.
- Прийнято округлення,витрати та два окремі наближені OHLCшляхи без доступу до майбутнього стануБПУ2.
- Канальні спеціальні правила відкладено до окремої стратегії. ПоточнаS6—пробійдіапазонуза трендом.
- Попередній аудит:2555D1+357W1,43кандидати,2912перевірокпричинності0розбіжностей,43/43верифікація свідків.
- Остання раніше підтверджена кодова перевірка: SHA6b2597ea498d347dde9b9c42acf91348d25d197d,CI37218743400success;491passed,4skipped,1warning,6subtests. Це історичний результат,не тест поточного документаційного head.

## Known Open Engineering Items

| Item | Status | Relevance |
|---|---|---|
| Правила S2 — пробій | OPEN | Безпосередня мета Next Task |
| Міграція коду S1 та її бектест | DEFERRED | Не виконувати в межах відновлення/погодження S2 |
| Брокерські календарі/числові специфікації | DEFERRED | Gerchik&Coреференс,не вимагати одного брокера/символів |
| Варіанти напрямку EMA20 та D1за рівнями | DEFERRED | Окремі майбутні порівняння |
| Торгівля в каналі | DEFERRED | Погоджується окремо,не підмінаS2/S6 |
| Рейтинг сили та незалежні мітки | OPEN | Дослідницький рейтинг не є доведеною якістю/ймовірністю |
| Нові ринкові роботи під час переходу | RELEASE_GATE | Пауза власника; сам recovery read-only |

## Next Task

**Після успішного read-only відновлення підготувати та подати в чат одну стратегію S2 — пробій від рівня — для погодження, звіривши її з книгою Герчика.**

Узгоджені S1 рішення використовувати лише як контекст; не переносити автоматично специфічні правила відбою на пробій. Показати передумови,модель входу,злам/скасування,параметри угоди та відкриті питання. Не реалізовувати і не запускати S2 до її погодження. Це єдине Next Task.

## Required Repository Resources

### kolemasakar/K-Trader

Branch: research/dual-market-historical-levels-v0-1.
Recovery Criticality: REQUIRED.

Мінімальні документи:
- docs/research/PROJECT_CHECKPOINT_2026-10-05_S1_APPROVED_HANDOFF_PAUSE.md
- docs/research/GERCHIK_STRATEGY_OWNER_GATE_2026-10-04.json
- docs/research/GERCHIK_S1_REJECTION_APPROVED_2026-10-05.md
- docs/research/GERCHIK_STRATEGY_RULES_FOR_APPROVAL_2026-10-04.md — розділи S2 та загальні актуальні рішення.

Метадані: repository identity/default branch,active ref,PR94.
Код/повнийroadmap/весьархів не потрібні для Next Task.

### Required Non-Repository Resource

Наданий PDF:
- Назва: «Курс активного трейдера (Александр Герчик) (2).pdf».
- Library ID: libfile_9166e8fbad10819187dc9b4421a44a51.
- File ID: file_00000000b690821083bdab750b1b2306.
-282сторінки.
- Завантажити тільки розділ пробою та посилання,потрібні для нього; початковий орієнтирс.125–127,додатковий розділстратегій післяс.234.
- Читання доступне в джерельній сесії; перевірити доступ заново. Відсутність PDFблокує книжкову звірку,не компенсувати припущеннями.

## Recovery Verification Requirements

- Перевірити REQUIREDGitHubidentity та default/activebranches незалежно.
- Прочитати мінімальні ресурси активної гілки й потрібний розділ PDF.
- Перевірити затвердженняS1,станS2,PR94та документаційну паузу.
- Застосувати Source of Truth Map; не приймати старі пропозиції за поточні рішення.
- Runtime revalidation: NOT_REQUIRED_FOR_NEXT_TASK. Якщо обсяг зміниться — нова перевірка обов'язкова.
- Повідомити користувачу,який доступ знайдено та які ресурси прочитано.
- Недоступне REQUIREDджерело → Recovery BLOCKED,Combined Verification FAILED.
- Combined Project Verification PASSлише за перевірених джерел,читання та узгодженості.
- Recovery read-only; жодних нових записів чи змінruntime.

## Recovery Status

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

Ці прапорці належать новій сесії; джерельна перевірка не заповнює їх наперед.

## Workspaces

| Path | Role | Git Repository / Branch | Source Session Verification | Required for Next Task |
|---|---|---|---|---|
| /workspace/scratch/452b7d5827aa/K-Trader | Часткова локальна копія документів | Не git clone; файли activebranch | Читання/запис документів підтверджено | No |

Шлях може зникнути. Відновлювати з GitHub,не вимагати цей локальний каталог.

## Runtime / Infrastructure

K-Trader має продуктивний сервер; його стан у цьому етапі не перевірявся.
Recovery Criticality: REFERENCE_ONLY.
Requires Revalidation: YESякщоruntimeстане потрібним.
Endpoint/credentials/поточні jobsне передаються. Runtimeне потрібен для погодженняS2.

## Deployment Boundary

- Active Test Target: майбутні офлайн історичні дослідження,не запущені.
- Production Target: K-Traderprod,без змін у цій сесії.
- Public Release Target: не визначено/не дозволено.
- Allowed Recovery Target: GitHubactivebranchта наданийPDFread-only.
- Prohibited Targets: deploy,merge,реальна торгівля,ордери; HP-OMEN/K_AI/MT4машина прямо чи опосередковано.
- FREE_ONLY. Не додавати платні сервіси/дані без нового рішення.

## Pull Request State

Repository:kolemasakar/K-Trader.
PR94:https://github.com/kolemasakar/K-Trader/pull/94.
Source-session verified:open,draft=true,merged=false,base=main,head=research/dual-market-historical-levels-v0-1.
Recovery rule:revalidate before use.

## Temporary Artifact Handling

- PERSISTENT: GitHubapprovedS1,checkpoint,gate,журнал,цей пакет.
- TEMPORARY_BUT_ACTIVE: локальні дзеркала,не REQUIRED.
- Жодні temporary cleanedартефакти не використовуються як джерела.

## Combined Recovery Result

Очікуваний результат нової сесії:

```text
Repository kolemasakar/K-Trader: VERIFIED
Provided Gerchik PDF: VERIFIED
Runtime: NOT_REQUIRED_FOR_NEXT_TASK
Cross-Source Consistency: PASS
Combined Project Verification: PASS
Recovery: COMPLETE
```

Це умови майбутнього результату,не твердження про вже виконане відновлення нового чату.
