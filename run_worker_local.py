import argparse
import sys

from dotenv import load_dotenv
from taskiq.cli.worker.cmd import worker_cmd


def main():
    # taskiq worker 실행 인자 설정
    # reload 옵션은 개발 환경에서 유용함
    sys.argv = [
        "taskiq",
        "src._apps.worker.app:app",
        "--reload",
    ]

    # Taskiq 워커 실행
    worker_cmd()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True)
    args = parser.parse_args()

    load_dotenv(dotenv_path=f"_env/{args.env}.env", override=True)

    # argparse가 처리한 인자를 제거하고 taskiq용 인자로 교체해야 함
    # 하지만 taskiq는 내부적으로 sys.argv를 파싱하므로 main()에서 덮어씌움
    main()
