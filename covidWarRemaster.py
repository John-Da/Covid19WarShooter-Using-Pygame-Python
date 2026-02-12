import pygame
import random
import sys

# ======================================
# CONFIG
# ======================================
BASE_WIDTH = 600
BASE_HEIGHT = 800
FPS = 60

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSE = "pause"
STATE_GAMEOVER = "gameover"

GAME_DURATION = 600
MAX_WAVES = 5

pygame.init()
pygame.mixer.init()

# ======================================
# CONTROLLER INIT
# ======================================
pygame.joystick.init()
controller = None

if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()
    print("🎮 Controller connected:", controller.get_name())
else:
    print("⚠ No controller detected - keyboard controls available")

# ===== WINDOW (MAXIMIZED SAFE) =====
window = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
pygame.display.set_caption("Covid19War")

game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("arial", 64, bold=True)
font = pygame.font.SysFont("arial", 26, bold=True)

# ======================================
# AUDIO
# ======================================
music_on = True
sound_on = True


def play_music():
    if music_on:
        try:
            pygame.mixer.music.load("sounds/music.ogg")
            pygame.mixer.music.play(-1)
        except:
            pass


def stop_music():
    pygame.mixer.music.stop()


try:
    boom_sound = pygame.mixer.Sound("boom.wav")
except:
    boom_sound = None

# ======================================
# BACKGROUND (FIXED IMAGE)
# ======================================
try:
    bg = pygame.image.load("bg.png").convert()
    bg = pygame.transform.scale(bg, (BASE_WIDTH, BASE_HEIGHT))
except:
    bg = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    bg.fill((20, 20, 40))

# ======================================
# EFFECTS
# ======================================
shake_timer = 0


# ======================================
# BUTTON CLASS
# ======================================
class Button:
    def __init__(self, text, y):
        self.text = text
        self.y = y

    def draw(self, surf, selected=False):
        size = 42 if selected else 30
        f = pygame.font.SysFont("arial", size, bold=True)
        color = (0, 255, 255) if selected else (140, 140, 140)
        txt = f.render(self.text, True, color)
        rect = txt.get_rect(center=(BASE_WIDTH // 2, self.y))
        surf.blit(txt, rect)


# ======================================
# START MENU
# ======================================
class StartMenu:
    def __init__(self):
        self.index = 0
        self.buttons = [
            Button("Start Game", 350),
            Button("Music: ON", 430),
            Button("Sound: ON", 510),
            Button("Exit", 590),
        ]
        self.update_text()

    def update_text(self):
        self.buttons[1].text = f"Music: {'ON' if music_on else 'OFF'}"
        self.buttons[2].text = f"Sound: {'ON' if sound_on else 'OFF'}"

    def move(self, d):
        self.index = (self.index + d) % len(self.buttons)

    def select(self):
        global game_state, music_on, sound_on

        if self.index == 0:
            reset_game()
            game_state = STATE_PLAYING

        elif self.index == 1:
            music_on = not music_on
            if music_on:
                play_music()
            else:
                stop_music()

        elif self.index == 2:
            sound_on = not sound_on

        elif self.index == 3:
            pygame.quit()
            sys.exit()

        self.update_text()

    def draw(self, surf):
        surf.blit(bg, (0, 0))
        title = font_big.render("Injection Release", True, (0, 255, 255))
        surf.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 150))

        for i, b in enumerate(self.buttons):
            b.draw(surf, i == self.index)


