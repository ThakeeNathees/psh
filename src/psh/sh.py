"""Module containing common helper functions for the scripting."""

import subprocess
from pathlib import Path
from colorama import Fore


_cd: Path = Path.cwd()


def cmd(command: str, throw: bool = False) -> int:
    """Run a shell command and print its output in real-time.

    The process inherits the parent console. This preserves TTY detection
    and ANSI colors.
    """
    proc = subprocess.Popen(command, shell=True, cwd=_cd)
    return_code = proc.wait()
    if throw and return_code != 0:
        print(f"{Fore.RED}Command failed with exit code {return_code}: {command}")
        raise Exception(f"Command failed with exit code {return_code}: {command}")
    return return_code


def cmd_s(command: str, throw: bool = False) -> str:
    """Do a command substitution like `$(command)` and returns the output."""
    result = subprocess.run(
        command, shell=True, cwd=_cd, capture_output=True, text=True
    )
    if throw and result.returncode != 0:
        print(f'{Fore.RED}Command failed with exit code {result.returncode}: "{command}"')
        raise Exception(f"Command failed with exit code {result.returncode}: {command}")
    return result.stdout


def cd(path: Path) -> int:
    """Change the current working directory to the specified path."""
    global _cd
    _cd = path
    if _cd.exists() and _cd.is_dir():
        return 0
    return 1


def rm(file_path: Path, throw: bool = False) -> None:
    """Remove a file not directory."""
    if file_path.exists() and not file_path.is_dir():
        file_path.unlink()
        print(f"{Fore.GREEN}Removed file: {file_path}")
    else:
        print(f"{Fore.RED}File not found or is a directory: {file_path}")
        if throw:
            raise FileNotFoundError(f"File not found or is a directory: {file_path}")


def rmdir(dir_path: Path, throw: bool = False) -> None:
    """Remove a directory."""
    if dir_path.exists() and dir_path.is_dir():
        dir_path.rmdir()
        print(f"{Fore.GREEN}Removed directory: {dir_path}")
    else:
        print(f"{Fore.RED}Directory not found or is not a directory: {dir_path}")
        if throw:
            raise FileNotFoundError(f"Directory not found or is not a directory: {dir_path}")
