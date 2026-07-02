@echo off
setlocal

set PYTHON=%~dp0.venv\Scripts\python.exe
set SERVER=%~dp0implementation\mcp_server.py

echo Starting MCP Inspector...
echo Python : %PYTHON%
echo Server : %SERVER%
echo.

npx -y @modelcontextprotocol/inspector "%PYTHON%" "%SERVER%"