# ======================================
# PAUSE MENU
# ======================================
class PauseMenu:
    def __init__(self):
        self.index = 0
        self.buttons = [
            Button("Resume", 340),
            Button("Main Menu", 420),
            Button("Music: ON", 500),
            Button("Sound: ON", 580),
        ]
        self.update_text()

    def update_text(self):
        self.buttons[2].text = f"Music: {'ON' if music_on else 'OFF'}"
        self.buttons[3].text = f"Sound: {'ON' if sound_on else 'OFF'}"

    def move(self, d):
        self.index = (self.index + d) % len(self.buttons)

    def select(self):
        global game_state, music_on, sound_on

        if self.index == 0:
            game_state = STATE_PLAYING

        elif self.index == 1:
            game_state = STATE_MENU

        elif self.index == 2:
            music_on = not music_on
            if music_on:
                play_music()
            else:
                stop_music()

        elif self.index == 3:
            sound_on = not sound_on

        self.update_text()

    def draw(self, surf):
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        overlay.set_alpha(100)  # Reduced from 180 to 100 for better visibility
        overlay.fill((0, 0, 0))
        surf.blit(overlay, (0, 0))

        title = font_big.render("GAME PAUSED", True, (0, 255, 255))
        surf.blit(title, (BASE_WIDTH // 2 - title.get_width() // 2, 180))

        for i, b in enumerate(self.buttons):
            b.draw(surf, i == self.index)


# ======================================
# PLAYER
# ======================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            # Load with alpha channel for transparency
            img1 = pygame.image.load("JiJiSR1.png").convert_alpha()
            img2 = pygame.image.load("JiJiSR1L.png").convert_alpha()
            img3 = pygame.image.load("JiJiSR1R.png").convert_alpha()
            self.images = [img1, img2, img3]
        except:
            # Fallback if images don't exist
            self.images = [pygame.Surface((40, 60), pygame.SRCALPHA) for _ in range(3)]
            for img in self.images:
                pygame.draw.polygon(img, (0, 255, 255), [(20, 0), (0, 60), (40, 60)])

        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=(BASE_WIDTH // 2, BASE_HEIGHT - 40))
        self.speedx = 0
        self.life = 100
        self.score = 0
        self.hit_cooldown = 0

    def update(self):
        self.rect.x += self.speedx
        self.rect.clamp_ip(pygame.Rect(0, 0, BASE_WIDTH, BASE_HEIGHT))

        if self.speedx < 0:
            self.image = self.images[1]
        elif self.speedx > 0:
            self.image = self.images[2]
        else:
            self.image = self.images[0]

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def shoot(self):
        b = Cure(self.rect.centerx, self.rect.top)
        allsprites.add(b)
        cures.add(b)


# ======================================
# ENEMY
# ======================================
class Covid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("covid19.png").convert_alpha()
        except:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 50, 50), (15, 15), 15)

        self.rect = self.image.get_rect()
        self.respawn()

    def respawn(self):
        self.rect.x = random.randrange(BASE_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 6)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > BASE_HEIGHT:
            self.respawn()


# ======================================
# BULLET
# ======================================
class Cure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.orig = pygame.image.load("cure.png").convert_alpha()
        except:
            self.orig = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.orig, (0, 255, 0), (10, 10), 10)

        self.image = self.orig
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.speedy = -8
        self.rot = 0

    def update(self):
        self.rect.y += self.speedy
        self.rot += 15

        # Rotate with transparency preserved
        rotated = pygame.transform.rotate(self.orig, self.rot)
        self.image = rotated

        # Update rect to keep it centered (rotation changes size)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        if self.rect.bottom < 0:
            self.kill()


# ======================================
# EXPLOSION
# ======================================
class Explosion:
    def __init__(self, pos):
        self.pos = pos
        self.radius = 10
        self.alpha = 255

    def update(self):
        self.radius += 3
        self.alpha -= 12

    def draw(self, surf):
        if self.alpha > 0:
            s = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 200, 0, self.alpha), (100, 100), self.radius, 3)
            surf.blit(s, (self.pos[0] - 100, self.pos[1] - 100))


explosions = []


# ======================================
# FLOATING TEXT (POINTS)
# ======================================
class FloatingText:
    def __init__(self, pos, text, points=100):
        self.pos = list(pos)
        self.text = text
        self.points = points
        self.alpha = 255
        self.lifetime = 90  # 1.5 seconds at 60 FPS
        self.age = 0

        # Choose color based on points
        if points >= 100:
            self.color = (0, 255, 255)  # Cyan for normal
        else:
            self.color = (255, 255, 0)  # Yellow for special

    def update(self):
        self.age += 1
        self.pos[1] -= 1  # Float upward

        # Fade out in the last 0.5 seconds
        if self.age > 60:
            self.alpha = int(255 * (1 - (self.age - 60) / 30))

        return self.age < self.lifetime

    def draw(self, surf):
        if self.alpha > 0:
            f = pygame.font.SysFont("arial", 28, bold=True)
            txt = f.render(f"+{self.points}", True, (*self.color, self.alpha))
            rect = txt.get_rect(center=(self.pos[0], self.pos[1]))

            # Add outline for better visibility
            outline_f = pygame.font.SysFont("arial", 28, bold=True)
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                outline = outline_f.render(f"+{self.points}", True, (0, 0, 0))
                surf.blit(outline, (rect.x + dx, rect.y + dy))

            surf.blit(txt, rect)


