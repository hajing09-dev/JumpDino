import pygame
import random

# 화면 크기 설정
WIDTH, HEIGHT = 800, 400
pygame.init()
# 화면 생성: SCALED(해상도 스케일링) + DOUBLEBUF(더블 버퍼)
# vsync=1을 요청하면 지원되는 플랫폼에서 화면 찢김(tearing) 완화에 도움됨(항상 보장되지는 않음)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
pygame.display.set_caption('Jump Dino')
clock = pygame.time.Clock()
# 한글 표시를 위해 시스템 한글 폰트 사용
font = pygame.font.SysFont("Apple SD Gothic Neo", 48)

# --- 클래스 및 함수 정의 ---
class Dino:
    def __init__(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y
        self.width = 40
        self.height = 40
        self.vel_y = 0
        self.jump_power = -15
        self.gravity = 1
        self.is_jumping = False
    def update(self, jump_signal, dt):
        """
        점프 및 중력 업데이트 (시간 기반)

        입력:
        - jump_signal: bool (스페이스 키 or 외부 신호)
        - dt: float, 프레임 간 시간(초) 예: 0.016

        물리 단위:
        - jump_power는 픽셀/프레임의 초기 속도(음수 = 위로)
        - gravity는 가속도 상수(프레임 단위 보정에 dt*60.0을 사용)

        구현 노트:
        - dt를 사용해 프레임레이트에 독립적인 동작을 보장합니다.
        - jump_power와 gravity 값은 조정 포인트입니다(더 높게/낮게 설정 가능).
        """
        if jump_signal and not self.is_jumping:
            # 점프 시작: 초기 수직 속도 부여
            self.vel_y = self.jump_power
            self.is_jumping = True
        # 중력 적용: dt와 기준 프레임(60fps)을 곱해 보정
        self.vel_y += self.gravity * dt * 60.0
        # 위치 업데이트: 속도는 픽셀/프레임 유사 단위이므로 dt*60으로 보정
        self.y += self.vel_y * dt * 60.0
        # 지면에 닿으면 보정
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vel_y = 0
            self.is_jumping = False

    def draw(self, surface):
         # 현재는 단순한 색칠된 사각형으로 표현
        pygame.draw.rect(surface, (0, 200, 0), (self.x, int(self.y), self.width, self.height))

class Obstacle:
    def __init__(self, x, ground_y):
        self.x = float(x)
        # 랜덤 너비/높이(픽셀)
        self.width = random.randint(20, 60)
        self.height = random.randint(30, 70)
        # y는 바닥(ground_y)을 기준으로 위로 올려서 정렬
        self.y = float(ground_y - self.height)
        # 속도를 픽셀/초로 설정(시간 기반 업데이트)
        # 기본 속도 범위를 상향 조정 (더 빠르게 이동)
        self.base_speed = float(random.randint(300, 600))
        # 실제 속도는 생성 시 외부에서 보정 가능 (spawn logic에서 설정)
        self.speed = self.base_speed
        self.passed = False
    def update(self, dt):
        """
        시간(dt 초)를 받아 x 위치를 왼쪽으로 이동시킵니다.
        - self.speed는 픽셀/초 단위
        - dt는 초 단위이므로 self.speed * dt를 빼서 이동
        """
        self.x -= self.speed * dt

    def draw(self, surface):
        # 현재는 검정색 사각형으로 장애물 표현
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height))

def check_collision(dino, obs):
    # 충돌 판정: pygame.Rect의 colliderect 사용
    dino_rect = pygame.Rect(dino.x, int(dino.y), dino.width, dino.height)
    obs_rect = pygame.Rect(obs.x, obs.y, obs.width, obs.height)
    return dino_rect.colliderect(obs_rect)

def draw_button(surface, text, rect, color, text_color):
    pygame.draw.rect(surface, color, rect)
    font_btn = pygame.font.SysFont("Apple SD Gothic Neo", 36)
    txt = font_btn.render(text, True, text_color)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)

def reset_game():
    global dino, obstacles, spawn_timer, score, game_over
    dino = Dino(50, HEIGHT - 80)
    obstacles = []
    spawn_timer = 0
    score = 0
    game_over = False

