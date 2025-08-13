from pathlib import Path
from typing import TypeAlias

import yaml
from colorama import Fore

from .types import *

CommandData: TypeAlias = str | list | dict


class ConfigParser:

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def parse(self) -> RunConfig:
        config = RunConfig()
        with open(self.file_path, "r") as file:
            config_data = yaml.safe_load(file)
            if not isinstance(config_data, dict):
                print(f"{Fore.RED}Invalid configuration expected a dict")
                exit(1)
            if "commands" not in config_data:
                print(f"{Fore.RED}Missing 'commands' key in configuration")
                exit(1)
            for cmd_name, cmd_data in config_data["commands"].items():
                cmd = self._parse_command(cmd_data)
                config.reg.commands[cmd_name] = cmd
        return config

    def _parse_command(self, cmd_data: CommandData) -> Command | CommandRegistry:

        if isinstance(cmd_data, str):
            return SimpleCommand(string=cmd_data)

        elif isinstance(cmd_data, list):
            commands: list[Command] = []
            for item in cmd_data:
                sub_cmd = self._parse_command(item)
                if not isinstance(sub_cmd, Command):
                    print(f"{Fore.RED}Expected a command in list: {item}")
                    exit(1)
                commands.append(sub_cmd)
            return ListCommands(commands=commands)

        elif isinstance(cmd_data, dict):
            # Throw config
            if "throw" in cmd_data and len(cmd_data) == 1:
                return ThrowConfig(throw=cmd_data["throw"])

            # Desc config
            if "desc" in cmd_data and len(cmd_data) == 1:
                return DescConfig(desc=cmd_data["desc"])

            # Command object
            if "cmd" in cmd_data:
                # TODO: change the keys from "cwd" to "/cwd" so the "cwd"
                # and other commands can be a custom user command.
                desc = cmd_data.pop("desc", "")
                ensure_env = set(cmd_data.pop("ensure_env", []))
                set_env = dict(cmd_data.pop("set_env", {}))
                throw = cmd_data.pop("throw", None)
                cwd = cmd_data.pop("cwd", None)
                cmd = self._parse_command(cmd_data.pop("cmd"))
                if len(cmd_data) > 0:
                    print(
                        f"{Fore.RED}Unexpected keys in command definition: {list(cmd_data.keys())}"
                    )
                    exit(1)
                return CommandObj(
                    cmd=cmd,
                    cwd=self.resolve_cwd(cwd) if cwd else None,
                    desc=desc,
                    ensure_env=ensure_env,
                    set_env=set_env,
                    throw=throw,
                )

            # Command registry
            reg = CommandRegistry()
            for key, value in cmd_data.items():
                cmd = self._parse_command(value)
                if key == "desc":
                    if not isinstance(cmd, SimpleCommand):
                        print(f"{Fore.RED}Expected a string 'desc': {value}")
                        exit(1)
                    reg.desc = cmd.string
                else:
                    reg.commands[key] = cmd
            return reg

    def resolve_cwd(self, cwd: str) -> Path:
        # TODO: Document this and add test
        if cwd.strip().startswith("$THIS_DIR"):
            return (Path(self.file_path) / cwd.removeprefix("$THIS_DIR")).parent
        return Path(cwd).resolve()
