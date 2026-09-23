# Architecture

## Pipeline stages

Each stage lives in `src/youtube_automation/pipeline/stages/` and reads/
writes fields on a single `VideoProject` (see `models.py`) as it flows
through `pipeline/orchestrator.py::VideoPipeline.create_video()`.

1. **Ideation** (`ideation.py`) — brainstorms 5 ideas for the channel's
   niche via the LLM provider, informed by the knowledge base's summary of
   what's worked before, and picks the highest `virality_score`.
2. **Research** (`research.py`) — queries the research provider for
   supporting sources, then has the LLM synthesize a `ResearchBrief`.
   Explicitly labels unverified claims when no web search is configured.
3. **Script** (`script.py`) — turns the idea + research into a scene-by
   -scene `Script`: a hook line, N scenes (narration, visual direction,
   on-screen caption, duration hint), and a call to action.
4. **Marketing** (`marketing.py`) — generates SEO title options, a
   description, tags, hashtags, and thumbnail concepts.
5. **Design** (`design.py`) — renders the thumbnail via the image provider.
6. **Production** (`production.py`) — for every scene: synthesizes
   narration audio (TTS provider) and renders the visual (image provider),
   then hands everything to the video assembler to produce the final
   `video.mp4` with burned-in captions.
7. **Publishing** (`publishing.py`) — uploads via the YouTube provider, or
   no-ops in dry-run mode.
8. **Improvement** (`analytics.py`) — a separate flow (`refresh_and_learn`,
   exposed as `youtube-automation analyze`) that pulls real view/like counts
   for published videos, stores them in the knowledge base, and asks the LLM
   to distill actionable insights. Those insights are injected into every
   future Ideation and Marketing prompt via
   `KnowledgeBase.context_for_prompt()`.

A ninth stage sits outside the per-video pipeline, one level up: **Channel
strategy** (`channel_strategy.py`, exposed as `youtube-automation
discover-channels`) — queries the research provider for the competitive
landscape around an interest area, then asks the LLM to propose several
distinct channel concepts (name, niche, audience, tone, positioning,
content pillars, sample titles). `storage/channel_config_writer.py` can turn
any concept straight into a `channels/<slug>.yaml`, ready to run with
`--channel <slug>`.

## Providers

Every external capability is behind a small interface in
`src/youtube_automation/providers/<capability>/base.py`, built by a factory
function in that package's `__init__.py` from `config.yaml` +
environment variables. This is what makes every stage swappable without
touching pipeline code:

- `providers/llm` — `LLMProvider.generate_json(system, prompt) -> dict`.
  `AnthropicProvider` (default) or `MockLLMProvider` (deterministic, offline,
  used by the test suite).
- `providers/research` — `ResearchProvider.search(query) -> list[SearchResult]`.
  `TavilyResearchProvider`, `YouTubeDataResearchProvider` (real subscriber/
  view counts and popular titles via a plain YouTube Data API key -- no
  OAuth -- used by both the research stage and `discover-channels`), or
  `LLMKnowledgeResearchProvider` (returns no results, so the caller falls
  back to the LLM's own knowledge).
- `providers/tts` — `TTSProvider.synthesize(text, path) -> duration_seconds`.
  `EspeakTTSProvider` (offline), `GoogleTTSProvider` (gTTS, free but needs
  network), `ElevenLabsTTSProvider` (paid, best quality),
  `SilentPlaceholderTTSProvider` (always succeeds; last-resort fallback).
  `AutoTTSProvider` chains several of these and falls back on any runtime
  failure (missing binary, network error) rather than crashing the run.
- `providers/image` — `ImageProvider.generate_scene_image(...)` /
  `.generate_thumbnail(...)`. `LocalImageProvider` (Pillow gradient + bold
  text, zero cost) or `OpenAIImageProvider` (real AI-generated art).
- `providers/video` — `VideoAssembler.assemble(scenes, captions, path)`.
  `FfmpegVideoAssembler` renders each scene as a still-image clip with
  burned-in captions (via `imageio-ffmpeg`'s bundled static binary, so no
  system ffmpeg install is required) and concatenates them.
- `providers/youtube` — `YouTubePublisher.publish(...)`. `DryRunPublisher`
  (default, safe) or `YouTubeApiPublisher` (real OAuth upload via the
  YouTube Data API v3). `YouTubeStatsReader` is the read-only counterpart
  used by the improvement stage.

## Storage

- `storage/project_store.py` — persists each `VideoProject` (as JSON) plus
  its generated media under `data/projects/<project_id>/`.
- `storage/knowledge_base.py` — a single JSON file
  (`data/knowledge_base.json`) recording every project's chosen title/tags,
  its performance once published, and the running list of distilled
  insights. `context_for_prompt()` renders this into a short text block
  injected into Ideation and Marketing prompts — this is the whole
  "improvement" loop.

## Multi-channel config resolution

`config.py::load_config(path)` reads one YAML file (defaulting to
`config.yaml`) plus environment variable overrides into an `AppConfig`.
There's nothing channel-specific about `AppConfig` itself -- multi-channel
support is just a CLI-level convention: `cli.py::_load_config()` resolves
`--channel <slug>` to `channels/<slug>.yaml` (via
`config.channel_config_path()`) before falling back to `--config`/
`config.yaml`. Each channel config typically points `data_dir` at its own
`data/channels/<slug>/`, so `ProjectStore` and `KnowledgeBase` -- and
therefore the improvement loop's insights -- never mix across channels.

## Adding a new provider

1. Implement the relevant `base.py` interface in a new module under
   `providers/<capability>/`.
2. Add a branch for it in that package's `build_*_provider()` factory,
   reading any needed config/env values from `AppConfig`.
3. Reference it by name in `config.yaml` under `providers.<capability>`.

No pipeline stage or orchestrator code needs to change.