# --- 변수 초기화 ---
button_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 40, 160, 50)
obstacles = []
score = 0
game_over = False
spawn_timer = 0.0
reset_game()
# 장애물 간 최소 거리 (픽셀)
min_gap = 220
# 초기 스폰 간격(초)
spawn_interval = random.uniform(0.8, 2.0)

# --- 메인 루프 ---
running = True
prev_time = pygame.time.get_ticks() / 1000.0
while running:
    # delta time (초)
    current_time = pygame.time.get_ticks() / 1000.0
    dt = current_time - prev_time
    prev_time = current_time
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                reset_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()

    # 배경 지우기
    screen.fill((255, 255, 255))

    if not game_over:
        # 키 상태 읽기 (로컬 테스트용)
        keys = pygame.key.get_pressed()
        signal_text = ""
        jump_signal = keys[pygame.K_SPACE]
        sneak_signal = keys[pygame.K_DOWN]
        if jump_signal:
            signal_text += "점프 "
        if sneak_signal:
            signal_text += "웅크리기 "
        if not signal_text:
            signal_text = "없음"
        # 화면에 현재 신호 표시 (디버그/테스트 목적)
        text_surface = font.render(f"신호: {signal_text}", True, (0, 0, 0))
        screen.blit(text_surface, (100, 150))

        # --- Dino 업데이트: dt(초)를 사용하여 프레임 독립 동작 보장 ---
        dino.update(jump_signal, dt)
        dino.draw(screen)

        # --- 장애물 스폰 로직(시간 기반) ---
        # spawn_timer는 초 단위 누적
        spawn_timer += dt
        if spawn_timer > spawn_interval:
            # 마지막 장애물의 x가 충분히 왼쪽에 있으면 스폰
            # (장애물이 너무 붙어 나오지 않도록 min_gap으로 보호)
            if len(obstacles) == 0 or obstacles[-1].x < WIDTH - min_gap:
                # 난이도(점수)에 따라 속도 보정: score 증가 시 속도 증가
                # speed_scale 계수는 난이도 곡선 조정 포인트
                speed_scale = 1.0 + (score * 0.05)
                obs = Obstacle(WIDTH, HEIGHT - 40)
                obs.speed = obs.base_speed * speed_scale
                obstacles.append(obs)
                spawn_timer = 0.0
                # 다음 스폰 간격은 랜덤화
                spawn_interval = random.uniform(0.8, 2.0)
            else:
                # 아직 간격이 부족하면 일부만 타이머를 리셋하여 재시도
                spawn_timer = spawn_interval * 0.5

        # --- 장애물 업데이트 및 충돌/점수 판정 ---
        for obs in obstacles[:]:
            obs.update(dt)
            obs.draw(screen)
            # 화면 왼쪽으로 완전히 벗어나면 리스트에서 제거
            if obs.x < -obs.width:
                obstacles.remove(obs)
            # 충돌 판정이 참이면 게임 오버 플래그 설정
            if check_collision(dino, obs):
                game_over = True

            # 장애물을 완전히 지나갈 때만 점수 증가 (중복 카운트 방지 위해 passed 사용)
            if not obs.passed and obs.x + obs.width < dino.x:
                obs.passed = True
                score += 1

        # 점수 표시
        score_surface = font.render(f"점수: {score}", True, (0, 0, 255))
        screen.blit(score_surface, (100, 100))

    else:
        # 게임 오버 화면: 점수 표시 및 다시 시작 버튼
        over_surface = font.render(f"게임 오버! 점수: {score}", True, (255, 0, 0))
        screen.blit(over_surface, (WIDTH//2 - over_surface.get_width()//2, HEIGHT//2 - 40))
        draw_button(screen, "다시 시작", button_rect, (0, 200, 0), (255,255,255))
  
    # 화면 갱신 및 프레임 제한
    pygame.display.flip()
    # tick(60)은 최대 60FPS로 제한. 필요시 clock.tick_busy_loop(60)로 더 빡세게 제어 가능
    clock.tick(60)

pygame.quit()