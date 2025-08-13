import sys
from contextlib import suppress
from importlib.metadata import version
from pathlib import Path

from colorama import Fore, Style
from platformdirs import user_config_dir
from pydantic import BaseModel

from . import sh
from .parser import ConfigParser, RunConfig

PROJECT_NAME = "py-shell-runner"
VERSION = version(PROJECT_NAME)
RUN_CONFIG_FILE_NAME = "run.yml"
THIS_DIR = Path(__file__).parent
EXAMPLE_FILE = THIS_DIR / "run-example.yml"

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------


def print_usage() -> None:
    """Print the usage information for the script."""
    psh_options = [
        CmdOption(short="-h", long="--help", desc="Show this help message"),
        CmdOption(short="-v", long="--version", desc="Show the version of the package"),
        CmdOption(short="-i", long="--init", desc="Initialize run.yml config file"),
        CmdOption(short="-e", long="--edit", desc="Edit the system level run.yml file"),
        CmdOption(short="", long="--update", desc="Update the package"),
    ]
    print("py-shell-runner", VERSION)
    print(f"{Fore.GREEN}Usage:{Style.RESET_ALL} run [options] <command>\n")

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

        case "-v" | "--version":
            print(VERSION)
            return

        case "-i" | "--init":
            _run_init()
            return

        case "-e" | "--edit":
            _run_edit()
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


def _generate_config_file(path: Path) -> None:
    if path.exists():
        print(f"{Fore.YELLOW}Configuration file already exists: {RUN_CONFIG_FILE_NAME}")
        return
    with open(EXAMPLE_FILE, "r") as example_file:
        with open(path, "w") as out_file:
            out_file.write(example_file.read())
    print(f"{Fore.GREEN}Configuration file generated at {path}")


def _run_init() -> None:
    """Generate a new configuration file."""
    _generate_config_file(Path(RUN_CONFIG_FILE_NAME))


def _run_edit() -> None:
    editor = sh.get_env("EDITOR")
    if editor is None:
        if sh.which("vim"):
            editor = "vim"
        if sh.which("nvim"):
            editor = "nvim"
        elif sh.which("nano"):
            editor = "nano"
        else:
            print(
                f"{Fore.RED}No editor found. Please set the EDITOR environment variable."
            )
            exit(1)
    system_config_path = _system_config_path()
    if not system_config_path.exists():
        _generate_config_file(system_config_path)
    sh.cmd(f"{editor} {system_config_path.parent}")


def _system_config_path() -> Path:
    """Get the system-wide configuration file path."""
    return (
        Path(user_config_dir(PROJECT_NAME, ensure_exists=True)) / RUN_CONFIG_FILE_NAME
    )


def _load_config() -> RunConfig:
    """Load the configuration from the specified YAML files."""
    system_config = _load_system_config()
    local_config = _load_local_config()

    if system_config:
        if local_config:
            return system_config.override(local_config)
        return system_config
    elif local_config:
        return local_config

    print(f"{Fore.RED}No configuration file found: {RUN_CONFIG_FILE_NAME}")
    print("run `run --init` to generate project level config or")
    print("run `run --edit` to generate and edit system level config")
    exit(1)


def _load_local_config() -> RunConfig | None:
    """Load the local configuration from the project directory."""
    config_file_path = Path(RUN_CONFIG_FILE_NAME)
    if not config_file_path.exists():
        return None
    return ConfigParser(config_file_path).parse()


def _load_system_config() -> RunConfig | None:
    """Load the system-wide configuration."""
    config_file_path = _system_config_path()
    if not config_file_path.exists():
        return None
    return ConfigParser(config_file_path).parse()


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
