import sys
from pathlib import Path
from colorama import Fore, Style
import yaml
from pydantic import BaseModel

from .pshconfig import PshConfig

PSH_CONFIG_FILE_NAME = "psh.yml"
THIS_DIR = Path(__file__).parent


# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------

def print_usage() -> None:
    """Print the usage information for the script."""
    psh_options = [
        CmdOption(short="-h", long="--help", desc="Show this help message"),
        CmdOption(short="-i", long="--init", desc="Initialize psh.yml config file"),
    ]
    max_opt_len = max(option.option_len() for option in psh_options)

    print(f"{Fore.GREEN}Usage:{Style.RESET_ALL} psh [options] <command>")
    print(f"{Fore.GREEN}Commands:{Style.RESET_ALL}")
    for option in psh_options:
        print(option.as_str(max_opt_len))
    print()


def main() -> None:

    args = sys.argv[1:]
    if len(args) == 0:
        print(f"{Fore.RED}No command provided.")
        print_usage()
        return

    arg = args.pop(0)

    # psh specific command
    match arg:
        case "-h" | "--help":
            print_usage()
            return

        case "-i" | "--init":
            _psh_init()
            return

    # Custom user command
    config: PshConfig = _load_config()
    config.execute(arg)


# -----------------------------------------------------------------------------
# Internal
# -----------------------------------------------------------------------------

class CmdOption(BaseModel):
    """Command-line argument model."""
    short: str = ""
    long: str = ""
    desc: str = ""
    params: list[str] | None = None

    def option_len(self) -> int:
        """Return the length of the option str witout the desc."""
        params_str = " " + " ".join(self.params) if self.params else ""
        return len(f"  {self.short}, {self.long}{params_str}")

    def as_str(self, max_opt_len: int) -> str:
        """Return the option as a formatted string."""
        params_str = " " + " ".join(self.params) if self.params else ""
        return (
            f"  {Fore.BLUE}{self.short.ljust(2)}{Style.RESET_ALL}, "
            f"{Fore.BLUE}{self.long.ljust(max_opt_len - 2)}{Style.RESET_ALL}"
            f"{params_str}  {self.desc}"
        )


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


def _load_config() -> PshConfig:
    """Load the configuration from the specified YAML files."""
    config_file_path = Path(PSH_CONFIG_FILE_NAME)
    if not config_file_path.exists():
        print(f"{Fore.RED}No configuration file found: {PSH_CONFIG_FILE_NAME}")
        exit(1)

    with open(config_file_path, "r") as file:
        try:
            config_data = yaml.safe_load(file)
            config = PshConfig.model_validate(config_data)
        except Exception as e:
            print(f"{Fore.RED}Error loading configuration: {e}")
            exit(1)
        return config

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
