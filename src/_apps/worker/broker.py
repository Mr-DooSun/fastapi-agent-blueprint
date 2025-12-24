from taskiq_aws import SQSBroker

# 전역 브로커 인스턴스 생성
# 설정은 app.py에서 초기화 시 주입되거나, 환경 변수를 통해 로드될 수 있습니다.
# 초기에는 빈 설정으로 생성하고 startup 시점에 구체적인 설정을 할 수도 있으나,
# taskiq는 보통 정의 시점에 브로커를 확정하는 것이 일반적입니다.
# 다만, 순환 참조를 피하기 위해 여기서 객체를 생성합니다.

broker = SQSBroker(
    url="",  # app.py에서 설정 값으로 오버라이드 예정
)
