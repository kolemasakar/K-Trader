# K-Trader — аудит проєкту, статус і подальший роадмап
Дата: 11.10.2026, Київ. Перевірка після завершення канального погодження.
Статус: REPOSITORY_AND_READ_ONLY_RUNTIME_AUDIT_COMPLETED.
Рекомендації нижче — запропонований порядок руху, а не нове погодження торгових правил чи production.

## Висновок і наше місце
Погодження поточних тестових специфікацій S1–S5, їхніх варіантів і канальної стратегії завершено; S6 поглинуто S2-Б.
K-Trader має працюючий read-only backend, дослідницьку базу та доступний багатокласовий корпус історії. Повна відповідність нового набору стратегій виконуваному коду та завершений бектест цих редакцій не підтверджені.
Наш поточний рубіж: **між завершеною формалізацією правил і прийманням інтегрованого виконання першої стратегії**.
Основне завдання — використати наявні рівні/ATR5/адаптери, завершити інтеграцію та показати відтворюваний перший S1-прогін. Переписування вже наявних алгоритмів не є необхідним шляхом.

## Мета та межі проєкту
Мета K-Trader: отримувати й перевіряти дані, знаходити причинно доступні рівні/моделі, досліджувати їх на історії, розраховувати вхід/SL/обсяг/TP та видавати доказові read-only результати.
Найближча дослідницька мета: перевірити роботу погоджених алгоритмів, потім оцінити результати за класами активів і на часовій контрольній вибірці.
Більш віддалена мета: підтверджена дослідженням основа для використання результатів іншими компонентами системи. Виконання ордерів K_AI не входить до read-only межі K-Trader v1.
Досягнення мети вимірюється відповідністю правилам, причинністю, відтворюваністю та прозорими результатами. Наявність коду або успішний CI не доводить прибутковість.

## Обсяг і доказова база
Проведено:
- читання базових README/REQUIREMENTS/ARCHITECTURE/ROADMAP та поточних дослідницьких специфікацій;
- інвентаризацію GitHub refs і PR, перевірку CI на конкретних SHA;
- статичний перегляд старого pattern-kernel, MT4-адаптера, S1 readiness/kernel/ATR wrapper;
- read-only перевірку живого контейнера/health/DEPLOYED_SHA/диска;
- свіжу агрегацію маніфесту MT4-корпусу та обмежений огляд каталогів результатів.
Не запускали нових стратегічних бектестів або тестових наборів, не змінювали код, права, runtime, ізольовану гілку чи frozen corpus.
Читання маніфесту не є повторною перевіркою кожного файлу архіву/хешів; повний повторний dataset audit не заявляється.

Зафіксовані refs до збереження цього аудиту:
| Напрям | SHA | Фактичний стан |
|---|---|---|
| main | c1bb8b5e0fe314ab11e6eeb8a3f0dd601939cb91 | Захищена основна гілка; DEPLOYED_SHA збігається |
| Специфікації/дослідження PR94 | f1bcfcb6b89a678977f643ddfe72984a69fbd29a | Draft/open/unmerged; CI 38103415324 SUCCESS |
| MT4/S1 інтеграція PR95 | 63214fc1becb83be29adc3c10e3cb56ad8bd9153 | Draft/open/unmerged; CI 38023437463 SUCCESS |
| PR88 | Та сама research head, що PR94 | Інший base ref; також draft/open |
| News Impact PR87 | dc4ee3aedc1c54e5adb0754f02ac50786ba2089c | Draft/open; фактичну KGM-інтеграцію цим аудитом не перевірено |

