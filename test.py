import inspect

import taskiq.cli.worker.cmd

# run_worker 함수가 받는 인자들을 확인합니다.
print(inspect.signature(taskiq.cli.worker.cmd.run_worker))
