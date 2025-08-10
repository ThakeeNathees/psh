from colorama import init as _colorama_init
from colorama import just_fix_windows_console as _just_fix_windows_console

from . import sh
from .helper import print_error, print_success, print_warning, project_root

# Initialize colorama once so ANSI works on Windows terminals
_colorama_init(autoreset=True)
_just_fix_windows_console()

__all__ = ["project_root", "print_success", "print_error", "print_warning", "sh"]
