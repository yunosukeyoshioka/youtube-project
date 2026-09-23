# YouTube Automation Pipeline

Turn a single command into a fully produced YouTube video: idea generation,
research, scriptwriting, marketing/SEO, thumbnail design, video production
(narration + visuals), publishing, and a feedback loop that learns from each
video's real performance.

```bash
youtube-automation create
```

That's it — no title, no script, no thumbnail to design by hand. The
pipeline picks the video's topic based on your channel's configured niche
(or a `--niche` override), writes and voices the script, renders the video,
and either uploads it or leaves it in `data/projects/<id>/` for you to
review, depending on how you've configured publishing.

## Honest expectations

This automates the *production* pipeline end to end. It does **not**
guarantee views or revenue — nothing can. What it does give you:

- A consistent, repeatable process across ideation → research → script →
  marketing → design → production → publish, so you can ship far more often
  than doing it by hand.
- A closed feedback loop: after videos are published, `youtube-automation
  analyze` pulls real view/like data and feeds distilled lessons back into
  future ideation and marketing prompts, so title/angle choices improve over
  time instead of staying static.
- Free, fully offline defaults (local Pillow-rendered visuals, espeak-ng
  narration) so you can run and inspect the whole pipeline with zero paid
  API keys, then swap in premium providers (ElevenLabs voices, AI-generated
  art, real web research) once you're ready to publish videos you'd actually
  want viewers to watch.

Views ultimately depend on the algorithm, competition, and how much you
invest in the premium providers (real narration voice, real illustrations,
real research) — treat this as the automation layer, not a growth
guarantee.

## How it works

```
niche (config) ──▶ Ideation ──▶ Research ──▶ Script ──▶ Marketing ──▶ Design
                                                                          │
                                                                          ▼
                Publish (or dry-run) ◀── Production (TTS + images + ffmpeg)
                       │
                       ▼
             Improvement (pulls real stats, derives insights, feeds
             them back into future Ideation/Marketing prompts)
```

Every stage is a small class in `src/youtube_automation/pipeline/stages/`
that calls one or more **providers** — pluggable interfaces for the LLM,
web research, text-to-speech, image generation, video assembly, and YouTube
upload. See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full
breakdown and how to swap in your own provider.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env         # fill in ANTHROPIC_API_KEY at minimum
cp config.example.yaml config.yaml   # customize your channel's niche/tone
```

`ANTHROPIC_API_KEY` is the one required key — it powers ideation, research
synthesis, scriptwriting, marketing copy, and the improvement loop. Every
other provider has a free/offline default:

| Stage             | Free default                      | Optional upgrade                          |
|-------------------|------------------------------------|--------------------------------------------|
| Research           | LLM's own knowledge (no web access) | Tavily web search (`TAVILY_API_KEY`), or real YouTube data (`YOUTUBE_API_KEY`) |
| Narration (TTS)    | `espeak-ng` (offline) / gTTS       | ElevenLabs (`ELEVENLABS_API_KEY`)          |
| Visuals/thumbnail  | Local Pillow renderer              | OpenAI image generation (`OPENAI_API_KEY`) |
| Publishing         | Dry-run (renders, never uploads)   | Real YouTube upload (OAuth, see below)     |

`espeak-ng` is a system package: `apt-get install espeak-ng` (Debian/Ubuntu)
or `brew install espeak-ng` (macOS). If it's missing, the `auto` TTS
provider falls back to gTTS, and finally to a silent track with burned-in
captions, so the pipeline always produces a video.

## Usage

```bash
# Fully automatic: picks the topic from config.yaml's niche
youtube-automation create

# Override the topic for this run
youtube-automation create --niche "budget travel hacks for solo travelers"

# Render without uploading (also the automatic behavior in dry-run mode)
youtube-automation create --no-publish

# List everything produced so far
youtube-automation list

