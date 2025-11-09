import pygame
import random
import os

# 화면 크기 설정
WIDTH, HEIGHT = 800, 400
pygame.init()
# 화면 생성: SCALED(해상도 스케일링) + DOUBLEBUF(더블 버퍼)
# vsync=1을 요청하면 지원되는 플랫폼에서 화면 찢김(tearing) 완화에 도움됨(항상 보장되지는 않음)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
pygame.display.set_caption('Jump Dino')
clock = pygame.time.Clock()
# 한글 표시: 프로젝트 폴더에 `fonts/` 폴더에 TTF/OTF 파일을 넣으면 우선 로드합니다.
# 없으면 시스템 폰트를 사용합니다.
FONT_DIR = os.path.join(os.path.dirname(__file__), 'fonts')
font = None
font_btn = None
try:
    if os.path.isdir(FONT_DIR):
        font_files = [n for n in os.listdir(FONT_DIR) if n.lower().endswith(('.ttf', '.otf'))]
    else:
        font_files = []
except Exception:
    font_files = []

if font_files:
    font_path = os.path.join(FONT_DIR, font_files[0])
    try:
        font = pygame.font.Font(font_path, 48)
        font_btn = pygame.font.Font(font_path, 36)
        print(f"Loaded font from {font_path}")
    except Exception as e:
        print(f"Warning: failed to load font {font_path}: {e}")
        font = pygame.font.SysFont("Apple SD Gothic Neo", 48)
        font_btn = pygame.font.SysFont("Apple SD Gothic Neo", 36)
else:
    # 폰트 파일이 없으면 시스템 폰트 사용
    font = pygame.font.SysFont("Apple SD Gothic Neo", 48)
    font_btn = pygame.font.SysFont("Apple SD Gothic Neo", 36)

