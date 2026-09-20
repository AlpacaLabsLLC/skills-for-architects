#!/usr/bin/env python3
"""Local stdio adapter using the official MCP SDK; no remote transport."""
import argparse
from pathlib import Path
import sys
from typing import Any
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp.server import MCPServer
from run import execute


def server(package_manifest):
    app = MCPServer('Arch Studio local operations')

    @app.tool(name='as_execute_operation', structured_output=True)
    def operation(request: dict[str, Any]) -> dict[str, Any]:
        """Execute one declared operation locally from the pinned Arch Studio package; no arbitrary commands."""
        return execute(request, package_manifest)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-manifest', required=True)
    args = parser.parse_args()
    server(Path(args.package_manifest).resolve()).run(transport='stdio')
