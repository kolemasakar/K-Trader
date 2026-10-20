# K-Trader — контрольна точка перед переходом, 20.10.2026

Статус: DOCUMENTATION_CHECKPOINT / REAL_S1_ACCEPTANCE_PENDING.
Власник доручив зафіксувати проєкт і синхронізувати документацію; генератор переходу надасть окремо. Нові прогони, merge і deployment у межах цієї фіксації не виконуються.

## Репозиторій та перевірки
- Repo: https://github.com/kolemasakar/K-Trader
- Гілка: `research/approved-strategies-readiness-20261011`.
- Draft PR96: https://github.com/kolemasakar/K-Trader/pull/96 — на момент перевірки відкритий, не merged.
- Перевірений remote code/docs baseline: `2d69ac1554b95d246a96d0057561c9e04a968c61`.
- CI run394: https://github.com/kolemasakar/K-Trader/actions/runs/38109252212 — SUCCESS; Python3.12/3.14, Docker amd64/arm64, canonical merge gate PASS.
- Локальна перевірена реалізація: `b5bc7eb5a9101749ab8f25eb509cc3b528212e58`, 333 PASS; цільові approved-model/MT4/S1 перевірки 55 PASS. Це попередні результати, не нове тестування 20.10.
- Код на GitHub опубліковано через конектор; локальні й remote commit SHA відрізняються через спосіб створення комітів. Дерево перевіреної реалізації збіглося: `fc5c0f317b12efa116663a179c6619d6082206fc`.

## Реалізація та чинні правила
- Новий контур S1–S5: `approved_models`, `approved_scheduler`, `approved_execution`, `level_admission`, `research_risk`; scripts `prepare_approved_backtest.py`, `run_approved_backtest.py`, `verify_approved_smoke.py`.
- Позначення за затвердженими документами: S1 відбій; S2-А/Б пробій; S3 пробій із ретестом; S4 однобарний хибний пробій; S5-А/Б багатобарний хибний пробій. Канал — окрема модель. Перекази з інших проєктів не змінюють ці позначення.
- Реалізація перевірена fixtures і synthetic smoke; повне приймання на реальній історії ще не завершене.
- A/B: O-H-L-C та O-L-H-C; сценарні лінійні сегменти, префіксна причинність. Це не відновлення фактичного тикового порядку всередині M5.
- Старий strategy/benchmark-код заморожений і виключений із нового виконання; старі результати не використовуються. Затверджені ATR5v2/детектори кандидатів/MT4-читач повторно використані за чинним протоколом.
- Умовний broker wall clock дозволений для алгоритмічної роботи. Непідтверджена точність сесій не блокує алгоритмічний прогін.
- FREE_ONLY, ізоляція research, незмінний source. Production/trading endpoints не змінювати. HP-OMEN не використовувати для K-Trader без окремого явного дозволу; наявна серверна копія корпусу — дозволене джерело.

## Дані й виконана підготовка
- Frozen source container: `/data/kif_research/external/kai_mt4_20261009`; host: `/opt/k-trader/data/kif_research/external/kai_mt4_20261009`.
- За попереднім аудитом: 280 активів, 840 канонічних D1/H1/M5 серій, 3 881 201 свічка; 840/840 content hashes/counts PASS. Два додаткові normalized acquisition-файли не канонічні.
- Дозволений маршрут: SentinelX → `sudo docker exec k-trader-ktrader-1 python …`, default UID1002. Не розширювати sudo/права доступу.
- Попередня ізоляція: `/tmp/ktrader-approved-20261011`; результати: `/data/research/approved-preparation-20261011`. Landlock/RLIMIT self-test source_read=true/source_write_denied=true PASS.
- `/tmp` може не зберегтися; на початку нового виконання перевірити наявність коду/результатів і hash, відновити з репозиторію за потреби. Живий стан сервера 20.10 не перевірявся.
- ACHC.us: D1 2175 / H1 2061 / M5 2198; кандидати 68 D1 + 12 W1; ATR5v2 ≈1,016; вибіркові prefix checks 6/6 PASS. Це попередній preparation report, не завершений market backtest.
- Незалежно допущених рівнів у preparation report: 0/80; market_trades=null. Synthetic ARM64 S1 A/B smoke PASS, детермінізм PASS; це не ринкові результати.

## Отримана публічна специфікація ACHC.us
Snapshot від 13.10: [ACHC_US_GERCHIK_PUBLIC_SPEC_20261013.json](ACHC_US_GERCHIK_PUBLIC_SPEC_20261013.json).
Офіційна сторінка: https://gerchik.co/en/for-trader/trading-terms/list-of-assets
API: POST https://po-api.gerchik.co/api/get-symbols-info-by-groups з групою US Stocks.
- Точний symbol ACHC.us; Acadia Healthcare Company, Inc.; tick_size=0.01 USD, tick_value=0.01 USD, contract_size=1; volume min=1/max=10000/step=1; currency_profit=USD.
- Snapshot SHA256 повної відповіді: `801400c5cd67d1e757cc02a84d542436551f4eaaae4a639815b0b679cb8a8e18`.
- Point і Digits відсутні. Tick не підміняє Point. Це snapshot сайту, не експорт з конкретного MT4/MT5 server/account.
- Історична незмінність параметрів, точний часовий пояс сесій і повний cost profile не підтверджені; жоден admission/profile flag не підвищено до true.
- Поточний tick уже знайдено; формулювання «tick узагалі відсутній» застаріле. В історичному KAI-корпусі відповідних метаданих не було.

## Борги й наступна послідовність
1) Підтвердити Point/Digits ACHC.us та історичну застосовність геометрії ціни; якщо потрібне сценарне припущення — зафіксувати окреме рішення власника, не позначати його історично доведеним фактом.
2) Незалежно перевірити D1/W1 witness-пакети за погодженими правилами: тип, посилення, source/evidence ID, причинний known_at. Не автоматично ставити CONFIRMED і не вигадувати reviewer.
3) Застосувати допуски та verified profile; виконати реальний S1 A/B на ACHC.us через read-only source isolation; повторити й порівняти детермінізм, перевірити заявки/fills/cancellations/SL/TP/censoring.
4) Прийняти реальний lifecycle report, потім S2-А/Б → S3 → S4 → S5-А/Б → канал та інші класи активів/незалежна контрольна вибірка.
5) Без перевірених contract/cost даних дозволений лише явно позначений price/R звіт; net/грошовий результат лишається невідомим. Знайдена поточна специфікація сама не доводить історичні витрати.

Чинний детальний протокол: [APPROVED_BACKTEST_PROTOCOL_20261011.md](APPROVED_BACKTEST_PROTOCOL_20261011.md). Підготовка переходу не означає завершення допуску рівнів чи ринкового S1-прогону. Генератор ще не отримано.
