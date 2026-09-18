# K-Trader — контрольний список GPT Builder v1.6

> **Platform transition notice — 2026-09-16**  
> OpenAI оголосила retirement Custom GPTs і перехід до Plugins. Цей checklist залишається чинним лише для підтримки поточного legacy GPT до retirement. Він **не є довгостроковим deployment target**. Стратегічний напрямок K-Trader зафіксовано в `docs/OPENAI_CUSTOM_GPT_TO_PLUGIN_TRANSITION_2026-09-16.md`: Instructions → Plugin skill/workflow; OpenAPI Action → supported App/Connector/custom MCP integration. Не видаляти цей checklist, доки legacy GPT ще використовується.

Статус: Phase 10 COMPLETE для поточного single-provider production scope — production Action, GPT Builder configuration, reachable Preview acceptance і вибраний режим поширення перевірені 2026-09-07. Governance instructions оновлено до затвердженої v1.4.

## Етап A — поведінка GPT
1. Відкрити редактор існуючого K_Trader GPT.
2. Активні Instructions: `custom_gpt/SYSTEM_K_TRADER_v1_4_COMPACT.md`.
3. У Knowledge обов'язково завантажити/оновити `custom_gpt/00_KNOWLEDGE_PRIORITY.md`; він визначає пріоритет канонічних knowledge-файлів і не замінює Instructions.
4. Опис GPT:

   `Професійний трейдер-аналітик. Відбір і ранжування торгових можливостей за підтвердженими ринковими даними та правилами K-Trader; без виконання угод.`

   Не використовувати `сценарії ≥60%` або інші пороги ймовірності, доки модель не калібрована.
5. Канонічний `custom_gpt/openapi.yaml` вказує на production origin `https://ktrader-api.duckdns.org`.
6. Канонічний режим перевірено в Preview:
   - `data_ready=true` → K-Trader Action має пріоритет;
   - `listSignals=0` не перетворюється на вигадані A/A+ сигнали;
   - `NO_TRADE` зберігається;
   - Entry/SL/TP не вигадуються;
   - Setup Score не трактується як statistical probability.
7. Резервний режим перевірено в Preview:
   - якщо канонічний `getAnalysis`/OHLCV недоступний, повертається `WATCHLIST ONLY`;
   - для кожного кандидата перед агрегатором перевіряється прямий біржовий REST API на відповідному типі ринку;
   - якщо перше пряме джерело не дає придатних даних, перевіряється другий підтримуваний прямий провайдер, якщо актив там доступний;
   - агрегатор використовується лише після таких перевірок;
   - у відповіді зазначаються фактично перевірені прямі джерела;
   - агреговані дані, якщо вони колись використовуються, мають бути явно позначені як агреговані;
   - не змішувати серії різних провайдерів;
   - формулювання нейтральні: `За результатами попереднього відбору відібрано...`;
   - немає фраз `я б звузив`, `я б використовував`, `я вважаю`;
   - користувацький текст українською, крім технічних назв, тикерів, службових статусів і скорочень;
   - GPT не вигадує клас, Оцінку сетапу, Оцінену ймовірність, Вхід, SL, TP, ATR, VSA або A/A+ у резервному режимі.
8. Якщо навіть публічних даних недостатньо або вони застарілі, GPT прямо повідомляє про це і не формує торговий сигнал.

## Етап B — канонічна Action
1. Production server пройшов `scripts/phase10_action_acceptance.py` з `data_ready=true` на `https://ktrader-api.duckdns.org`.
2. `KTRADER_ACTION_API_KEY` зберігається в GitHub Environment `production`; те саме значення введено лише в налаштування автентифікації GPT Action. Не зберігати ключ у репозиторії або документації.
3. Використовується канонічний `custom_gpt/openapi.yaml`.
4. Production one-click schema endpoint: `https://ktrader-api.duckdns.org/action-openapi.yaml`.
5. Автентифікація: API key → Bearer.
6. Privacy Policy URL: `https://ktrader-api.duckdns.org/privacy`.
7. GPT Builder розпізнає всі десять операцій: `getHealth`, `getScannerStatus`, `listUniverse`, `getMarketSnapshot`, `getMT4MarketContextSummary`, `getMT4Candles`, `getCandles`, `getAnalysis`, `listCandidates`, `listSignals`.
8. Базові production operations пройшли Preview acceptance; compact MT4 operations додатково підтверджені live на `EURUSD` та `USDTRY` після production promotion 2026-09-18.
9. Provider ambiguity HTTP 409: backend contract покритий regression test; GPT-side live 409 retry стає blocking gate перед Phase 12 multi-provider activation.
10. Автоперемикання перевірено: канонічні дані доступні → canonical mode; канонічний analysis/OHLCV недоступний → `WATCHLIST ONLY`.

## Етап C — publishing/privacy
1. Для поточного режиму поширення `Усі, хто має посилання` Action має чинний Privacy Policy URL.
2. Після Builder/Preview acceptance GPT оновлено через `Оновити`.
3. Перед майбутнім широким GPT Store/public distribution повторно перевірити актуальні publishing requirements та privacy policy.

## Knowledge upload checklist

Обов'язкові governance/product файли для актуальної конфігурації:

- `custom_gpt/00_KNOWLEDGE_PRIORITY.md`;
- `custom_gpt/SYSTEM_K_TRADER_v1_4_COMPACT.md` використовується як **Instructions**, а не як дубль Knowledge;
- канонічні knowledge-файли, перелічені в `00_KNOWLEDGE_PRIORITY.md`, мають відповідати його пріоритету і статусам.

Не залишати активну v1.2 або v1.3 після переходу на затверджену v1.4.

## Acceptance evidence

Канонічний checkpoint: `docs/PHASE_10_PRODUCT_ACCEPTANCE.md`.

Phase 10 вважається завершеним для поточного read-only single-provider K-Trader v1 scope. Автоматичне виконання угод, exchange-account access, multi-provider ambiguity activation і statistical win probability не входять у цей acceptance; ambiguity Preview стає blocking gate перед Phase 12.


## MT4 operational Preview acceptance

1. Простий запит `проаналізуй USDTRY` сам запускає compact MT4 workflow без ручного переліку Actions.
2. Перший виклик: `getMT4MarketContextSummary(symbol=USDTRY, market=forex)`.
3. Далі GPT отримує `getMT4Candles` для D1/H1/M15/M5 у bounded limits.
4. Повний `getMT4MarketContext` не присутній у Action schema і не використовується.
5. Результат містить `WATCHLIST ONLY` та operational state `NO TRADE/WATCH/SETUP CANDIDATE`, якщо engine signal відсутній.
6. Binance `scanner_status=DEGRADED` не підміняє і не блокує валідний MT4 context.
7. BrokerServer timestamps не трактуються як UTC.
8. Spread/cost і `trade_allowed` відображаються як warnings, але market-context analysis не видається за engine signal.
