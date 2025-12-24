import asyncio

from taskiq_aws import SQSBroker

# 1. SQS 브로커 초기화
# queue_url은 AWS 콘솔에서 생성한 SQS 대기열의 URL을 입력합니다.
broker = SQSBroker(
    queue_url="https://sqs.ap-northeast-2.aseware",
    aws_region="ap-northeast-2",
)


# 2. 비동기 태스크 정의
@broker.task
async def calculate_sum(a: int, b: int) -> None:
    print(f"계산 중: {a} + {b}")
    await asyncio.sleep(2)
    print(f"결과: {a + b}")


async def main():
    # 브로커 시작
    await broker.startup()

    # 태스크를 SQS로 전송 (kiq)
    await calculate_sum.kiq(10, 20)

    # 브로커 종료
    await broker.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
