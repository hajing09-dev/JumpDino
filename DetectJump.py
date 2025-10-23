import cv2  # OpenCV 라이브러리 불러오기
import mediapipe as mp  # MediaPipe 라이브러리
import pyautogui  # 키 입력용


# MediaPipe 포즈 인식 모델 설정
mp_pose = mp.solutions.pose 
mp_drawing = mp.solutions.drawing_utils

# 포즈 인식 모델 초기화
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# 웹캠에서 비디오 캡처 시작
cap = cv2.VideoCapture(1)  # 0 = 아이폰 무선 연결, 1 = 외장 웹캠, 2 = 맥북 내장 카메라
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 60)

# 화면에 표시할 기준 선의 Y 좌표 (화면의 중앙)
line_y = 360 # 아이폰 카메라 기준 480, 맥북 내장 카메라 기준 360
 
last_signal = None  # 신호 중복 전송 방지용 변수

while cap.isOpened():  # 웹캠이 열려있는 동안 반복
    # 웹캠에서 프레임 읽기
    success, frame = cap.read()
    if not success:  # 프레임을 읽지 못한 경우 루프 종료
        break

    # MediaPipe는 RGB 포맷을 사용하므로 BGR을 RGB로 변환
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 포즈 인식 모델에 프레임을 전달하여 신체를 감지
    result = pose.process(frame_rgb)

    # 화면에 기준 선 그리기 (선의 시작, 끝 좌표와 색상 및 두께 지정)
    cv2.line(frame, (0, line_y), (2500, line_y), (255, 0, 0), 2)  # 화면에 파란색 수평선을 그림

    # 포즈(신체)가 감지된 경우
    signal = 'X'  # 기본값: 불 끄기
    if result.pose_landmarks:
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        head_y = result.pose_landmarks.landmark[0].y * frame.shape[0]
        hip_y = result.pose_landmarks.landmark[24].y * frame.shape[0]

        if hip_y < line_y:
            cv2.putText(frame, 'Jump', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            signal = 'R'
        elif head_y > line_y:
            cv2.putText(frame, 'Sneak', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            signal = 'B'
        else:
            cv2.putText(frame, 'None', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
            signal = 'X'
    else:
        cv2.putText(frame, 'None', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
        signal = 'X'

    # pyautogui로 키 입력 처리
    # 웅크리기: down키 누름/뗌
    if signal == 'B' and last_signal != 'B':
        pyautogui.keyDown('down')
    elif last_signal == 'B' and signal != 'B':
        pyautogui.keyUp('down')

    # 점프: space키 누름/뗌
    if signal == 'R' and last_signal != 'R':
        pyautogui.keyDown('space')
    elif last_signal == 'R' and signal != 'R':
        pyautogui.keyUp('space')

    last_signal = signal

    # 결과 프레임을 화면에 표시
    cv2.imshow('JumpDinoInput', frame)

    # 'q' 키를 눌러 프로그램 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 웹캠과 모든 창을 닫습니다.
cap.release()
cv2.destroyAllWindows()