# --- 스프라이트 로드 (달리기 2프레임, 스탠딩 1프레임) ---
SPRITES_DIR = os.path.join(os.path.dirname(__file__), 'sprites')
def load_image(name):
    path = os.path.join(SPRITES_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return img
    except Exception as e:
        print(f"Warning: failed to load sprite {path}: {e}")
        # 실패 시 투명한 표준 서피스 반환
        return pygame.Surface((40, 40), pygame.SRCALPHA)

# 필요한 프레임을 미리 로드
RUN_FRAMES = [load_image('dino_running.png'), load_image('dino_running_2.png')]
STAND_FRAME = load_image('dino_standing.png')
# Dino 출력 크기 조정(스케일링). 1.0 = 원본, 0.6 = 60% 크기
DINO_SCALE = 0.65
def _scale_frames(frames, scale):
    scaled = []
    for f in frames:
        w, h = f.get_size()
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        scaled.append(pygame.transform.smoothscale(f, (nw, nh)))
    return scaled

# 스프라이트를 축소하여 사용
RUN_FRAMES = _scale_frames(RUN_FRAMES, DINO_SCALE)
STAND_FRAME = pygame.transform.smoothscale(STAND_FRAME, _scale_frames([STAND_FRAME], DINO_SCALE)[0].get_size())

# --- 장애물 이미지 로드 ---
# sprites 폴더에서 obstacle_*.png 를 자동으로 찾아 로드합니다.
OBSTACLE_IMAGE_NAMES = [n for n in os.listdir(SPRITES_DIR) if n.lower().startswith('obstacle_') and n.lower().endswith('.png')]
OBSTACLE_IMAGES = [load_image(n) for n in OBSTACLE_IMAGE_NAMES]
# 장애물 이미지 스케일 비율 (예: 0.6 => 60%)
OBSTACLE_SCALE = 0.5
# 로드된 장애물 이미지가 있으면 지정한 스케일로 축소
if len(OBSTACLE_IMAGES) > 0:
    OBSTACLE_IMAGES = _scale_frames(OBSTACLE_IMAGES, OBSTACLE_SCALE)

# --- 클래스 및 함수 정의 ---
class Dino:
    def __init__(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y
        # y는 상단 y 좌표(기존 코드와 호환)
        self.y = ground_y
        # 스탠딩 프레임 크기를 기준으로 바운딩 설정
        w, h = STAND_FRAME.get_size()
        self.width = w
        self.height = h
        self.vel_y = 0
        self.jump_power = -15
        self.gravity = 1
        self.is_jumping = False
        # 애니메이션 타이머 (러닝 2프레임 순환)
        self.anim_idx = 0
        self.anim_t = 0.0
        self.anim_frame_time = 0.12
        # 현재 표시할 프레임
        self.current_frame = STAND_FRAME

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
        # 애니메이션: 점프 중에는 스탠딩 프레임, 지면에 있으면 러닝 애니메이션
        if self.is_jumping:
            self.current_frame = STAND_FRAME
            # 리셋 타이머(공중에서는 애니메이션 진행 X)
            self.anim_t = 0.0
            self.anim_idx = 0
        else:
            # 러닝 프레임 순환
            self.anim_t += dt
            if self.anim_t >= self.anim_frame_time:
                self.anim_t -= self.anim_frame_time
                self.anim_idx = (self.anim_idx + 1) % len(RUN_FRAMES)
            self.current_frame = RUN_FRAMES[self.anim_idx]

    def draw(self, surface):
        # 현재 애니메이션 프레임을 그립니다.
        # self.y는 '기준선(바닥 y)'로 사용하므로 이미지를 bottom-align 하여 그립니다.
        frame = getattr(self, 'current_frame', STAND_FRAME)
        fh = frame.get_height()
        draw_x = int(self.x)
        draw_y = int(self.y - fh)
        surface.blit(frame, (draw_x, draw_y))

class Obstacle:
    def __init__(self, x, ground_y):
        self.x = float(x)
        # 가능한 경우 이미지 기반 장애물 사용: sprites 폴더에서 불러온 OBSTACLE_IMAGES 사용
        if len(OBSTACLE_IMAGES) > 0:
            self.image = random.choice(OBSTACLE_IMAGES)
            self.width, self.height = self.image.get_size()
        else:
            self.image = None
            # 랜덤 너비/높이(픽셀)
            self.width = random.randint(30, 50)
            self.height = random.randint(40, 60)
        # y는 바닥(ground_y)을 기준으로 위로 올려서 정렬
        self.y = float(ground_y - self.height)
        # 속도를 픽셀/초로 설정(시간 기반 업데이트)
        # 기본 속도 범위를 상향 조정 (더 빠르게 이동)
        self.base_speed = OBSTACLE_BASE_SPEED
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
        # 이미지가 있으면 이미지로, 없으면 사각형으로 표시
        if getattr(self, 'image', None) is not None:
            surface.blit(self.image, (int(self.x), int(self.y)))
        else:
            # 어두운 배경에서 보이도록 밝은 회색으로 장애물 표현
            pygame.draw.rect(surface, (200, 200, 200), (self.x, self.y, self.width, self.height))

def check_collision(dino, obs):
    # 충돌 판정: Dino는 self.y를 '바닥 기준선(ground_y)'로 사용하므로
    # 현재 표시중인 프레임 크기를 이용해 실제 top y를 계산한다.
    # obstacle은 이미 top-y 기준(self.y)으로 설정되어 있음.
    try:
        frame = getattr(dino, 'current_frame')
        dw, dh = frame.get_size()
    except Exception:
        dw, dh = dino.width, dino.height
    dino_top = int(dino.y - dh)
    dino_rect = pygame.Rect(int(dino.x), dino_top, int(dw), int(dh))
    obs_rect = pygame.Rect(int(obs.x), int(obs.y), int(obs.width), int(obs.height))
    return dino_rect.colliderect(obs_rect)

def draw_button(surface, text, rect, color, text_color):
    pygame.draw.rect(surface, color, rect)
    # 전역으로 생성된 font_btn 사용
    txt = font_btn.render(text, True, text_color)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)

def reset_game():
    global dino, obstacles, spawn_timer, score, game_over
    # Dino의 기준선(바닥 y)을 장애물과 일치시키기 위해 HEIGHT-40을 사용
    dino = Dino(50, HEIGHT - 40)
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
# 기본 장애물 속도(픽셀/초) - 고정값으로 설정하면 모든 장애물의 base_speed가 동일해짐
OBSTACLE_BASE_SPEED = 450.0

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

    # 배경 지우기 (어두운 색)
    screen.fill((20, 20, 20))

    if not game_over:
        # 키 상태 읽기 (로컬 테스트용)
        keys = pygame.key.get_pressed()
        # 현재는 점프(스페이스)만 사용합니다. 웅크리기 기능은 추후 추가 예정
        jump_signal = keys[pygame.K_SPACE]
        signal_text = "점프" if jump_signal else "없음"
        # 화면에 현재 신호 표시 (디버그/테스트 목적) - 어두운 배경에서는 밝은 색으로
        text_surface = font.render(f"신호: {signal_text}", True, (255, 255, 255))
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
                # 레벨 기반 속도 보정
                # level = score // 5 (예: 0..4 = 레벨0, 5..9 = 레벨1, ...)
                level = score // 5
                # level 당 10% 속도 증가(e.g., level=1 => 1.1배)
                speed_scale = 1.0 + (level * 0.10)
                obs = Obstacle(WIDTH, HEIGHT - 40)
                # Obstacle의 base_speed를 고정 상수로 덮어쓰기
                obs.base_speed = OBSTACLE_BASE_SPEED
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

        # 점수 표시 (밝은 색)
        score_surface = font.render(f"점수: {score}", True, (255, 255, 255))
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