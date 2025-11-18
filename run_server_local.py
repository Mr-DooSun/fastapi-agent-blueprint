import argparse

import uvicorn
from dotenv import load_dotenv

# import subprocess


def main():
    uvicorn.run("src._apps.server.app:app", reload=True, host="127.0.0.1", port=8000)
    # subprocess.run([
    #     "gunicorn",
    #     "src.apps.monolith.app:app",
    #     "-k", "uvicorn.workers.UvicornWorker",
    #     "-w", "1",
    #     "-b", "0.0.0.0:8000"
    # ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()

    load_dotenv(dotenv_path=f"_env/{args.env}.env", override=True)

    main()
