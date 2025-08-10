from typing import TypeAlias
from colorama import Fore, Style
from pydantic import BaseModel, Field
from . import sh


class ThrowConfig(BaseModel):
    """Represents a throw configuration in the psh configuration."""
    throw: bool


class Command(BaseModel):
    """Represents a command in the psh configuration."""
    cmd: "str | list[ThrowConfig | str | Command]"
    ensure_env: set[str] = Field(default_factory=set)
    set_env: dict[str, str] = Field(default_factory=dict)
    throw: bool | None = None


CommandType: TypeAlias = str | Command | list[ThrowConfig | str | Command]


class PshConfig(BaseModel):
    commands: dict[str, CommandType]

    def execute(self, alias: str) -> None:
        if alias not in self.commands:
            print(f"{Fore.RED}Unknown command: {alias}")
            avail_commands = [ f"{Fore.YELLOW}{c}{Style.RESET_ALL}" for c in self.commands.keys() ]
            print(f"Available commands: [{', '.join(avail_commands)}]")
            exit(1)
        cmd = self.commands[alias]
        try:
            execute_command(cmd)
        except Exception as _:
            pass


def execute_command(
        cmd: CommandType,
        ensure_envs: set[str] | None = None,
        throw: bool = False,
    ) -> None:

    if isinstance(cmd, str):
        for env_var_name in ensure_envs or set():
            if not sh.has_env(env_var_name):
                print(f"{Fore.RED}Missing environment variable: {env_var_name}")
                print(f"While executing command: \"{cmd}\"")
                exit(1)
        sh.cmd(cmd, throw=throw)

    elif isinstance(cmd, Command):
        for key, value in cmd.set_env.items():
            sh.set_env(key, value)
        throw = cmd.throw if cmd.throw is not None else throw
        execute_command(cmd.cmd, ensure_envs=(ensure_envs or set()) | cmd.ensure_env, throw=throw)
        for key in cmd.set_env.keys():
            sh.unset_env(key)

    elif isinstance(cmd, list):
        for sub_cmd in cmd:
            if isinstance(sub_cmd, ThrowConfig):
                throw = sub_cmd.throw
            else:
                execute_command(sub_cmd, ensure_envs=ensure_envs, throw=throw)
