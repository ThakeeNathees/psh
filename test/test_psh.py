from unittest import TestCase
from pathlib import Path

from pyshrun import sh, project_root


class TestPsh(TestCase):

    def test_project_root(self) -> None:
        PROJECT_ROOT = project_root("test")
        test_dir = Path(__file__).parent
        self.assertEqual(PROJECT_ROOT, test_dir)

    def test_psh_command(self) -> None:
        # Test if the command can be run without throwing an error
        try:
            output = sh.cmd_s("echo Hello, World!").strip()
            self.assertEqual(output, "Hello, World!")
        except Exception as e:
            self.fail(f"Command execution failed with error: {e}")

    def test_run_command(self) -> None:
        # Test if the command can be run without throwing an error
        try:
            this_dir = Path(__file__).parent
            sh.cd(this_dir)
            output = sh.cmd_s("psh build").strip()
            self.assertEqual(output, "Building project...")
        except Exception as e:
            self.fail(f"Command execution failed with error: {e}")

