import sys
from pathlib import Path
from colorama import Fore
import yaml

from .pshconfig import PshConfig
from . import sh


PSH_CONFIG_FILE_NAMES = [
    "psh.yaml",
    "psh.yml",
]

# -----------------------------------------------------------------------------
# Main Function
# -----------------------------------------------------------------------------

def main() -> None:

    args = sys.argv[1:]
    if len(args) == 0:
        print(f"{Fore.RED}No command provided. Use 'psh --help' for usage information.")
        return

    config: PshConfig = _load_config()
    cmd_alias = args.pop(0)
    cmd = config.get_cmd(cmd_alias)
    sh.cmd(cmd)


# -----------------------------------------------------------------------------
# Internal Functions
# -----------------------------------------------------------------------------

def _load_config() -> PshConfig:
    """Load the configuration from the specified YAML files."""
    for config_file in PSH_CONFIG_FILE_NAMES:
        if Path(config_file).exists():
            with open(config_file, "r") as file:
                config_data = yaml.safe_load(file)
                return PshConfig.model_validate(config_data)
    print(f"{Fore.RED}No configuration file found. Search filenames: " \
          f"{PSH_CONFIG_FILE_NAMES}")
    exit(1)

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