Публічні прив'язки:
- [PR94](https://github.com/kolemasakar/K-Trader/pull/94)
- [PR95](https://github.com/kolemasakar/K-Trader/pull/95)
- [CI research](https://github.com/kolemasakar/K-Trader/actions/runs/38103415324)
- [CI MT4](https://github.com/kolemasakar/K-Trader/actions/runs/38023437463)

## Свіжий операційний стан
Health generated_at: 2026-10-11T01:59:18.295990Z, тобто 04:59:18 за Києвом.
| Перевірка | Результат |
|---|---|
| Host | k-trader-prod-vnic, SentinelX operational |
| /health | status=ok, mode=read_only, data_ready=true |
| Provider | binance_usdm |
| Scanner | DEGRADED |
| Action auth | enabled |
| Container | Up 9 days (healthy) |
| DEPLOYED_SHA | c1bb8b5e0fe314ab11e6eeb8a3f0dd601939cb91 |
| Диск | 45G total, 16G used, 29G available |

Причину поточного DEGRADED не встановлено: команда читання container logs не дозволена поточним sudo-набором. Старі повідомлення про молоді символи з недостатньою D1-історією не видаються за свіжу причину.
Пряме host-читання /opt/k-trader/data також denied; дозволений sudo docker exec на цьому самому K-Trader host дав потрібний read-only доступ. Привілеї не розширювалися.
Публічний HTTPS/Builder acceptance не перевірявся заново; локальний health не доводить нове повне приймання всіх API-операцій.

## Дані: фактично доступно
Source: /data/kif_research/external/kai_mt4_20261009.
Свіже читання full_corpus_series_validation_20261009.csv:
- 280 активів; 840 серій; 3 881 201 свічка;
- D1/H1/M5 — по 280 серій;
- статус у маніфесті PASS для 840/840;
- класи: 232 акції США, 29 криптоактивів, 15 Forex, 2 енергетичних, 2 металів.

ACHC.us — поточний перший S1-кандидат для інтеграційного тесту:
| TF | Кількість |
|---|---:|
| D1 | 2175 |
| H1 | 2061 |
| M5 | 2198 |

Документована M5-історія ACHC.us: 26.08–06.10.2026; це не річний M5-бектест.
За записом інвентаризації PR95 лише 6 M5-серій мали ≥365 днів, 274 — коротші; цей часовий розподіл не перераховано в поточній свіжій агрегатній перевірці.
Відсутність встановленого UTC для MT4 не блокує погоджений ALGORITHMIC_WALL_CLOCK режим: хронологія порівнюється в однакових умовних координатах. Сесійні/першогодинні перевірки без календарного зв'язку позначаються неоціненими, не автоматично пройденими.
Немає підстав повсюдно заявляти річну глибину чи незалежну сесійну перевірку з самого CSV PASS.

## Статус за складовими
| Складова | Що підтверджено | Що ще відкрите |
|---|---|---|
| Read-only продукт/API/runtime | Реалізовано; живий health/container підтверджено | Поточна причина DEGRADED; свіжий повний HTTPS/API acceptance |
| Phase 11A–11G базова інфраструктура | Історичні replay/каталог/provenance/ізоляція реалізовані | Прийняття нових Gerchik-моделей через ці інтерфейси |
| ATR5 v2 | Канонічний код, погоджені правила й історична перевірка існують | Повна інтеграція у цикл S1; v3 окремий експеримент |
| Сім типів рівнів | Detector/replay/witness machinery існує | Реальні review/strength admission і покриття всіх класів; rating provisional |
| Правила стратегій | S1, S2-А/Б, S3, S4, S5-А/Б, канал погоджені | Технічні політики відтворення та broker metadata |
| MT4-читач | Явний as_of, completed bars, wall-clock, CI PASS | Повне приймання кожної серії/календарів/вартості виконання |
| US-equity levels | PR95 повторно використовує classifier і адаптацію D1/W1 | Реальний ізольований ACHC classifier run/допуск торгових рівнів |
| S1 setup/runner | Часткові causal gates; readiness runner | Повний БПУ/event lifecycle/volume/cancellation/order generation |
| A/B intrabar | Окреме ядро в PR95; успадкований погоджений сценарій S1 | Повна інтеграція всіх подій із формуванням заявок |
| Бектести нинішніх моделей | Завершений пакет результатів не знайдено в перевірених джерелах | Перший повний S1, далі решта моделей/класів |
| Незалежна перевірка | Машинні причинні/witness перевірки є | Реальні незалежні розмітки та недоторкана контрольна вибірка |
| Внутрішні входи каналу | Відкладений варіант | Окрема специфікація/погодження, не блокер поточної версії |

Останній записаний level audit: 43 кандидати на 2555 D1 + 357 W1; 2912 prefix checks без розбіжностей, 43/43 автоматичних witness PASS. Це історична перевірка 04.10, не новий прогін.
Незалежний review-файл містить accepted=[], 21 missing case, tradable_levels_created=0. Нові review-дані в перевірених матеріалах не встановлені; не оголошувати всі дослідницькі кандидати готовими торговими рівнями.

## Основні знахідки аудиту
| ID | Важливість | Знахідка | Потрібна дія |
|---|---|---|---|
| A1 | Висока | Старий gerchik_strategy_patterns_v0_1.py виконує завершені bars/next-open, S3=6 bars, старі S5 й окрему S6. Каналу та нових S2-А/Б входів немає | Матриця специфікація→код→перевірка; перенесення чинних автоматів |
| A2 | Висока | PR95 s1_research_runner.py явно READ_ONLY_S1_READINESS_NOT_BACKTEST; trades/returns=None. inspect_readiness завжди додає ATR5/BPU2 integration reasons | Завершити ордерний генератор і фактичний end-to-end replay; не називати readiness результатом |
| A3 | Висока | Canonical ATR wrapper є, але це ще не знімає readiness/integration gap | Використати існуючий v2 у єдиному циклі, не писати третю версію ATR |
| A4 | Висока | Provisional candidates/score не дорівнюють confirmed strong level admission | Причинна перевірка рівня й посилювальної ознаки; окремі diagnostic/qualified outputs |
| A5 | Середня | ROOT ROADMAP/REQUIREMENTS — історичний production baseline: blanket RR≥3/ATR80/structural TP, старий 1R→3R; нова крипта=1,5R і канал має ATR60 exception | Доповнення актуальним research track; не переносити старі runtime gates у нові сценарії |
| A6 | Середня | Protocol gate report 04.10 BLOCKED включає вже застарілі unapproved S1/S6 поля | Перегенерувати протокол за новим набором/хешами; не рахувати старий список як поточний |
| A7 | Середня | Реальний source доступний, але ізольований запуск нових PR-модулів на ACHC не підтверджений | Завершити вже окремо виконуваний approved bounded research route без зміни прав |
| A8 | Середня | Broker Point/tick/contract/cost metadata та післяfill відхилення ризику не встановлені для повного нового набору | Versioned profiles; незадані net значення UNKNOWN; окреме policy погодження за потреби |
| A9 | Середня | Дублювання варіантів S2-А/Б потребує ключа setup і вибору; одночасні події/гепи потребують явного протоколу | Точні технічні правила без зміни погоджених entry/SL |
| A10 | Середня | Current scanner DEGRADED, актуальна причина не прочитана | Дозволена структурована діагностика або окрема операційна робота |
| A11 | Середня | Основна/дослідницька/MT4 документація й PR descriptions описують різні часові зрізи | Єдиний актуальний index, точні refs й розділення історії від current acceptance |

Реальна відмінність у коді — не доказ загальної поломки legacy production. Це доказ того, що старий candidate kernel не можна зарахувати як реалізацію нових погоджених стратегій.
Успішний CI research/MT4 на зазначених SHA — актуальний факт; кількість локальних тестів зі старих звітів не сумується й не видається за новий запуск.

## Старі результати й межі висновків
На сервері є kai.multi_strategy_r3.summary.v1, контракт fee0b235d3ace98bb1f27da22beb5a0b3ed0681bcdded7a1548ccc9ec59c748a, execution_boundary=RESEARCH_ONLY_COMMON_MODEL_NO_MT4_BROKER_GEOMETRY.
Збережені старі A/B/C setup counts: 605/593/247. Це інший контракт, не S1/S2-А/Б/S3/S4/S5/канал поточних редакцій.
Повні результати й cost provenance цього старого дослідження заново не аудійовано; не переносити його profit factors або net R на поточні моделі. Отже, висновок не «ніколи не було досліджень», а «приймання результатів нового погодженого набору ще не підтверджене».

## Роадмап: історична база й поточний дослідницький шлях
| Етап | Місце | Умова завершення |
|---|---|---|
| Foundation / Phases 0–8.5 | Історично реалізовано | Data→analysis→read-only API; актуальний локальний runtime працює |
| Production / Phases 9–10 | Історично прийнято | Deployment/HTTPS/Action; новий повний live acceptance окремо |
| Phase 11A–11G | Основа реалізована; дослідження тривають | Provenance/replay/outcomes; не рівнозначно доведеній ефективності нових моделей |
| Формалізація Gerchik-стратегій | ЗАВЕРШЕНО для поточного набору | Погоджені authoritative specs, варіанти й канал |
| Відповідність специфікацій коду | НАСТУПНИЙ РУБІЖ; частково реалізовано | Кожне правило має виконуване місце й значущу перевірку |
| Перший повний S1 algorithmic replay | НЕ ПІДТВЕРДЖЕНО | Реальні causal заявки, два незмінні сценарії, результати/скасування/censor/provenance |
| Порівняльні тести моделей/класів | ПОДАЛЬШИЙ ЕТАП | Однакові умови, frozen configs, доступна глибина, окремі варіанти |
| Аналіз і Level Strength v2 | ПІСЛЯ результатів | Очікування/просадка/стійкість; заздалегідь обмежені зміни, без підгонки контрольної вибірки |
| Незалежна контрольна перевірка | ПОДАЛЬШИЙ ЕТАП | Недоторкана хронологічна вибірка й відтворюваний acceptance |
| Production нової методики | ОКРЕМЕ РІШЕННЯ | Технічний/дослідницький acceptance, explicit owner decision |

Phase 12 multi-provider expansion — старий відкладений напрям; немає підстав робити його обов'язковим кроком перед першим S1-тестом. News Impact — окремий компонент, не заміна завершенню стратегії.

## Способи досягнення цілей
- **Відповідність правилам:** versioned specification hash; матриця правил; двосторонні LONG/SHORT й граничні fixture cases; заборона непомітного перенесення legacy constants.
- **Причинність:** levels known_at, завершені D1/W1, pivot availability 2+2, поточний префікс M5 на T−30/stop trigger; дані після cutoff не змінюють попередні рішення.
- **Відтворюваність:** exact code ref, source/control hashes, strategy/config hashes, clock mode, метадані, два фіксовані A/B сценарії; deterministic rerun digest.
- **Реалістичність:** календарна/брокерська прив'язка в окремому fidelity етапі; gross/net окремо, UNKNOWN замість нульових невідомих витрат.
- **Ефективність:** signals→orders→fills→cancel→SL/TP/censored funnel; кількість і якість вибірки, середній R/expectancy, profit factor, просадка в явно визначеному послідовному обліку; окремі клас/модель/напрям/сценарій.
- **Стійкість:** chronological discovery/validation/untouched control; порівняння альтернатив лише як заздалегідь оголошені окремі експерименти; не налаштовувати пороги за вигіднішим intrabar outcome.
- **Ресурси:** reuse існуючих модулів, перший один актив/одна модель, bounded RO runner; FREE_ONLY.

## Подальший рух: послідовно
1) **У цьому чаті — матриця відповідності погодженого комплекту реалізації.** Для кожного правила: джерело/код/перевірка/статус; окремо технічні рішення, що справді змінюють поведінку й потребують погодження. Не починати реалізацію ізольованого напряму тут.
2) **В окремому бектестовому напрямі — завершення S1 на ACHC.us.** Використати наявні ATR5 v2/level detector/wall-clock/ядро A/B; завершити causal level admission, БПУ generator, stop/volume/order lifecycle і дозволений ізольований запуск.
3) **Прийняти перший відтворюваний звіт.** Inventory/time depth, skipped gates, unknown metadata/costs, сигнали/заявки/виконання/скасування/SL/TP/censored; 0 trades в readiness не є market result.
4) **Послідовно підключити S2-А/Б, S3, S4, S5-А/Б і канал.** Верифікувати особливі trigger/stop/cancel механізми; для каналу явно вилучити ATR60 і зберегти 80% від E.
5) **Розширити історичні тести за класами.** Акції/Forex/метали-енергія/крипта, за фактичною доступною глибиною. Бажаний річний горизонт — ціль, коротші серії не перейменовувати у річні.
6) **Проаналізувати результат і сформувати рішення про покращення.** Level Strength v2/окремі альтернативи, потім незалежний контроль. Не робити production-рішення до завершення відповідних gates.

