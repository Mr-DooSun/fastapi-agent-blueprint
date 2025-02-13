# -*- coding: utf-8 -*-
import argparse

import uvicorn
from dotenv import load_dotenv


def main():
    uvicorn.run("src.server.app:app", reload=True, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()

    load_dotenv(dotenv_path=f"_env/{args.env}.env", override=True)

    main()
