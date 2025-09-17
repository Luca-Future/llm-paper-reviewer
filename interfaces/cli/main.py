"""
Main CLI entry point.
"""

import click
import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

from infrastructure.config.settings import Settings
from infrastructure.container import ApplicationContainer, initialize_container
from core.exceptions import PaperAnalysisError
from domain.models.analysis import AnalysisStatus
from .commands import AnalysisCommands


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--log-level', default='INFO', help='Logging level')
@click.pass_context
def cli(ctx, config, log_level):
    """Paper Reviewer AI - Academic paper analysis tool."""
    setup_logging(log_level)

    # Load configuration
    if config:
        settings = Settings.from_yaml(config)
    else:
        settings = Settings.from_env()

    # Initialize container
    initialize_container(settings)
    ctx.ensure_object(dict)
    ctx.obj['settings'] = settings
    ctx.obj['container'] = ApplicationContainer.get_instance()


@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--prompt-version', help='Prompt version to use')
@click.option('--model', help='AI model to use')
@click.option('--max-length', type=int, help='Maximum characters to analyze')
@click.option('--extract-images', is_flag=True, help='Extract images from PDF')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def analyze(ctx, input_path, output, prompt_version, model, max_length, extract_images, verbose):
    """Analyze a single academic paper."""
    if verbose:
        setup_logging("DEBUG")

    async def _analyze():
        try:
            commands = AnalysisCommands(ctx.obj['container'])
            result = await commands.analyze_paper(
                input_path=input_path,
                output_path=output,
                prompt_version=prompt_version,
                model=model,
                max_length=max_length,
                extract_images=extract_images
            )

            if result.status == AnalysisStatus.COMPLETED:
                click.echo("✅ Analysis completed successfully!")
                if verbose:
                    _display_analysis_result(result)
            else:
                click.echo(f"❌ Analysis failed: {result.error_message}")
                sys.exit(1)

        except PaperAnalysisError as e:
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Unexpected error: {e}")
            sys.exit(1)

    asyncio.run(_analyze())


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--prompt-version', help='Prompt version to use')
@click.option('--model', help='AI model to use')
@click.option('--max-length', type=int, help='Maximum characters to analyze')
@click.option('--concurrent', type=int, default=3, help='Number of concurrent analyses')
@click.pass_context
def batch_analyze(ctx, input_dir, output_dir, prompt_version, model, max_length, concurrent):
    """Analyze multiple papers in a directory."""
    async def _batch_analyze():
        try:
            commands = AnalysisCommands(ctx.obj['container'])
            results = await commands.batch_analyze_papers(
                input_dir=input_dir,
                output_dir=output_dir,
                prompt_version=prompt_version,
                model=model,
                max_length=max_length,
                concurrent=concurrent
            )

            successful = sum(1 for r in results if r.status == AnalysisStatus.COMPLETED)
            total = len(results)

            click.echo(f"📊 Batch analysis completed: {successful}/{total} papers analyzed successfully")

            for result in results:
                if result.status != AnalysisStatus.COMPLETED:
                    click.echo(f"❌ Failed: {result.paper_id} - {result.error_message}")

        except PaperAnalysisError as e:
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Unexpected error: {e}")
            sys.exit(1)

    asyncio.run(_batch_analyze())


@cli.command()
@click.pass_context
def test_connection(ctx):
    """Test connection to AI service."""
    async def _test():
        try:
            commands = AnalysisCommands(ctx.obj['container'])
            success = await commands.test_connection()

            if success:
                click.echo("✅ AI service connection successful!")
            else:
                click.echo("❌ AI service connection failed!")
                sys.exit(1)

        except Exception as e:
            click.echo(f"❌ Connection test error: {e}")
            sys.exit(1)

    asyncio.run(_test())


@cli.command()
@click.pass_context
def info(ctx):
    """Display system information."""
    try:
        commands = AnalysisCommands(ctx.obj['container'])
        info = commands.get_system_info()

        click.echo("📋 Paper Reviewer AI System Information")
        click.echo("=" * 50)
        click.echo(f"Version: {info['version']}")
        click.echo(f"AI Provider: {info['ai_provider']}")
        click.echo(f"AI Model: {info['ai_model']}")
        click.echo(f"Prompt Version: {info['prompt_version']}")
        click.echo(f"Max Paper Length: {info['max_paper_length']}")
        click.echo(f"Supported Formats: {', '.join(info['supported_formats'])}")

    except Exception as e:
        click.echo(f"❌ Error getting system info: {e}")
        sys.exit(1)


def _display_analysis_result(analysis):
    """Display analysis result details."""
    click.echo("\n📋 Analysis Result:")
    click.echo(f"Title: {analysis.title}")
    click.echo(f"Summary: {analysis.summary[:200]}...")
    click.echo(f"Problem: {analysis.problem[:200]}...")
    click.echo(f"Solution: {analysis.solution[:200]}...")
    click.echo(f"Quality Score: {analysis.get_quality_score():.2f}")
    click.echo(f"Processing Time: {analysis.metrics.processing_time:.2f}s")


if __name__ == '__main__':
    cli()