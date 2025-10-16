# TODO 공룡게임 구현

import pygame
pygame.init()

WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Game")

# 스프라이트 시트 불러오기 (파일명은 실제 파일명으로 변경)
sprite_sheet = pygame.image.load('dinosprite.png').convert_alpha()

# 공룡 스프라이트 위치와 크기 (예시값, 실제 위치/크기로 변경 필요)
dino_rect = pygame.Rect(40, 0, 88, 94)  # (x, y, w, h)
dino_img = sprite_sheet.subsurface(dino_rect)

dino_x, dino_y = 50, HEIGHT - 94  # 바닥에 맞춰 위치

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # 배경 흰색
    screen.blit(dino_img, (dino_x, dino_y))  # 공룡 그리기
    pygame.display.flip()

pygame.quit()