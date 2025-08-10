import sys
from importlib.metadata import version
from pathlib import Path

from colorama import Fore, Style
from pydantic import BaseModel

from .parser import RunConfig, parse_config

PSH_CONFIG_FILE_NAME = "run.yml"
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
    ]
    print(f"{Fore.GREEN}Usage:{Style.RESET_ALL} psh [options] <command>\n")

    print(f"{Fore.GREEN}Options:{Style.RESET_ALL}")

    max_opt_len = max(len(option.long) for option in psh_options)
    for option in psh_options:
        params_str = " " + " ".join(option.params) if option.params else ""
        print(
            f"  {Fore.BLUE}{option.short.ljust(2)}{Style.RESET_ALL}, "
            f"{Fore.BLUE}{option.long.ljust(max_opt_len)}{Style.RESET_ALL}"
            f"{params_str}  {option.desc}"
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
            _psh_init()
            return

        case "-v" | "--version":
            print(version("py-shell-runner"))
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
    params: list[str] | None = None


def _psh_init() -> None:
    """Generate a new configuration file."""
    config_file_path = Path(PSH_CONFIG_FILE_NAME)
    if config_file_path.exists():
        print(f"{Fore.YELLOW}Configuration file already exists: {PSH_CONFIG_FILE_NAME}")
        return

    with open(config_file_path, "w") as file:
        with open(THIS_DIR / "psh-example.yml") as example_file:
            file.write(example_file.read())
    print(f"{Fore.GREEN}Created new configuration file: {config_file_path}")


def _load_config() -> RunConfig:
    """Load the configuration from the specified YAML files."""
    config_file_path = Path(PSH_CONFIG_FILE_NAME)
    if not config_file_path.exists():
        print(f"{Fore.RED}No configuration file found: {PSH_CONFIG_FILE_NAME}")
        exit(1)
    return parse_config(config_file_path)


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