# After some videos have real view data, refresh insights
youtube-automation analyze
```

Each run writes everything to `data/projects/<project_id>/`:
`project.json` (every stage's structured output + a timestamped log),
`thumbnail.png`, `scenes/` (per-scene audio + images), and `video.mp4`.

## Running multiple channels

`youtube-automation` isn't tied to a single channel. `config.yaml` is your
default channel; any number of additional channels live as their own file
under `channels/<slug>.yaml` (same schema, see `config.example.yaml`) and
each gets its own `data_dir` — so knowledge bases, past videos, and
improvement-loop insights never mix across channels.

You don't have to write those files by hand. `discover-channels` analyzes
the current YouTube landscape and proposes new channel concepts — name,
niche, audience, tone, and how each one is positioned against what's already
out there:

```bash
# Propose 3 channel concepts around an interest area
youtube-automation discover-channels --interest "personal finance for beginners"

# Same, but also write each one to channels/<slug>.yaml
youtube-automation discover-channels --interest "cooking for one" --save

# See every configured channel
youtube-automation channels

# Run a specific channel
youtube-automation --channel budget-builder create
youtube-automation --channel budget-builder list
```

`discover-channels` works with the free LLM-knowledge fallback, but it's
much more grounded with `providers.research: youtube_data_api` and a
`YOUTUBE_API_KEY` set (a plain API key from Google Cloud Console with the
YouTube Data API v3 enabled — no OAuth needed) — that pulls real subscriber
counts, view counts, and currently popular titles for the interest area
instead of relying on the LLM's static knowledge.

## Running it from your phone

The CLI itself needs a real machine (ffmpeg, Python, etc.), so it can't run
directly on a phone. But this repo ships two GitHub Actions workflows with
`workflow_dispatch` triggers, which the **GitHub mobile app** (or any mobile
browser) can fire with a couple of taps: **Actions tab → pick the workflow →
Run workflow**.

- **Create Video** (`.github/workflows/create-video.yml`) — runs the full
  pipeline with optional `channel`/`niche`/`publish` inputs. The finished
  `video.mp4` + `thumbnail.png` come back as a downloadable workflow
  artifact (Actions → the run → Artifacts).
- **Discover Channels** (`.github/workflows/discover-channels.yml`) — runs
  `discover-channels --save` and opens a pull request with the proposed
  `channels/*.yaml` files for you to review and merge, also from your phone.

One-time setup (from a desktop, since GitHub doesn't make entering secrets
convenient on mobile): add `ANTHROPIC_API_KEY` as a repository secret under
**Settings → Secrets and variables → Actions**. Add the optional keys
(`TAVILY_API_KEY`, `ELEVENLABS_API_KEY`, `OPENAI_API_KEY`, `YOUTUBE_API_KEY`)
the same way if you want the premium providers in CI too. After that,
triggering runs is phone-only.

To let **Create Video** publish for real from your phone, base64-encode your
already-authorized `data/youtube_token.json` (see below — you still need to
do the one-time OAuth consent from a machine with a browser first) and add
it as the `YOUTUBE_TOKEN_JSON_B64` secret (`base64 -w0 data/youtube_token.json`).
Without that secret, `publish: true` safely falls back to dry-run.

## Publishing to YouTube for real

By default `providers.youtube` is `dry_run` — the pipeline renders the full
video but never uploads anything, so it's safe to run repeatedly (including
in CI) without a Google account.

To publish for real:

1. In [Google Cloud Console](https://console.cloud.google.com/), create a
   project, enable the **YouTube Data API v3**, and create an OAuth client
   ID of type **Desktop app**.
2. Download the client secret JSON to `data/youtube_client_secret.json`
   (or point `youtube_client_secrets_file` in `config.yaml` elsewhere).
3. Set `providers.youtube: youtube_api` in `config.yaml`.
4. Run `youtube-automation create`. The first run opens a browser for
   consent; the token is cached in `data/youtube_token.json` after that.

Videos publish as `private` by default (`privacy_status` in `config.yaml`)
so you can review before making anything public.

## Development

```bash
pytest                 # unit tests, all offline (mocked LLM, no network/API keys needed)
ruff check src tests   # lint
```

The test suite uses `providers.llm: mock` so it never calls a real API; the
production/video-assembly tests exercise the real `espeak-ng` + `ffmpeg`
path (via the bundled `imageio-ffmpeg` binary) to produce an actual `.mp4`,
proving the pipeline is genuinely end-to-end and not just mocked.
