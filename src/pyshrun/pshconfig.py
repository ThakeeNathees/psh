from colorama import Fore, Style
from pydantic import BaseModel


class PshConfig(BaseModel):
    commands: dict[str, str]

    def get_cmd(self, cmd: str) -> str:
        if cmd not in self.commands:
            print(f"{Fore.RED}Unknown command: {cmd}")
            avail_commands = [ f"{Fore.YELLOW}{c}{Style.RESET_ALL}" for c in self.commands.keys() ]
            print(f"Available commands: [{', '.join(avail_commands)}]")
            exit(1)
        return self.commands[cmd]
