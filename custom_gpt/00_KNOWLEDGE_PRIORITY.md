# K-Trader Knowledge Priority

Status: ACTIVE KNOWLEDGE-GOVERNANCE FILE

## PURPOSE
Цей файл визначає пріоритет джерел знань і не відключає чинні можливості K-Trader. Проєкт ще перебуває в активній розробці, тому historical Knowledge не можна ані автоматично робити canonical, ані безпідставно відкидати.

## CURRENT TRADING DECISION PRIORITY
1. чинна системна інструкція;
2. актуальні явні рішення користувача;
3. K-Trader Action/API + deployed runtime/config;
4. canonical GitHub repo;
5. current research;
6. historical Knowledge;
7. external/general knowledge.

## STRATEGY / RESEARCH PRIORITY
1. чинна системна інструкція;
2. актуальні явні рішення користувача;
3. accepted canonical repo/checkpoints/specifications;
4. preregistered research + reproducible evidence;
5. runtime evidence;
6. historical Knowledge;
7. external/general knowledge.

Вищий пріоритет перекриває нижчий лише в конкретній точці конфлікту.

## HISTORICAL / RESEARCH REFERENCE
Файли зберігаються без перейменування:
- `01_levels_rules.pdf`
- `02_ATR_and_range.pdf`
- `03_money_management.pdf`
- `04_position_sizing.pdf`
- `K_Trader_KB_VSA_ATR_SysInstrAddition1.md`

Їх дозволено використовувати для:
- hypothesis generation;
- feature discovery;
- пояснення market structure, levels, ATR, VSA, risk;
- порівняння з current research;
- відновлення попередньої логіки проєкту.

Вони НЕ є автоматично чинними торговими правилами.

## REVALIDATION REQUIRED
Без повторної перевірки не переносити як hard gate:
- старі `ATR_used_pct` thresholds;
- fixed percentage/pip/cent stops;
- old money-management percentages;
- mandatory VSA/volume filters;
- old timeframe/holding assumptions.

## CONFLICT RULE
Якщо historical reference суперечить новішому canonical/research evidence:
- не застосовувати старе правило мовчки;
- зберігати його як hypothesis/reference;
- документувати матеріальний conflict;
- promotion лише через preregistered version + causal backtest/walk-forward + fresh OOS/prospective evidence;
- holdout не використовувати для tuning.

## PRESERVE CURRENT FUNCTIONALITY
До появи експериментально валідованої робочої версії:
- не вимикати чинні API/Actions/workflows через зміну research-пріоритетів;
- не видаляти робочий компонент лише тому, що його немає в historical Knowledge;
- не замінювати server decision локальною реконструкцією GPT;
- не змінювати production/risk/execution/deployment без явного дозволу;
- вести strategic changes versioned/audited.

## STATUS
Перелічені файли мають статус:

`HISTORICAL / RESEARCH REFERENCE`

Вони залишаються корисними джерелами гіпотез, але не можуть автоматично перекривати current canonical K-Trader state.
