# Copyright (C) 2026 KARMENLOOP Official Team
# SPDX-License-Identifier: AGPL-3.0-only
"""Controller contracts only; these checks do not impersonate an actual Agent."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_agent_trial as runner


class RunnerTests(unittest.TestCase):
    def test_same_model_permissions_and_literal_paths_reach_cli(self):
        args = runner.cli_arguments("/path with spaces/codex", {"model":"fixture", "training":False},
                                    Path("workspace with spaces"), Path("native output.txt"))
        self.assertEqual(args[0], "/path with spaces/codex")
        self.assertEqual(args[args.index("-m")+1], "fixture")
        self.assertEqual(args[args.index("--sandbox")+1], "workspace-write")
        self.assertEqual(args[args.index("-C")+1], "workspace with spaces")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)

    def test_training_or_unrecognized_transport_is_not_silently_substituted(self):
        for config in ({"model":"fixture","training":True},
                       {"model":"fixture","training":False,"transport":"unsupported"},
                       {"model":"fixture","training":False,"reasoning_effort":"unknown"}):
            with self.assertRaises(ValueError): runner.cli_arguments("codex", config, Path("w"), Path("f"))

    def test_http_profile_is_per_invocation_and_not_a_builtin_override(self):
        args = runner.cli_arguments("codex", {"model":"fixture","training":False,"transport":"openai-http"},
                                    Path("w"),Path("f"))
        self.assertIn('model_provider="trial-http"',args)
        self.assertTrue(any("supports_websockets=false" in value for value in args))
        self.assertFalse(any("model_providers.openai=" in value for value in args))

    def test_stop_only_the_owned_invocation_and_allow_repeated_cleanup(self):
        process = subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"],
                                   start_new_session=os.name == "posix")
        try:
            runner.stop_owned(process)
            self.assertIsNotNone(process.poll())
            runner.stop_owned(process)
        finally:
            if process.poll() is None: process.kill();process.wait()


if __name__ == "__main__": unittest.main()
