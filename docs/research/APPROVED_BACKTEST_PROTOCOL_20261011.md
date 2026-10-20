## Завершений умовний S1 — рішення власника 20.10.2026

Власник погодив окремий інженерний режим Point=0.02/tick=0.02 (попередня пропозиція0.01 не застосовується). Виконано прямий S1 A/B на ACHC.us із11 provisional рівнями;0 заявок уA іB; повторний повний прогін ідентичний. Source hashes до/після збіглися, Landlock self-test PASS;366 локальних тестів PASS. Historical/independent-human verification не заявляється; цей дозвіл змінює вимоги лише окремого engineering mode. [Повний результат і межі](ACHC_S1_ENGINEERING_ACCEPTANCE_20261020.md).

## Актуальне виконання — 20.10.2026

Тестовий шлях переведено на прямий `approved_replay` без імпорту scheduler, із code hashes та умовними M5-координатами, без реальних сесій. Повний локальний набір: 342 PASS. Для 80 рівнів виконано окрему перевірку форми: 63 SHAPE_PASS_REVIEW_PENDING, 13 QUALITATIVE_REVIEW_REQUIRED, 4 POLICY_UNAPPROVED. Це не незалежний допуск; admitted=0. Point/Digits та історична геометрія залишаються непідтвердженими. Деталі: [звіт](S1_TEST_PATH_REVIEW_20261020.md).

Нижче збережено попередні часові зрізи; твердження про ще невиконану адаптацію scheduler є історичними.

# Чинний протокол підготовки S1–S5 — 11.10.2026

Статус: PREPARATION_EXECUTED / IMPLEMENTATION_REQUIRES_REAL_ADMISSION_ACCEPTANCE.
Підстава: доручення власника після аудиту, 11.10.2026: завершити допуск D1/W1, реалізацію S1–S5, підготовку бектестів; старий код заморозити; старі benchmark-результати не враховувати; умовні часові координати допустити для роботи.
Цей протокол має пріоритет над історичними баровими/next-Open/1R правилами, документаційними паузами та старими roadmap milestones.

## Код та межі
- База: PR95 `63214fc1becb83be29adc3c10e3cb56ad8bd9153`.
- Авторитетні правила: комплект S1–S5/канал від 11.10; специфікації й реєстр із дослідницької гілки імпортовані в одну реалізаційну гілку.
- Новий контур: `approved_models.py`, `approved_scheduler.py`, `approved_execution.py`, `level_admission.py`, `research_risk.py`, `prepare_approved_backtest.py`, `run_approved_backtest.py`.
- Повторно використано затверджений ATR5 v2, нові Gerchik-кандидатні детектори та MT4-читач. Legacy strategy/pivot/BOS-proxy/benchmark-алгоритми не входять до нового виконання. Автоматичні архетипи не підміняють незалежний допуск.
- Production/API/order endpoints не змінювались; результати тільки research. Старий код зафіксовано як виключений із нового контуру, без його видалення.

## Дані та час
Frozen source: `/data/kif_research/external/kai_mt4_20261009`.
840 серій за авторитетними acquisition manifests; два додаткові acquisition-файли не включаються. Перевіряти candle-content SHA256, не хеш заголовка+свічок; перевіряти кількість та OHLC.
Умовний broker wall clock дозволений для алгоритмічної роботи. UTC/session accuracy не заявляти. Не вводити вигаданого календаря/щоденного завершення; календарні перевірки маркувати NOT_VERIFIED. Це не блокер алгоритмічного запуску.
W1 відомий лише після першого завершеного D1 наступного тижня за поточним консервативним адаптером; його known_at не переноситься на попередній тиждень.

## Допуск рівнів
- Exact originating D1/W1 High/Low, одна primary type, причинні witness indices; AMBIGUOUS не проходить.
- Верифіковані historical tick і незалежний review із source hash/evidence ID/known_at.
- Щонайменше одна підтверджена посилювальна ознака за чинною методикою; score>=60 не є заміною.
- Не вигадувати reviewer, історичну доступність чи Point/tick із числа десяткових знаків котирування.
- Пакет для перевірки: `level_review_panels.json`, із реальними witness rows, без автоматичного CONFIRMED.

