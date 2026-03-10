"""Main entry point for the Personal Assistant CLI."""

from app.cli import PersonalAssistantCLI

if __name__ == "__main__":
    cli = PersonalAssistantCLI()
    cli.load_content()
    try:
        cli.run()
    except KeyboardInterrupt:
        cli.exit(1)
    except Exception:
        cli.console.print_exception(show_locals=True)
    finally:
        cli.save_content()
