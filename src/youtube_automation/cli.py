"""Command-line entry point.

    youtube-automation create                 # fully automatic, uses config.yaml niche
    youtube-automation create --niche "..."    # override the niche for this run
    youtube-automation create --no-publish     # skip the upload step (still renders the video)
    youtube-automation analyze                 # pull performance stats and derive insights
    youtube-automation list                    # list past projects
"""

from __future__ import annotations

import logging
import sys

import click

from .config import load_config
from .pipeline.orchestrator import VideoPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("youtube_automation")


@click.group()
@click.option("--config", "config_path", default=None, help="Path to config.yaml")
@click.pass_context
def cli(ctx: click.Context, config_path: str | None) -> None:
    """Automate YouTube video ideation, research, scripting, marketing,
    thumbnail design, production, publishing, and improvement."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path


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
    config = load_config(ctx.obj.get("config_path"))
    pipeline = VideoPipeline(config)

    logger.info("Starting video creation pipeline...")
    result = pipeline.create_video(niche=niche, publish=publish)
    project = result.project

    click.echo("")
    click.echo("=" * 60)
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
    config = load_config(ctx.obj.get("config_path"))
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
    """List all past project IDs and their titles."""
    config = load_config(ctx.obj.get("config_path"))
    pipeline = VideoPipeline(config)

    for project_id in pipeline.project_store.list_project_ids():
        data = pipeline.project_store.load(project_id)
        title = (data.get("marketing") or {}).get("chosen_title", "(untitled)")
        click.echo(f"{project_id}  {title}")


def main() -> None:
    try:
        cli(obj={})
    except Exception as exc:  # noqa: BLE001 - top-level CLI error reporting
        logger.error("Pipeline failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