## Виконання і звіт
- Фіксовані окремі A=O-H-L-C та B=O-L-H-C; лінійні сегменти; події точних перетинів і T−30s; поточний префікс, без фінальних майбутніх extrema.
- S1/S3 — ліміти; S2/S4/S5 — програмний trigger → causal SL → sizing. S2-Б має frozen range/окремий entry; один вибраний варіант у одному прогоні, без сумування дубльованих заявок.
- Стопи, напрями, activity і скасування — за моделями. S3/S5-Б не мають історичного довільного 6-барного ліміту. Портфельних обмежень не додано.
- Канал: окрема модель; 80% від entry, TP всередині, ATR60 не перевіряється.
- Грошовий ризик: 0,005 Deposit, округлення volume вниз, підтверджений contract/cost profile. Невідомі лоти/витрати/net залишаються null.
- Відкрита позиція на кінці історії — CENSORED; немає вигаданого exit. Adverse SL gap — фактичний модельований Open; favorable TP gap — за target.
- Фіксувати source/evidence/profile/code hashes, конкретний model/variant, сценарій, pending/fill/cancel/exit, unknown fields, фактичну глибину.
- Старі benchmark-дані не читати й не включати у жодний висновок нового прогону.
- Перший engineering replay не є незалежним holdout. Подальші discovery/validation/holdout — за freeze від KAI, коротка історія окремо; touched samples не видавати за untouched.

## Фактично виконано
- Відновлено дозволений `sudo docker exec k-trader-ktrader-1 python …`, default UID1002; не змінено sudo/права SentinelX.
- Ізольований код у `/tmp/ktrader-approved-20261011`; Landlock/RLIMIT launcher із PR95; результат `/data/research/approved-preparation-20261011`.
- Landlock self-test: source_read=true / source_write_denied=true / exit0.
- Реальна підготовка ACHC.us: D1=2175/H1=2061/M5=2198; D1 candidates=68/W1=12; ATR5 v2≈1,016.
- Вибіркові real-prefix checks: 6/6 PASS. Не називати це повним незалежним аудитом усіх архетипів.
- 55 цільових перевірок PASS (approved_models, MT4, S1 replay): нові моделі/сценарії та відповідні MT4/S1 регресії. Повний локальний набір: 333 PASS. Ізольований ARM64 synthetic S1 A/B smoke та повторення: PASS. CI run394 на remote `2d69ac1554b95d246a96d0057561c9e04a968c61` SUCCESS; не видавати synthetic tests за real strategy backtest.
- Реальний допуск: 0/80; усі 80 мають HISTORICAL_TICK_UNVERIFIED та INDEPENDENT_REVIEW_MISSING.
- Даних Point/tick/contract/cost/review у перевіреному KAI-корпусі не знайдено. Підготовка виконана, повний market S1 replay заблокований; trades=null, не 0 market trades.

## Наступний рубіж
1) Завершити незалежну розмітку підготовлених D1/W1 witness-пакетів і отримати верифікований історичний профіль символу.
2) Застосувати review/metadata до admission; запустити S1 на ACHC.us у тому самому ізольованому маршруті й двічі перевірити детермінізм.
3) Прийняти реальний lifecycle report; потім послідовно S2-А/Б → S3 → S4 → S5-А/Б → канал; тестові fixtures не замінюють цей acceptance.

## Фінальна локальна ревізія
- Подія досягнення наступного сильного рівня S5-Б передається у lifecycle до повернення; сценарії A/B мають регресійні перевірки.
- Первісну публікацію відхилила автоматична перевірка дозволів; власник згодом явно дозволив публікацію. Гілку `research/approved-strategies-readiness-20261011` опубліковано через GitHub-конектор; draft [PR96](https://github.com/kolemasakar/K-Trader/pull/96), CI run394 завершено SUCCESS (Python3.12/3.14, Docker amd64/arm64, canonical merge gate).
- Опубліковане дерево коду `fc5c0f317b12efa116663a179c6619d6082206fc` точно відповідає локально перевіреній ревізії `b5bc7eb5a9101749ab8f25eb509cc3b528212e58`. Початковий remote commit: `01b596504a8df2fca945add1ed53707d478e827c`; наступне оновлення стосується тільки цього протоколу.

## Доповнення станом на 20.10.2026
- Поточний публічний tick ACHC.us знайдено 13.10 на офіційному API Gerchik & Co: 0,01 USD; tick value 0,01 USD; contract size 1. [Snapshot](ACHC_US_GERCHIK_PUBLIC_SPEC_20261013.json). Point/Digits відсутні; історична застосовність і конкретний terminal server не підтверджені. Не підміняти Point тиковим кроком і не ставити historical verification=true.
- Незалежний допуск рівнів та реальний market S1 acceptance не завершені. Відсутність метаданих у KAI-корпусі не означає відсутності знайденої поточної вебспецифікації.
- Зафіксовано [контрольну точку перед переходом](PROJECT_CHECKPOINT_20261020_PRE_TRANSITION.md); вона уточнює поточний стан без зміни погоджених правил моделей. Генератор очікується окремо.