floating_texts = []


# ======================================
# RESET GAME
# ======================================
def reset_game():
    global allsprites, covids, cures, player, game_start_time, current_wave

    allsprites = pygame.sprite.Group()
    covids = pygame.sprite.Group()
    cures = pygame.sprite.Group()

    player = Player()
    allsprites.add(player)

    for i in range(6):
        c = Covid()
        allsprites.add(c)
        covids.add(c)

    game_start_time = pygame.time.get_ticks()
    current_wave = 1


# ======================================
# CENTER DRAW + SHAKE
# ======================================
def draw_centered():
    global shake_timer

    window.fill((0, 0, 0))
    win_w, win_h = window.get_size()

    scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)
    new_w = int(BASE_WIDTH * scale)
    new_h = int(BASE_HEIGHT * scale)

    scaled = pygame.transform.scale(game_surface, (new_w, new_h))

    x = (win_w - new_w) // 2
    y = (win_h - new_h) // 2

    if shake_timer > 0:
        x += random.randint(-12, 12)  # Increased shake intensity
        y += random.randint(-12, 12)
        shake_timer -= 1

    window.blit(scaled, (x, y))


# ======================================
# SIDE UI
# ======================================
def draw_side_ui():
    win_w, _ = window.get_size()
    if win_w > BASE_WIDTH:
        right = win_w - 200

        window.blit(font.render(f"Score: {player.score}", True, (0, 255, 255)), (right, 60))
        window.blit(font.render(f"HP: {player.life}", True, (0, 255, 255)), (right, 110))
        pygame.draw.rect(window, (255, 255, 255), (right, 140, 120, 12))
        pygame.draw.rect(window, (0, 255, 255), (right, 140, player.life, 12))
        window.blit(font.render(f"Wave {current_wave}/{MAX_WAVES}", True, (255, 255, 0)), (right, 190))
        pygame.draw.rect(window, (255, 255, 255), (right, 220, 120, 12))
        pygame.draw.rect(window, (255, 255, 0), (right, 220, int((current_wave / MAX_WAVES) * 120), 12))


# ======================================
# CONTROLLER HELPERS
# ======================================
def is_pause_button(button_num):
    """
    Check if button is a pause/start button
    Common mappings:
    - Xbox controller: button 7 (Start)
    - PlayStation: button 9 (Options)
    - Nintendo Switch Pro: button 10 (Plus)
    - Some controllers: button 6
    """
    return button_num in [6, 7, 9, 10]


def is_action_button(button_num):
    """Primary action button (A/Cross/B)"""
    return button_num == 0


def is_back_button(button_num):
    """Back/Select button"""
    return button_num in [1, 6, 8]


def is_dpad_up(button_num):
    """D-pad Up (Nintendo Switch Pro: button 11)"""
    return button_num == 11


def is_dpad_down(button_num):
    """D-pad Down (Nintendo Switch Pro: button 12)"""
    return button_num == 12


def is_dpad_left(button_num):
    """D-pad Left (Nintendo Switch Pro: button 13)"""
    return button_num == 13


def is_dpad_right(button_num):
    """D-pad Right (Nintendo Switch Pro: button 14)"""
    return button_num == 14


# ======================================
# INIT
# ======================================
start_menu = StartMenu()
pause_menu = PauseMenu()
play_music()

game_state = STATE_MENU
high_score = 0
running = True
gameover_time = 0

# Variables to prevent keyboard/controller conflicts during gameplay
keyboard_control_active = False

