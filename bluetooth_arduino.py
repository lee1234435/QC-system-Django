import serial
import time

def main():
    bluetooth_port = "COM4"  # 실제 블루투스 시리얼 포트로 변경
    baud_rate = 115200

    try:
        # 시리얼 연결 초기화
        bluetooth_serial = serial.Serial(bluetooth_port, baud_rate)
        time.sleep(2)  # 초기화를 위해 대기

        while True:
            command = input("명령어 입력 (1: UP, 2: DOWN, q: Quit): ")
            
            if command == 'q':
                print("종료합니다...")
                break
            elif command in ['1', '2']:
                bluetooth_serial.write(command.encode())
                print(f"명령어 전송: {command}")
            else:
                print("잘못된 명령어입니다. 1, 2, 또는 q를 입력하세요.")
            
            time.sleep(1)  # 명령어 사이에 딜레이

    except serial.SerialException as e:
        print(f"시리얼 포트를 여는 중 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    finally:
        if 'bluetooth_serial' in locals() and bluetooth_serial.is_open:
            bluetooth_serial.close()
            print("시리얼 연결을 닫았습니다.")

if __name__ == "__main__":
    main()