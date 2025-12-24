"""
Taskiq Publisher 테스트 예제

이 파일은 FastAPI Router나 다른 곳에서 Task를 전송하는 방법을 보여줍니다.
"""

import asyncio

from src._core.infrastructure.di.core_container import CoreContainer


async def test_send_task():
    """TaskiqManager를 사용하여 Task를 전송하는 예제"""

    container = CoreContainer()
    taskiq_manager = container.taskiq_manager()

    print("Sending task to Taskiq...")

    # Taskiq는 find_task를 통해 태스크를 찾거나, 데코레이터된 함수를 직접 import해서 .kiq()를 호출할 수 있습니다.
    # TaskiqManager는 이름으로 태스크를 찾아서 전송하는 방식을 사용합니다 (find_task -> kick).

    try:
        result = await taskiq_manager.send_task(
            task_name="{project-name}.user.test",
            kwargs={"user_id": 123, "name": "John Doe", "email": "john@example.com"},
        )
        print("Task sent successfully!")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Failed to send task: {e}")


async def test_send_multiple_tasks():
    """여러 Task를 동시에 전송하는 예제"""

    container = CoreContainer()
    taskiq_manager = container.taskiq_manager()

    print("Sending multiple tasks...")

    tasks = []
    for i in range(5):
        task = taskiq_manager.send_task(
            task_name="{project-name}.user.test",
            kwargs={"user_id": i, "name": f"User {i}", "email": f"user{i}@example.com"},
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    print(f"All {len(results)} tasks sent successfully!")


if __name__ == "__main__":
    print("=== Taskiq Publisher Test ===\n")

    print("Test 1: Send single task")
    asyncio.run(test_send_task())

    print("\n" + "=" * 50 + "\n")

    print("Test 2: Send multiple tasks")
    asyncio.run(test_send_multiple_tasks())

    print("\n=== Test Complete ===")
