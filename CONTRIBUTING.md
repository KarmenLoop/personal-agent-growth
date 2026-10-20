# Contributing

Describe the task or failure that motivates a change. Include the observed result, the expected result, and a small reproduction without private task memory or credentials.

For changes to a skill rule, explain which decision should change and why. Distinguish a text review, a deterministic utility check, and an actual agent run. Preserve known failures and state what remains untested.

For utility changes, run `python3 -m unittest discover -s tests -v`. If the installable file set changes, update `tools/build_release.py` and check the generated ZIP with `scripts/verify_handoff.py`.

Keep README text, repository descriptions, and commit messages in clear English. Existing skill instructions may remain in Chinese.

Contributions are accepted under this repository's AGPL-3.0-only license. Only submit material you have the right to contribute under those terms. Preserve applicable notices and identify modifications and dates when distributing your own version.

Security reports or private details should go to [info@karmenloop.com](mailto:info@karmenloop.com).
