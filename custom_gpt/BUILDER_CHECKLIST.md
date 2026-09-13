# K-Trader — контрольний список GPT Builder v1.5

Статус: Phase 10 COMPLETE для поточного single-provider production scope — production Action, GPT Builder configuration, reachable Preview acceptance і вибраний режим поширення перевірені 2026-09-07. Governance instructions оновлено до затвердженої v1.3.

## Етап A — поведінка GPT
1. Відкрити редактор існуючого K_Trader GPT.
2. Активні Instructions: `custom_gpt/SYSTEM_K_TRADER_v1_3_COMPACT.md`.
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
7. GPT Builder розпізнає всі вісім операцій: `getHealth`, `getScannerStatus`, `listUniverse`, `getMarketSnapshot`, `getCandles`, `getAnalysis`, `listCandidates`, `listSignals`.
8. Усі вісім reachable production operations пройшли Preview acceptance 2026-09-07.
9. Provider ambiguity HTTP 409: backend contract покритий regression test; GPT-side live 409 retry стає blocking gate перед Phase 12 multi-provider activation.
10. Автоперемикання перевірено: канонічні дані доступні → canonical mode; канонічний analysis/OHLCV недоступний → `WATCHLIST ONLY`.

## Етап C — publishing/privacy
1. Для поточного режиму поширення `Усі, хто має посилання` Action має чинний Privacy Policy URL.
2. Після Builder/Preview acceptance GPT оновлено через `Оновити`.
3. Перед майбутнім широким GPT Store/public distribution повторно перевірити актуальні publishing requirements та privacy policy.

## Knowledge upload checklist

Обов'язкові governance/product файли для актуальної конфігурації:

- `custom_gpt/00_KNOWLEDGE_PRIORITY.md`;
- `custom_gpt/SYSTEM_K_TRADER_v1_3_COMPACT.md` використовується як **Instructions**, а не як дубль Knowledge;
- канонічні knowledge-файли, перелічені в `00_KNOWLEDGE_PRIORITY.md`, мають відповідати його пріоритету і статусам.

Не залишати активну v1.2 після переходу на затверджену v1.3.

## Acceptance evidence

Канонічний checkpoint: `docs/PHASE_10_PRODUCT_ACCEPTANCE.md`.

Phase 10 вважається завершеним для поточного read-only single-provider K-Trader v1 scope. Автоматичне виконання угод, exchange-account access, multi-provider ambiguity activation і statistical win probability не входять у цей acceptance; ambiguity Preview стає blocking gate перед Phase 12.
