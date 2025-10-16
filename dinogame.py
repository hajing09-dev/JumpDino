import pygame

WIDTH, HEIGHT = 800, 400
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.DOUBLEBUF)
pygame.display.set_caption('Jump Dino')
clock = pygame.time.Clock()
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
    def update(self, jump_signal):
        if jump_signal and not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True
        self.vel_y += self.gravity
        self.y += self.vel_y
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.vel_y = 0
            self.is_jumping = False
    def draw(self, surface):
        pygame.draw.rect(surface, (0, 200, 0), (self.x, int(self.y), self.width, self.height))

class Obstacle:
    def __init__(self, x, ground_y):
        self.x = x
        self.y = ground_y
        self.width = 20
        self.height = 60
        self.speed = 8
    def update(self):
        self.x -= self.speed
    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height))

def check_collision(dino, obs):
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
spawn_timer = 0
reset_game()

# --- 메인 루프 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_over:
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                reset_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()

    screen.fill((255, 255, 255))

    if not game_over:
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
        text_surface = font.render(f"신호: {signal_text}", True, (0, 0, 0))
        screen.blit(text_surface, (100, 150))

        dino.update(jump_signal)
        dino.draw(screen)

        spawn_timer += 1
        if spawn_timer > 60:
            obstacles.append(Obstacle(WIDTH, HEIGHT - 80))
            spawn_timer = 0

        for obs in obstacles[:]:
            obs.update()
            obs.draw(screen)
            if obs.x < -obs.width:
                obstacles.remove(obs)
            if check_collision(dino, obs):
                game_over = True

        score += 1
        score_surface = font.render(f"점수: {score}", True, (0, 0, 255))
        screen.blit(score_surface, (100, 100))

    else:
        over_surface = font.render(f"게임 오버! 점수: {score}", True, (255, 0, 0))
        screen.blit(over_surface, (WIDTH//2 - over_surface.get_width()//2, HEIGHT//2 - 40))
        draw_button(screen, "다시 시작", button_rect, (0, 200, 0), (255,255,255))
  
    pygame.display.flip()
    clock.tick(60)

pygame.quit()