# ======================================
# MAIN LOOP
# ======================================
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ==================== MENU STATE ====================
        if game_state == STATE_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    start_menu.move(-1)
                elif event.key == pygame.K_DOWN:
                    start_menu.move(1)
                elif event.key == pygame.K_RETURN:
                    start_menu.select()

            # Controller D-pad for menu navigation (hat motion)
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:  # Up
                    start_menu.move(-1)
                elif event.value[1] == -1:  # Down
                    start_menu.move(1)

            # Controller buttons in menu
            elif event.type == pygame.JOYBUTTONDOWN:
                # print(f"🎮 Menu - Button {event.button} pressed")

                # D-pad navigation (Nintendo Switch Pro controller uses buttons)
                if is_dpad_up(event.button):
                    start_menu.move(-1)
                elif is_dpad_down(event.button):
                    start_menu.move(1)
                elif is_action_button(event.button):
                    start_menu.select()
                elif is_pause_button(event.button):
                    # Start button can also select in menu
                    start_menu.select()

        # ==================== PLAYING STATE ====================
        elif game_state == STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_PAUSE
                    # print("⏸ Paused via keyboard")
                elif event.key == pygame.K_LEFT:
                    player.speedx = -6
                    keyboard_control_active = True
                elif event.key == pygame.K_RIGHT:
                    player.speedx = 6
                    keyboard_control_active = True
                elif event.key == pygame.K_SPACE:
                    player.shoot()

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if keyboard_control_active:
                        player.speedx = 0

            # Controller buttons during gameplay
            elif event.type == pygame.JOYBUTTONDOWN:
                # print(f"🎮 Game - Button {event.button} pressed")

                # Check for pause button FIRST (most important)
                if is_pause_button(event.button):
                    game_state = STATE_PAUSE
                    # print(f"⏸ Paused via controller button {event.button}")

                # Shoot button (A/Cross/B)
                elif is_action_button(event.button):
                    player.shoot()
                    # print("💉 Shot fired")

                # D-pad movement (Nintendo Switch Pro - press and hold)
                elif is_dpad_left(event.button):
                    player.speedx = -6
                    keyboard_control_active = False
                elif is_dpad_right(event.button):
                    player.speedx = 6
                    keyboard_control_active = False

                # Debug - show unmapped buttons
                else:
                    print(f"❓ Unmapped button {event.button}")

            # D-pad button release (Nintendo Switch Pro)
            elif event.type == pygame.JOYBUTTONUP:
                if is_dpad_left(event.button) or is_dpad_right(event.button):
                    # Only stop if analog stick is also centered
                    if controller and abs(controller.get_axis(0)) < 0.2:
                        player.speedx = 0

            # D-pad for movement (hat motion - for other controllers)
            elif event.type == pygame.JOYHATMOTION:
                if event.value[0] == -1:  # Left
                    player.speedx = -6
                    keyboard_control_active = False
                elif event.value[0] == 1:  # Right
                    player.speedx = 6
                    keyboard_control_active = False
                elif event.value[0] == 0:  # Centered
                    # Only stop if analog stick is also centered
                    if controller and abs(controller.get_axis(0)) < 0.2:
                        player.speedx = 0

        # ==================== PAUSE STATE ====================
        elif game_state == STATE_PAUSE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_PLAYING
                    # print("▶ Resumed via keyboard")
                elif event.key == pygame.K_UP:
                    pause_menu.move(-1)
                elif event.key == pygame.K_DOWN:
                    pause_menu.move(1)
                elif event.key == pygame.K_RETURN:
                    pause_menu.select()

            # Controller D-pad in pause menu (hat motion)
            elif event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1:  # Up
                    pause_menu.move(-1)
                elif event.value[1] == -1:  # Down
                    pause_menu.move(1)

            # Controller buttons in pause menu
            elif event.type == pygame.JOYBUTTONDOWN:
                # print(f"🎮 Pause - Button {event.button} pressed")

                # D-pad navigation (Nintendo Switch Pro controller uses buttons)
                if is_dpad_up(event.button):
                    pause_menu.move(-1)
                elif is_dpad_down(event.button):
                    pause_menu.move(1)
                elif is_action_button(event.button):
                    pause_menu.select()
                elif is_pause_button(event.button):
                    # Pressing pause again resumes
                    game_state = STATE_PLAYING
                    # print(f"▶ Resumed via controller button {event.button}")

        # ==================== GAME OVER STATE ====================
        elif game_state == STATE_GAMEOVER:
            # Allow any button to skip to menu
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                if pygame.time.get_ticks() - gameover_time > 1000:  # Prevent accidental skip
                    game_state = STATE_MENU

    # ==================== UPDATE ====================
    if game_state == STATE_PLAYING:

        # Analog stick control (overrides keyboard if active)
        if controller:
            axis = controller.get_axis(0)
            if abs(axis) > 0.2:
                player.speedx = int(axis * 8)
                keyboard_control_active = False
            elif not keyboard_control_active:
                # Only reset speed if keyboard isn't being used
                player.speedx = 0

        allsprites.update()

        # Collision: bullets hit enemies
        hits = pygame.sprite.groupcollide(covids, cures, True, True)
        for h in hits:
            player.score += 100
            if sound_on and boom_sound:
                boom_sound.play()
            explosions.append(Explosion(h.rect.center))

            # Add floating "+100" text
            floating_texts.append(FloatingText(h.rect.center, "+100", 100))

            # Spawn new enemy
            c = Covid()
            allsprites.add(c)
            covids.add(c)

        # Collision: enemies hit player
        hits = pygame.sprite.spritecollide(player, covids, False)
        if hits and player.hit_cooldown == 0:
            player.life -= 10
            player.hit_cooldown = 60
            shake_timer = 15  # Screen shake duration
            if sound_on and boom_sound:
                boom_sound.play()

            if player.life <= 0:
                if player.score > high_score:
                    high_score = player.score
                gameover_time = pygame.time.get_ticks()
                game_state = STATE_GAMEOVER

        # Wave progression
        elapsed = (pygame.time.get_ticks() - game_start_time) / 1000
        new_wave = int(elapsed // 120) + 1
        if new_wave != current_wave and new_wave <= MAX_WAVES:
            current_wave = new_wave
            # Spawn more enemies each wave
            for i in range(3 + current_wave):
                c = Covid()
                allsprites.add(c)
                covids.add(c)

        # Update explosions
        for e in explosions:
            e.update()
        explosions[:] = [e for e in explosions if e.alpha > 0]

        # Update floating texts
        floating_texts[:] = [ft for ft in floating_texts if ft.update()]

    # ==================== DRAW ====================
    game_surface.fill((0, 0, 0))

    if game_state == STATE_MENU:
        start_menu.draw(game_surface)

    elif game_state == STATE_PLAYING:
        game_surface.blit(bg, (0, 0))
        allsprites.draw(game_surface)
        for e in explosions:
            e.draw(game_surface)
        for ft in floating_texts:
            ft.draw(game_surface)

    elif game_state == STATE_PAUSE:
        # Draw game underneath
        game_surface.blit(bg, (0, 0))
        allsprites.draw(game_surface)
        for e in explosions:
            e.draw(game_surface)

        # Draw pause menu on top
        pause_menu.draw(game_surface)

    elif game_state == STATE_GAMEOVER:
        game_surface.fill((0, 0, 0))
        t1 = font_big.render("MISSION END", True, (0, 255, 255))
        t2 = font.render(f"Score {player.score}", True, (255, 255, 255))
        t3 = font.render(f"Best {high_score}", True, (255, 255, 0))
        t4 = font.render("Press any key to continue", True, (140, 140, 140))

        game_surface.blit(t1, (BASE_WIDTH // 2 - t1.get_width() // 2, 300))
        game_surface.blit(t2, (BASE_WIDTH // 2 - t2.get_width() // 2, 420))
        game_surface.blit(t3, (BASE_WIDTH // 2 - t3.get_width() // 2, 460))

        # Blinking text
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            game_surface.blit(t4, (BASE_WIDTH // 2 - t4.get_width() // 2, 550))

        # Auto-return to menu after 8 seconds
        if pygame.time.get_ticks() - gameover_time > 8000:
            game_state = STATE_MENU

    draw_centered()

    if game_state == STATE_PLAYING:
        draw_side_ui()

    pygame.display.update()