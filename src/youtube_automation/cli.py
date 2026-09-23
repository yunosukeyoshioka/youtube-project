"""Command-line entry point.

    youtube-automation create                        # fully automatic, uses config.yaml niche
    youtube-automation create --niche "..."           # override the niche for this run
    youtube-automation create --no-publish            # skip the upload step (still renders the video)
    youtube-automation --channel my-channel create     # run a specific channel (see channels/)
    youtube-automation analyze                        # pull performance stats and derive insights
    youtube-automation list                           # list past projects
    youtube-automation discover-channels --interest "..." --save  # propose new channel concepts
    youtube-automation channels                       # list configured channels
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from .config import CHANNELS_DIR, AppConfig, channel_config_path, load_config
from .pipeline.orchestrator import VideoPipeline
from .pipeline.stages.channel_strategy import ChannelStrategyStage
from .providers.llm import build_llm_provider
from .providers.research import build_research_provider
from .storage import write_channel_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("youtube_automation")


@click.group()
@click.option("--config", "config_path", default=None, help="Path to a config.yaml file.")
@click.option(
    "--channel",
    "channel_slug",
    default=None,
    help="Use channels/<slug>.yaml instead of --config. See `youtube-automation channels`.",
)
@click.pass_context
def cli(ctx: click.Context, config_path: str | None, channel_slug: str | None) -> None:
    """Automate YouTube video ideation, research, scripting, marketing,
    thumbnail design, production, publishing, and improvement -- across one
    or many channels."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path
    ctx.obj["channel_slug"] = channel_slug


def _load_config(ctx: click.Context) -> AppConfig:
    channel_slug = ctx.obj.get("channel_slug")
    if channel_slug:
        path = channel_config_path(channel_slug)
        if not path.exists():
            raise click.ClickException(
                f"No channel config at {path}. Run `youtube-automation discover-channels "
                f"--save` to propose one, or create it by hand (see config.example.yaml)."
            )
        return load_config(path)
    return load_config(ctx.obj.get("config_path"))


@cli.command()
@click.option("--niche", default=None, help="Override the channel niche for this run.")
@click.option(
    "--publish/--no-publish",
    default=True,
    help="Upload to YouTube after rendering (default: on; falls back to dry-run "
    "unless real credentials are configured).",
)
@click.pass_context
def create(ctx: click.Context, niche: str | None, publish: bool) -> None:
    """Run the full pipeline once and produce one finished video."""
    config = _load_config(ctx)
    pipeline = VideoPipeline(config)

    logger.info("Starting video creation pipeline for channel %r...", config.channel.name)
    result = pipeline.create_video(niche=niche, publish=publish)
    project = result.project

    click.echo("")
    click.echo("=" * 60)
    click.echo(f"Channel:    {config.channel.name}")
    click.echo(f"Project:    {project.project_id}")
    click.echo(f"Title:      {project.marketing.chosen_title}")
    click.echo(f"Video:      {project.production.video_path}")
    click.echo(f"Thumbnail:  {project.production.thumbnail.path}")
    if project.publish_result and project.publish_result.published:
        click.echo(f"Published:  {project.publish_result.url}")
    else:
        reason = project.publish_result.reason if project.publish_result else "not run"
        click.echo(f"Published:  no ({reason})")
    click.echo(f"Files:      {result.project_dir}")
    click.echo("=" * 60)


@cli.command()
@click.pass_context
def analyze(ctx: click.Context) -> None:
    """Refresh performance stats for published videos and derive new
    insights to improve future videos."""
    config = _load_config(ctx)
    pipeline = VideoPipeline(config)

    insights = pipeline.refresh_and_learn()
    if not insights:
        click.echo(
            "No new insights yet. This needs real YouTube publishing "
            "(providers.youtube: youtube_api) and some time for view data to "
            "accumulate."
        )
        return
    click.echo("New insights recorded:")
    for insight in insights:
        click.echo(f"  - {insight}")


@cli.command(name="list")
@click.pass_context
def list_projects(ctx: click.Context) -> None:
    """List all past project IDs and their titles for the selected channel."""
    config = _load_config(ctx)
    pipeline = VideoPipeline(config)

    for project_id in pipeline.project_store.list_project_ids():
        data = pipeline.project_store.load(project_id)
        title = (data.get("marketing") or {}).get("chosen_title", "(untitled)")
        click.echo(f"{project_id}  {title}")


@cli.command(name="discover-channels")
@click.option(
    "--interest",
    default=None,
    help="Broad interest area to focus on, e.g. 'cooking' or 'personal finance'. "
    "Defaults to the current config's niche, or general trending analysis if none.",
)
@click.option("--count", default=3, help="How many channel concepts to propose.")
@click.option(
    "--save/--no-save",
    default=False,
    help="Write each proposed concept as channels/<slug>.yaml, ready to use with "
    "`--channel <slug>`.",
)
@click.pass_context
def discover_channels(ctx: click.Context, interest: str | None, count: int, save: bool) -> None:
    """Analyze the current YouTube landscape and propose new channel
    concepts: name, niche, audience, tone, and positioning. Set
    providers.research: youtube_data_api (with YOUTUBE_API_KEY) for
    real competitor data; otherwise falls back to the LLM's general
    knowledge."""
    config = load_config(ctx.obj.get("config_path"))
    llm = build_llm_provider(config)
    research_provider = build_research_provider(config)
    stage = ChannelStrategyStage(llm, research_provider)

    effective_interest = interest or config.channel.niche or "general audience YouTube content"
    logger.info("Analyzing the competitive landscape for %r...", effective_interest)
    concepts = stage.propose(
        interest_area=effective_interest,
        count=count,
        language=config.channel.language,
        video_length_seconds=config.channel.video_length_seconds,
    )

    for i, concept in enumerate(concepts, start=1):
        click.echo("")
        click.echo(f"--- Concept {i}: {concept.name} ---")
        click.echo(f"Niche:        {concept.niche}")
        click.echo(f"Audience:     {concept.audience}")
        click.echo(f"Tone:         {concept.tone}")
        click.echo(f"Positioning:  {concept.positioning}")
        click.echo(f"Pillars:      {', '.join(concept.content_pillars)}")
        click.echo("Sample titles:")
        for title in concept.sample_video_titles:
            click.echo(f"  - {title}")
        click.echo(f"Why:          {concept.reasoning}")

        if save:
            path = write_channel_config(concept, CHANNELS_DIR, config.providers)
            click.echo(f"Saved:        {path}  (run with --channel {path.stem})")


@cli.command(name="channels")
def list_channels() -> None:
    """List every configured channel (channels/*.yaml)."""
    if not CHANNELS_DIR.exists() or not any(CHANNELS_DIR.glob("*.yaml")):
        click.echo(
            "No channels configured yet. Run `youtube-automation discover-channels "
            "--save` to propose some, or add channels/<slug>.yaml by hand."
        )
        return
    for path in sorted(Path(CHANNELS_DIR).glob("*.yaml")):
        config = load_config(path)
        click.echo(f"{path.stem:<24} {config.channel.name} -- {config.channel.niche}")


def main() -> None:
    try:
        cli(obj={})
    except Exception as exc:  # noqa: BLE001 - top-level CLI error reporting
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
