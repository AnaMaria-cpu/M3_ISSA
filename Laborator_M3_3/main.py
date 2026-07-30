"""Optional launcher for the Ethernet laboratory.

The laboratory also works without this file: server.py and client.py are
standalone applications. This launcher simply opens both applications.
"""
from pathlib import Path
import subprocess
import sys
import time


def main():
    project_dir = Path(__file__).resolve().parent

    server_process = subprocess.Popen(
        [sys.executable, str(project_dir / "server.py")],
        cwd=project_dir,
    )

    # Give the server window time to open. The user still presses Start server.
    time.sleep(0.5)

    client_process = subprocess.Popen(
        [sys.executable, str(project_dir / "client.py")],
        cwd=project_dir,
    )

    try:
        server_process.wait()
        client_process.wait()
    except KeyboardInterrupt:
        server_process.terminate()
        client_process.terminate()


if __name__ == "__main__":
    main()
