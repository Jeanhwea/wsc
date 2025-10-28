:<<"::CMDLITERAL"
@ECHO OFF
GOTO :CMDSCRIPT
::CMDLITERAL

# fmt.cmd format source codes
# THIS SCRIPTS WORKS FOR ALL SYSTEMS Linux/Windows/macOS

set -eux

uv run autoflake -i -r app.py
uv run isort app.py
uv run black app.py
uv run ruff format app.py

exit 0

:CMDSCRIPT

uv run autoflake -i -r app.py
uv run isort app.py
uv run black app.py
uv run ruff format app.py
