import sys
from contextlib import suppress
from importlib.metadata import version
from pathlib import Path

from colorama import Fore, Style
from pydantic import BaseModel

from . import sh
from .parser import RunConfig, parse_config

PROJECT_NAME = "py-shell-runner"
RUN_CONFIG_FILE_NAME = "run.yml"
THIS_DIR = Path(__file__).parent


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------


def print_usage() -> None:
    """Print the usage information for the script."""
    psh_options = [
        CmdOption(short="-h", long="--help", desc="Show this help message"),
        CmdOption(short="-i", long="--init", desc="Initialize psh.yml config file"),
        CmdOption(short="-v", long="--version", desc="Show the version of the package"),
        CmdOption(short="", long="--update", desc="Update the package"),
    ]
    print(f"{Fore.GREEN}Usage:{Style.RESET_ALL} psh [options] <command>\n")

    print(f"{Fore.GREEN}Options:{Style.RESET_ALL}")
    max_opt_len = max(len(option.long) for option in psh_options)
    for option in psh_options:
        if option.short:
            print(f"  {Fore.BLUE}{option.short.ljust(2)}{Style.RESET_ALL}, ", end="")
        else:
            print(" " * 6, end="")
        print(
            f"{Fore.BLUE}{option.long.ljust(max_opt_len)}{Style.RESET_ALL} {option.desc}"
        )
    print()

    config: RunConfig = _load_config()
    config.reg.print_usage()


def main() -> None:

    args = sys.argv[1:]
    if len(args) == 0:
        print(f"{Fore.RED}No command provided.")
        print_usage()
        return

    # psh specific command
    match args[0]:
        case "-h" | "--help":
            print_usage()
            return

        case "-i" | "--init":
            _run_init()
            return

        case "-v" | "--version":
            print(version(PROJECT_NAME))
            return

        case "--update":
            _self_update()
            return

    # Custom user command
    config: RunConfig = _load_config()
    config.execute(args)


# -----------------------------------------------------------------------------
# Internal
# -----------------------------------------------------------------------------


class CmdOption(BaseModel):
    """Command-line argument model."""

    short: str = ""
    long: str = ""
    desc: str = ""


def _run_init() -> None:
    """Generate a new configuration file."""
    config_file_path = Path(RUN_CONFIG_FILE_NAME)
    if config_file_path.exists():
        print(f"{Fore.YELLOW}Configuration file already exists: {RUN_CONFIG_FILE_NAME}")
        return

    with open(THIS_DIR / "run-example.yml", "r") as example_file:
        with open(config_file_path, "w") as out_file:
            out_file.write(example_file.read())
    print(f"{Fore.GREEN}Created new configuration file generated: {config_file_path}")


def _load_config() -> RunConfig:
    """Load the configuration from the specified YAML files."""
    config_file_path = Path(RUN_CONFIG_FILE_NAME)
    if not config_file_path.exists():
        print(f"{Fore.RED}No configuration file found: {RUN_CONFIG_FILE_NAME}")
        exit(1)
    return parse_config(config_file_path)


def _self_update() -> None:

    # Try installing using uv (if we're in a virtual environment)
    if sh.which("uv") is not None:
        with suppress(Exception):
            sh.cmd(f"uv add --dev {PROJECT_NAME}", throw=True)
            sh.cmd(f"uv sync --upgrade-package {PROJECT_NAME} --refresh", throw=True)
            return

        with suppress(Exception):
            sh.cmd(
                f"uv pip install --no-cache-dir --upgrade {PROJECT_NAME}", throw=True
            )
            return

        print(f"{Fore.RED}Failed to update using uv. Trying pip...{Style.RESET_ALL}")

    if sh.which("pip") is None:
        print(f"{Fore.RED}pip is not installed. Cannot update {PROJECT_NAME}.")
        return

    sh.cmd(f"pip install --no-cache-dir --upgrade {PROJECT_NAME}", throw=True)


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
