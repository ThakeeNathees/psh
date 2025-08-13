from dataclasses import dataclass, field
from pathlib import Path

from colorama import Fore, Style

from . import sh


@dataclass
class Command:
    desc: str = ""


@dataclass
class ConfigCmd(Command):
    pass


@dataclass
class ThrowConfig(ConfigCmd):
    throw: bool = False


@dataclass
class DescConfig(ConfigCmd):
    pass


@dataclass
class CwdConfig(ConfigCmd):
    cwd: Path = Path.cwd()


@dataclass
class SimpleCommand(Command):
    string: str = ""


@dataclass
class ListCommands(Command):
    commands: list[Command] = field(default_factory=list)

    def __post_init__(self) -> None:
        for cmd in self.commands:
            if isinstance(cmd, DescConfig):
                self.desc = cmd.desc
                self.commands.remove(cmd)
                break


@dataclass
class CommandRegistry:
    desc: str = ""
    commands: "dict[str, Command | CommandRegistry]" = field(default_factory=dict)

    def print_usage(self) -> None:
        try:
            print(f"{Fore.GREEN}Commands:{Style.RESET_ALL}")
            max_cmd_len = max(len(cmd_name) for cmd_name in self.commands.keys())
            for cmd_name, cmd in self.commands.items():
                print(
                    f"  {Fore.BLUE}{cmd_name.ljust(max_cmd_len)}{Style.RESET_ALL}  {cmd.desc}"
                )
        except Exception:
            pass

    def available_commands(self) -> str:
        avail_commands = [
            f"{Fore.YELLOW}{c}{Style.RESET_ALL}" for c in self.commands.keys()
        ]
        return f"Available commands: [{', '.join(avail_commands)}]"


@dataclass
class CommandObj(Command):
    cmd: "Command | CommandRegistry" = field(default_factory=Command)
    cwd: Path | None = None
    ensure_env: set[str] = field(default_factory=set)
    set_env: dict[str, str] = field(default_factory=dict)
    throw: bool | None = None


@dataclass
class ExecCtx:
    args: list[str]
    throw: bool = False
    cwd: Path | None = None

    def get_command(self, reg: CommandRegistry) -> Command:
        if len(self.args) == 0:
            print(f"{Fore.RED}Missing command(s)")
            print(reg.available_commands())
            exit(1)
        cmd_name = self.args.pop(0)
        if cmd_name not in reg.commands:
            print(f"{Fore.RED}Unknown command: {cmd_name}")
            print(reg.available_commands())
            exit(1)
        next_cmd = reg.commands[cmd_name]
        if isinstance(next_cmd, CommandRegistry):
            return self.get_command(next_cmd)
        return next_cmd


@dataclass
class RunConfig:
    reg: CommandRegistry = field(default_factory=CommandRegistry)

    def override(self, other: "RunConfig") -> "RunConfig":
        """Override commands in the registry with the other registry."""
        self.reg.commands.update(other.reg.commands)
        return self

    def execute(self, args: list[str]) -> None:
        try:
            ctx = ExecCtx(args=args, cwd=Path.cwd())
            cmd = ctx.get_command(self.reg)
            RunConfig.execute_command(cmd, ctx)
        except Exception:
            pass

    # TODO: Move the execution to a different file and use with ctx: like
    # way to properly handle exection context instead of setting and undoing
    # in the finally block, it's a complete mess.
    @staticmethod
    def execute_command(cmd: Command, ctx: ExecCtx) -> None:
        cwd: Path | None

        if isinstance(cmd, ConfigCmd):
            if isinstance(cmd, ThrowConfig):
                ctx.throw = cmd.throw
            elif isinstance(cmd, DescConfig):
                pass
            elif isinstance(cmd, CwdConfig):
                ctx.cwd = cmd.cwd

        elif isinstance(cmd, SimpleCommand):
            sh.cmd(cmd.string, throw=ctx.throw)

        elif isinstance(cmd, ListCommands):
            throw = ctx.throw
            cwd = ctx.cwd
            try:
                for sub_cmd in cmd.commands:
                    RunConfig.execute_command(sub_cmd, ctx)
            finally:
                ctx.throw = throw
                ctx.cwd = cwd

        elif isinstance(cmd, CommandObj):
            for key, value in cmd.set_env.items():
                sh.set_env(key, value)
            for env_var_name in cmd.ensure_env:
                if not sh.has_env(env_var_name):
                    print(f"{Fore.RED}Missing environment variable: {env_var_name}")
                    print(f'While executing command: "{cmd}"')
                    exit(1)
            throw = ctx.throw
            cwd = ctx.cwd
            ctx.throw = cmd.throw if cmd.throw is not None else ctx.throw
            ctx.cwd = cmd.cwd if cmd.cwd is not None else ctx.cwd
            # ------------------------------------------
            try:
                if ctx.cwd is not None:
                    sh.cd(ctx.cwd)
                if isinstance(cmd.cmd, Command):
                    RunConfig.execute_command(cmd.cmd, ctx)
                elif isinstance(cmd.cmd, CommandRegistry):
                    sub_cmd = ctx.get_command(cmd.cmd)
                    RunConfig.execute_command(sub_cmd, ctx)
            # ------------------------------------------
            finally:
                ctx.throw = throw
                ctx.cwd = cwd
            for key in cmd.set_env.keys():
                sh.unset_env(key)