Оцінка календарного строку завершення не підтверджена: залежить від реальної готовності S1 event engine, допуска рівнів, метаданих і isolated execution. Відсоток загальної готовності не наводиться, бо він приховав би різні критерії завершення.

## Трасування джерел
- main README/REQUIREMENTS/ARCHITECTURE/ROADMAP, ref c1bb8b5…
- [Поточний комплект](GERCHIK_STRATEGY_PACKAGE_2026-10-11.md), [реєстр](GERCHIK_STRATEGY_OWNER_GATE_2026-10-04.json), [канал](GERCHIK_CHANNEL_STRATEGY_BASE_APPROVED_2026-10-11.md).
- [Аудит рівнів 04.10](GERCHIK_METHODOLOGY_AUDIT_2026-10-04.md), [independent-label snapshot](GERCHIK_INDEPENDENT_LABEL_READINESS_2026-10-04.json), [старий protocol report](GERCHIK_PROTOCOL_GATE_REPORT_2026-10-04.json).
- [Canonical ATR5](ATR5_GERCHIK_OWNER_DECISION_2026-10-01.md).
- [PR94 pattern code](https://github.com/kolemasakar/K-Trader/blob/f1bcfcb6b89a678977f643ddfe72984a69fbd29a/scripts/research/gerchik_strategy_patterns_v0_1.py).
- [PR95 runner](https://github.com/kolemasakar/K-Trader/blob/63214fc1becb83be29adc3c10e3cb56ad8bd9153/src/ktrader/s1_research_runner.py), [setup](https://github.com/kolemasakar/K-Trader/blob/63214fc1becb83be29adc3c10e3cb56ad8bd9153/src/ktrader/s1_setup.py), [MT4 audit](https://github.com/kolemasakar/K-Trader/blob/63214fc1becb83be29adc3c10e3cb56ad8bd9153/docs/research/S1_BACKTEST_READINESS_AUDIT_20261009.md), [reuse](https://github.com/kolemasakar/K-Trader/blob/63214fc1becb83be29adc3c10e3cb56ad8bd9153/docs/research/S1_EXISTING_IMPLEMENTATIONS_REUSE_20261010.md), [execution gate](https://github.com/kolemasakar/K-Trader/blob/63214fc1becb83be29adc3c10e3cb56ad8bd9153/docs/research/S1_REAL_EXECUTION_GATE_20261010.md).
- Живі read-only результати SentinelX: health, DEPLOYED_SHA, docker ps, df, CSV aggregate, result directory inventory, legacy r3_summary.
