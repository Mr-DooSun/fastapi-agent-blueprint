# -*- coding: utf-8 -*-
import argparse
import signal
import subprocess
import sys
import time
from dotenv import load_dotenv

# 실행된 프로세스들을 저장할 리스트
running_processes = []

def signal_handler(signum, frame):
    """시그널 핸들러 - Ctrl+C 처리"""
    print("\n🛑 Shutting down services...")
    for process in running_processes:
        if process.poll() is None:  # 프로세스가 아직 실행 중인지 확인
            print(f"  Terminating process {process.pid}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"  Force killing process {process.pid}...")
                process.kill()
    print("✅ All services stopped!")
    sys.exit(0)

def run_user_service():
    """User 마이크로서비스 실행"""
    print("🟢 Starting User Service on port 8001...")
    process = subprocess.Popen([
        "uvicorn", "src.user.app:app", 
        "--reload", "--host", "127.0.0.1", "--port", "8001"
    ])
    running_processes.append(process)
    return process

def run_chat_service():
    """Chat 마이크로서비스 실행"""  
    print("🔵 Starting Chat Service on port 8002...")
    process = subprocess.Popen([
        "uvicorn", "src.chat.app:app",
        "--reload", "--host", "127.0.0.1", "--port", "8002" 
    ])
    running_processes.append(process)
    return process

def run_gateway():
    """Gateway 실행"""
    print("🟣 Starting Gateway on port 8000...")
    process = subprocess.Popen([
        "uvicorn", "src.apps.gateway.app:app",
        "--reload", "--host", "127.0.0.1", "--port", "8000"
    ])
    running_processes.append(process)
    return process

def main():
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, help="Environment (local, dev, prod)")
    parser.add_argument("--with-gateway", action="store_true", help="Run with Gateway")
    args = parser.parse_args()
    
    # 환경변수 로드
    load_dotenv(dotenv_path=f"_env/{args.env}.env", override=True)
    
    print("🚀 Starting Microservices...")
    
    try:
        # 마이크로서비스들 실행
        run_user_service()
        time.sleep(2)
        
        run_chat_service()
        time.sleep(2)
        
        if args.with_gateway:
            run_gateway()
        
        print("✅ All services started!")
        print("📊 Services:")
        print("   - User Service: http://localhost:8001/docs")
        print("   - Chat Service: http://localhost:8002/docs")
        if args.with_gateway:
            print("   - Gateway: http://localhost:8000/docs-swagger")
        
        print("\n🔥 Press Ctrl+C to stop all services")
        
        # 모든 프로세스가 종료될 때까지 대기
        while True:
            # 모든 프로세스가 종료되었는지 확인
            if all(process.poll() is not None for process in running_processes):
                print("🛑 All services have stopped")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        # signal_handler에서 처리하므로 여기서는 pass
        pass

if __name__ == "__main__":
    main()
