# Gold-Trading-Signal-AI-Bot

Gold Signal Bot is a daily signal generator for XAU/USD (Gold) that
combines:

- Market data and technical indicators

- News and macro analysis

- Sentiment scoring

- An optional PyTorch ML model to refine or override signals

- Optional Telegram and Email notifications

The bot is designed to run:

- On-demand (single run)

- On a schedule (cron/Task Scheduler)

- Inside Docker or directly on your machine

It outputs:

- A daily CSV of signals

- A human-readable text report

- A compact signal.txt log

**Table of Contents**

1.  [[Features]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#features)

2.  [[Pipeline
    Flowchart]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#pipeline-flowchart)

3.  [[Detailed Pipeline
    Steps]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#detailed-pipeline-steps)

4.  [[APIs and External
    Services]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#apis-and-external-services)

5.  [[Installation]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#installation)

6.  [[Configuration]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#configuration)

7.  [[Running the
    Bot]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#running-the-bot)

    - [[Core CLI
      Flags]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#core-cli-flags)

    - [[Rule-Based vs ML
      Signal]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#rule-based-vs-ml-signal)

    - [[Proxy
      Options]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#proxy-options)

    - [[Prompt Refinement
      Options]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#prompt-refinement-options)

8.  [[Outputs]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#outputs)

9.  [[Training the ML
    System]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#training-the-ml-system)

    - [[Feature
      Set]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#feature-set)

    - [[Labeling
      Scheme]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#labeling-scheme)

    - [[Training
      Workflow]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#training-workflow)

    - [[Saving the Model and
      Config]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#saving-the-model-and-config)

10. [[Running with
    Docker]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#running-with-docker)

    - [[Building the
      Image]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#building-the-image)

    - [[Running the
      Container]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#running-the-container)

11. [[Scheduling the
    Bot]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#scheduling-the-bot)

12. [[Testing]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#testing)

13. [[Security and
    Disclaimers]{.underline}](https://www.taskade.com/d/ioJMVKnRZ9a41vyi#security-and-disclaimers)

**Features**

- Market Data & Technicals

  - Fetches XAU/USD price and time series from Twelve Data.

  - Computes:

    - SMA20, EMA50

    - RSI(14)

    - MACD (line, signal, histogram)

    - ATR(14)

    - 20-day volatility

    - Moving-average cross (bullish/bearish)

    - Trend slope (via linear regression)

- News & Sentiment

  - Collects recent gold-related news using:

    - SerpApi (Google News) (Perplexity path is stubbed and ready to
      extend).

  - Estimates sentiment per article (VADER).

  - Weights sentiment by impact tag (high, medium, low).

  - Aggregates into a single sentiment score in \[-1, 1\].

- Rule-Based Signal Engine

  - Combines technicals, sentiment, volatility, and macro flags into a
    score S_rule ∈ \[-1, 1\].

  - Maps S_rule to:

    - BUY

    - SELL

    - HOLD

    - UNPREDICTABLE / STAY OUT

  - Provides reasons, suggested action, and basic ATR-based SL/TP.

- PyTorch ML Signal Model (Optional)

  - Uses engineered features (technicals + sentiment + macro).

  - Predicts class probabilities for SELL, HOLD, BUY.

  - Maps to S_ml ∈ \[-1, 1\].

  - Blends with rule-based score:

    - S_final = α \* S_rule + (1 - α) \* S_ml

  - Final signal, confidence, and reasons include ML info.

- Outputs

  - CSV with signal and score.

  - Text report with explanation.

  - signal.txt log for quick inspection.

- Notifications (Optional)

  - Telegram message.

  - Email via SMTP.

- Docker Support

  - Dockerfile provided.

  - Ready for CI/CD or server deployment.

**Pipeline Flowchart**

A concise view of the full pipeline, including the ML system:

Copy┌──────────────────────────────────────────────────────────────┐

│ START / ENTRYPOINT │

│ (python -m src.main or gold-signal-bot) │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 1. Load config & parse CLI args │

│ - Read .env & environment │

│ - Parse flags (once, ML options, proxies, etc.) │

│ - Validate TWELVEDATA_API_KEY │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 2. (Optional) Proxy setup │

│ - Decide to use proxies or direct requests │

│ - (Stub) Load or scrape proxies if enabled │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 3. Market data collection (Twelve Data) │

│ - Fetch latest XAU/USD price │

│ - Fetch recent daily time series │

│ - Compute technical indicators │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 4. News collection (SerpApi / Perplexity stub) │

│ - Query Google News for gold-related headlines │

│ - Basic impact tagging (high/medium/low) │

│ - Save raw news JSON to outputs/ │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 5. Sentiment analysis │

│ - Compute per-article sentiment (VADER) │

│ - Weight by impact │

│ - Aggregate average sentiment in \[-1, 1\] │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 6. Rule-based signal generation │

│ - Combine technicals, sentiment, volatility, macro │

│ - Produce S_rule ∈ \[-1, 1\] │

│ - Map S_rule → BUY / SELL / HOLD / UNPREDICTABLE │

│ - Build reasons, suggested action, SL/TP │

└───────────────┬──────────────────────────────────────────────┘

│

│ if use_ml_signal == True

v

┌──────────────────────────────────────────────────────────────┐

│ 7. ML feature build & inference (PyTorch) │

│ - Build feature_dict from price, indicators, news │

│ - Convert to vector in fixed feature order │

│ - Apply normalization (from model_config.yaml) │

│ - Load model_config + signal_model.pt │

│ - Run forward pass → probabilities \[SELL, HOLD, BUY\] │

│ - Decode to S_ml ∈ \[-1, 1\] and ML confidence │

│ - Blend: S_final = α\*S_rule + (1-α)\*S_ml │

│ - Map S_final → final signal │

│ - Append ML reasoning to explanation │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 8. Export outputs │

│ - Append row to daily CSV │

│ - Write detailed text report │

│ - Append to signal.txt log │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ 9. Optional notifications │

│ - Send Telegram alert (if configured) │

│ - Send Email via SMTP (if configured) │

└───────────────┬──────────────────────────────────────────────┘

│

v

┌──────────────────────────────────────────────────────────────┐

│ END │

└──────────────────────────────────────────────────────────────┘

**Detailed Pipeline Steps**

**1. Configuration and CLI Parsing**

- Loads .env or environment variables.

- Validates TWELVEDATA_API_KEY.

- Applies CLI flags on top of env
  (e.g., \--use-ml-signal, \--output-dir, etc.).

**2. Optional Proxy Setup**

- If proxy usage is enabled, the bot will attempt to:

  - Load or scrape proxies (logic is stubbed and ready to extend).

  - Attach them to HTTP sessions for external API calls.

**3. Market Data Collection**

- Uses the Twelve Data API to:

  - Fetch the latest XAU/USD price.

  - Fetch recent daily OHLC data.

- Computes indicators:

  - SMA20, EMA50

  - RSI(14)

  - MACD (line, signal, histogram)

  - ATR(14)

  - Volatility (20-day standard deviation)

  - Moving-average cross (SMA20 vs EMA50)

  - Trend slope (via regression over recent closes)

**4. News Collection**

- Uses SerpApi (Google News engine) to search for:

  - "gold price XAUUSD macro economic news" (customizable in code).

- Extracts:

  - Title, snippet, URL, source, date.

- Assigns a naive impact_tag (high / medium / low) based on keywords
  (e.g., "Fed", "CPI", "inflation").

- Saves raw news JSON to outputs/news\_\<timestamp\>.json.

(Perplexity integration is scaffolded but requires filling in a real
endpoint and payload.)

**5. Sentiment Analysis**

- For each news item:

  - Builds a text string from title + summary.

  - Computes sentiment with VADER (compound score in \[-1, 1\]).

  - Weights by impact_tag.

- Aggregates to:

  - A single average_score in \[-1, 1\].

  - A list of items, each with sentiment_score attached.

**6. Rule-Based Signal Engine**

- Inputs:

  - Latest price

  - Indicators

  - Aggregated sentiment

  - Volatility and ATR

  - Simple macro flag (e.g., any high-impact news)

- Computes:

  - tech_score: from RSI, MACD, trend, MA cross.

  - sent_score: from news sentiment.

  - vol_score: penalty for high volatility.

  - macro_score: adjustment for macro days.

- Combines into:

  - S_rule = 0.4 \* tech_score + 0.35 \* sent_score + 0.15 \*
    vol_score + 0.1 \* macro_score

  - Clamped to \[-1, 1\].

- Maps S_rule to a label:

  - S_rule ≥ 0.35 → BUY

  - S_rule ≤ -0.35 → SELL

  - -0.15 \< S_rule \< 0.15 → UNPREDICTABLE

  - Else → HOLD

- Derives:

  - confidence_pct_rule = \|S_rule\| \* 100

  - Reasons (bullet points).

  - Suggested action.

  - ATR-based SL/TP for BUY or SELL.

**7. ML Signal (Optional)**

If ML is enabled:

- Builds a feature set from:

  - Price and indicators.

  - Sentiment and news counts.

  - Macro flag.

- Features (exact order):

  1.  price

  2.  sma20_over_price

  3.  ema50_over_price

  4.  rsi14

  5.  macd_hist

  6.  atr14_over_price

  7.  volatility20_over_price

  8.  ma_cross_bullish

  9.  trend_slope_over_price

  10. news_sentiment

  11. num_news_items

  12. num_high_impact_pos

  13. num_high_impact_neg

  14. macro_flag

- Applies normalization defined
  in models/model_config.yaml (currently scheme: \"none\" by default;
  can be updated when you train for real).

- Loads:

  - models/model_config.yaml (metadata).

  - models/signal_model.pt (PyTorch weights).

- Runs inference to get probabilities:

  - \[p_sell, p_hold, p_buy\].

- Decodes to:

  - pred_label_ml ∈ {SELL, HOLD, BUY}

  - S_ml ∈ \[-1, 1\] (via label_to_score mapping).

  - ml_confidence = max probability.

- Blends:

  - S_final = α \* S_rule + (1 - α) \* S_ml

  - Where α is ml_blend_alpha (0.0--1.0).

- Maps S_final to final label and confidence:

  - Same thresholds as rule-based.

  - Final confidence = \|S_final\| \* 100.

- Adds ML reasoning to the final explanation.

**8. Export and Logging**

- Creates/updates:

  - outputs/daily_YYYYMMDD_XAUUSD.csv

  - outputs/daily_YYYYMMDD_XAUUSD.txt

  - outputs/signal.txt

**9. Notifications**

- If configured:

  - Sends a Telegram message with signal summary.

  - Sends an Email with full explanation.

**APIs and External Services**

The bot may use the following external services:

1.  Twelve Data

    - Used for:

      - Latest XAU/USD price.

      - Historical daily time series.

    - Required for the bot to function.

    - Key: TWELVEDATA_API_KEY.

2.  SerpApi (Google Search)

    - Used for:

      - Fetching gold-related news headlines and snippets.

    - Optional but strongly recommended for news/sentiment.

    - Key: SERPAPI_KEY.

3.  Perplexity (Planned / Stubbed)

    - Intended for:

      - Richer macro and news context.

    - Requires:

      - PERPLEXITY_API_KEY.

    - Current code includes a stub for future integration.

4.  OpenAI (Optional)

    - Intended for:

      - Prompt refinement for Perplexity or other LLM flows.

    - Key: OPENAI_API_KEY.

    - Optional; not required for basic operation.

5.  Telegram Bot API (Optional)

    - For sending notifications.

    - Requires:

      - TELEGRAM_BOT_TOKEN

      - TELEGRAM_CHAT_ID.

6.  SMTP Email (Optional)

    - For email alerts.

    - Requires:

      - SMTP_HOST, SMTP_PORT

      - SMTP_USERNAME, SMTP_PASSWORD (if needed)

      - SMTP_FROM, SMTP_TO.

**Installation**

1.  Clone the repository

2.  Copygit clone \<your_repo_url\> gold-signal-bot

3.  cd gold-signal-bot

4.  Create and activate a virtual environment (recommended)

5.  Copypython -m venv .venv

6.  source .venv/bin/activate \# Linux/macOS

7.  \# or

8.  .venv\\Scripts\\activate \# Windows

9.  Install dependencies

10. Copypip install -r requirements.txt

11. Copy and edit environment file

12. Copycp .env.example .env

> Fill in at least:

- TWELVEDATA_API_KEY

- SERPAPI_KEY (for news)

- (Optional) Telegram/SMTP/ML keys.

**Configuration**

Configuration comes from:

- .env / environment variables.

- CLI flags (override env).

Key environment variables:

- Core:

  - TWELVEDATA_API_KEY (required)

  - SERPAPI_KEY (recommended for news)

  - PERPLEXITY_API_KEY (future use)

  - OPENAI_API_KEY (future use)

- ML:

  - USE_ML_SIGNAL (true / false)

  - ML_MODEL_CONFIG_PATH (default: models/model_config.yaml)

  - ML_DEVICE (cpu / cuda)

  - ML_BLEND_ALPHA (0.0--1.0)

- Proxies:

  - USE_PROXIES

  - PROXY_MODE (load_saved / scrape)

  - PROXY_TYPE (http / socks5)

- Output:

  - OUTPUT_DIR (default: outputs)

  - DRY_RUN (if true, skip writing outputs/notifications)

- Notifications:

  - TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

  - SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM, SMTP_TO

**Running the Bot**

**Core CLI Flags**

Basic usage:

Copypython -m src.main \--once \--output-dir outputs

Key flags:

- \--once\
  Run the pipeline once and exit.

- \--output-dir PATH\
  Override output directory (default: outputs).

- \--dry-run\
  Run the whole pipeline but do not write files or send notifications.

**Rule-Based vs ML Signal**

- \--use-ml-signal\
  Enable ML-based blending with rule-based signal.

- \--no-use-ml-signal\
  Force rule-based only, even if env says otherwise.

- \--ml-model-config-path PATH\
  Path to model metadata, default models/model_config.yaml.

- \--ml-device {cpu,cuda}\
  Device for PyTorch inference.

- \--ml-blend-alpha FLOAT\
  Blending coefficient α in \[0,1\]:

  - α = 1.0 → pure rule-based (S_final = S_rule)

  - α = 0.0 → pure ML (S_final = S_ml)

  - α = 0.5 → equal blend

Examples

Rule-based only (default):

Copypython -m src.main \--once \--output-dir outputs

Enable ML blending (50/50):

Copypython -m src.main \\

\--once \\

\--use-ml-signal \\

\--ml-model-config-path models/model_config.yaml \\

\--ml-device cpu \\

\--ml-blend-alpha 0.5 \\

\--output-dir outputs

Pure ML signal:

Copypython -m src.main \\

\--once \\

\--use-ml-signal \\

\--ml-model-config-path models/model_config.yaml \\

\--ml-device cpu \\

\--ml-blend-alpha 0.0 \\

\--output-dir outputs

Force rule-based (ignore ML):

Copypython -m src.main \\

\--once \\

\--no-use-ml-signal \\

\--output-dir outputs

**Proxy Options**

- \--use-proxies\
  Attempt to route HTTP requests via proxies.

- \--proxy-mode {load_saved,scrape}\
  Select proxy source mode (logic is minimal/stubbed).

- \--proxy-type {http,socks5}\
  Proxy protocol type.

Example:

Copypython -m src.main \\

\--once \\

\--use-proxies \\

\--proxy-mode scrape \\

\--proxy-type http \\

\--output-dir outputs

**Prompt Refinement Options**

The project scaffolds prompt refinement and Perplexity usage; you can
control them via:

- \--prefer-perplexity / \--no-prefer-perplexity

- \--use-chatgpt-for-prompt-refinement / \--no-use-chatgpt-for-prompt-refinement

These are primarily for future extension when Perplexity and LLM-based
prompt refinement are fully wired.

**Outputs**

After a successful run, you'll see in outputs/:

- daily_YYYYMMDD_XAUUSD.csv\
  Contains timestamp, symbol, price, signal, score, confidence.

- daily_YYYYMMDD_XAUUSD.txt\
  Human-readable report:

  - Timestamp, symbol, price

  - Final signal, score, confidence

  - Reasons (including ML reasoning if enabled)

  - Suggested action

  - SL/TP

- signal.txt\
  Log format: one line per run:

  - ISO timestamp

  - Symbol

  - Signal

  - Score

  - Confidence

- news_YYYYMMDD_HHMMSS.json\
  Raw news items retrieved for that run.

**Training the ML System**

The repo includes an inference-ready ML pipeline. To get real value, you
need to:

- Train a model offline using historical data.

- Save it to models/signal_model.pt.

- Update models/model_config.yaml as needed (especially normalization).

**Feature Set**

The ML model expects a 14-dimensional feature vector in this exact
order:

1.  price

2.  sma20_over_price

3.  ema50_over_price

4.  rsi14

5.  macd_hist

6.  atr14_over_price

7.  volatility20_over_price

8.  ma_cross_bullish (0 or 1)

9.  trend_slope_over_price

10. news_sentiment

11. num_news_items

12. num_high_impact_pos

13. num_high_impact_neg

14. macro_flag (0 or 1)

These are built at runtime by the bot's feature builder.

**Labeling Scheme**

A typical labeling strategy:

1.  For each historical day t, compute XAU/USD return:

    - ret\_{t+1} = (close\_{t+1} - close_t) / close_t

2.  Choose thresholds (example):

    - If ret\_{t+1} \> +0.003 → BUY (label 2)

    - If ret\_{t+1} \< -0.003 → SELL (label 0)

    - Else → HOLD (label 1)

3.  Align each feature vector at day t with label derived from t+1.

You can adjust thresholds and horizon (e.g., 2-day returns) based on
your strategy.

**Training Workflow**

1.  Collect Data

    - Historical OHLC data for XAU/USD (from Twelve Data or any
      provider).

    - Historical news and sentiment (you can log daily features and
      labels over time with the bot, then train later).

2.  Build Dataset

    - For each day:

      - Compute indicators using the same functions as the bot.

      - Build feature_dict and feature_vector in the same order.

    - Normalize features (e.g., StandardScaler).

    - Split into train/validation/test sets (time-based splits).

3.  Train Model (PyTorch)

    - Use the SignalMLP architecture (same as in the bot).

    - Input dimension: 14.

    - Hidden layers: e.g., \[64, 32\].

    - Output dimension: 3 (SELL, HOLD, BUY).

    - Loss: CrossEntropyLoss.

    - Optimizer: Adam or similar.

4.  Evaluate

    - Track accuracy, F1, confusion matrix.

    - Adjust hyperparameters / thresholds as needed.

**Saving the Model and Config**

Once trained:

1.  Save the model:

2.  Copytorch.save(model.state_dict(), \"models/signal_model.pt\")

3.  Update models/model_config.yaml:

    - model.input_dim, hidden_layers, output_dim (must match training).

    - model.state_dict_path: \"models/signal_model.pt\".

    - features.order: keep as defined (unless you change your features;
      then you must update both training and inference).

    - features.normalization:

      - Set scheme: \"standard\".

      - Fill in mean and std for each feature (from your scaler).

    - classes:

      - Ensure index_to_label and label_to_index match your labels.

      - label_to_score defines mapping to \[-1, 1\].

4.  (Optional) Use the
    provided scripts/create_dummy_signal_model.py script as a template
    to build your own training and saving logic.

Once signal_model.pt and model_config.yaml are in place, the bot will
use your trained model when use_ml_signal is enabled.

**Running with Docker**

**Building the Image**

From the project root:

Copydocker build -t gold-signal-bot .

**Running the Container**

Basic run (rule-based only):

Copydocker run \--rm \\

\--env-file .env \\

-v \"\$(pwd)/outputs:/app/outputs\" \\

gold-signal-bot \\

python -m src.main \--once \--output-dir outputs

With ML enabled:

Copydocker run \--rm \\

\--env-file .env \\

-v \"\$(pwd)/outputs:/app/outputs\" \\

-v \"\$(pwd)/models:/app/models\" \\

gold-signal-bot \\

python -m src.main \\

\--once \\

\--use-ml-signal \\

\--ml-model-config-path models/model_config.yaml \\

\--ml-device cpu \\

\--ml-blend-alpha 0.5 \\

\--output-dir outputs

Notes:

- Mount outputs so that results are available on the host.

- Mount models if you maintain model artifacts outside the image.

- Ensure .env contains all required keys.

**Scheduling the Bot**

**Linux (cron)**

Edit crontab:

Copycrontab -e

Add a daily job (e.g., 21:00 UTC):

Copy0 21 \* \* \* cd /path/to/gold-signal-bot && /path/to/python -m
src.main \--once \--output-dir outputs \>\> cron.log 2\>&1

For ML-enabled daily run:

Copy0 21 \* \* \* cd /path/to/gold-signal-bot && /path/to/python -m
src.main \--once \--use-ml-signal \--ml-model-config-path
models/model_config.yaml \--ml-device cpu \--ml-blend-alpha 0.5
\--output-dir outputs \>\> cron.log 2\>&1

**Windows (Task Scheduler)**

- Create a Basic Task.

- Trigger: Daily at your chosen time.

- Action: Start a program:

  - Program/script: python

  - Arguments: -m src.main \--once \--output-dir outputs

  - Start in: C:\\path\\to\\gold-signal-bot

To enable ML, add ML flags to the Arguments field.

**Testing**

To run the test suite:

Copypytest

To run only unit tests:

Copypytest -m unit

To add your own tests (recommended):

- Put them under the tests/ directory.

- Use pytest conventions.

**Security and Disclaimers**

- API Keys:\
  Never commit real API keys to Git. Use .env and environment variables.

- Trading Risk:\
  This bot is for educational and research purposes. It
  does not constitute financial advice. Always:

  - Use proper risk management.

  - Validate any strategy on historical data.

  - Comply with local regulations and broker requirements.

- ML Interpretability:\
  The ML model can improve signal quality but also introduce complexity.
  The blended approach allows you to retain rule-based transparency
  while gradually incorporating learned patterns.
