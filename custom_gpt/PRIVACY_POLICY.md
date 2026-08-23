# K-Trader Action Privacy Policy

K-Trader exposes read-only public derivatives market data and deterministic scanner results to the K_Trader Custom GPT.

- It does not accept exchange credentials.
- It does not access exchange accounts.
- It cannot place, modify, or cancel orders.
- The API is designed not to store ChatGPT prompts or conversation content.
- Normal infrastructure/application logs may contain technical request metadata such as timestamp, client/network address, request path, status code, and diagnostic information needed to operate and secure the service.
- Market-data requests may be sent to configured public exchange market-data endpoints; ChatGPT credentials and exchange-account credentials are not sent to those providers.

The deployed API exposes the current policy at `/privacy`.

Before public GPT distribution, add any operator/contact details required by the selected publishing mode and review the policy against the actual deployed logging/retention configuration.
