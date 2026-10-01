
import pygame
import random
import math
from array import array
from .fruit import Fruit

# Game Engine

WHITE = (255, 255, 255)
BOMB_BLACK = (30, 30, 30)
FRUIT_COLORS = [
    (220, 60, 60),
    (230, 140, 40),
    (230, 200, 40),
    (90, 180, 90)
]


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.fruits = []
        self.trail = []  # recent mouse positions, drawn as the "blade"
        self.previous_mouse_pos = None

        # -------------------------
        # TASK 3: DIFFICULTY
        # -------------------------
        self.difficulty = "Medium"

        self.spawn_interval = 55
        self._spawn_timer = 0
        self.bomb_chance = 0.15
        self.speed_scale = 1.0

        self.lives = 3
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 28)
        self.game_over = False

        # -------------------------
        # TASK 4: SOUND
        # -------------------------
        self.fruit_sound = None
        self.bomb_sound = None
        self.game_over_sound = None
        self.game_over_sound_played = False

        self._setup_sounds()

    # =========================================================
    # TASK 4: SOUND SETUP
    # =========================================================

    def _setup_sounds(self):
        """
        Create simple generated tones.

        No external sound files are required.
        If the audio mixer cannot be initialized, the game
        continues without sound.
        """
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=1,
                    buffer=512
                )

            # Fruit sliced = short high tone
            self.fruit_sound = self._create_tone(
                frequency=700,
                duration=0.08,
                volume=0.25
            )

            # Bomb hit = short low tone
            self.bomb_sound = self._create_tone(
                frequency=180,
                duration=0.20,
                volume=0.35
            )

            # Game over = two-tone sound
            tone1 = self._create_tone(
                frequency=300,
                duration=0.18,
                volume=0.35
            )

            tone2 = self._create_tone(
                frequency=150,
                duration=0.30,
                volume=0.35
            )

            if tone1 and tone2:
                self.game_over_sound = self._combine_sounds(
                    tone1,
                    tone2
                )

        except Exception:
            # If audio fails, the game still works normally.
            self.fruit_sound = None
            self.bomb_sound = None
            self.game_over_sound = None

    def _create_tone(self, frequency, duration, volume):
        """Generate a simple sine-wave sound."""
        try:
            sample_rate = 44100
            sample_count = int(sample_rate * duration)

            samples = array("h")

            for i in range(sample_count):
                value = int(
                    32767
                    * volume
                    * math.sin(
                        2 * math.pi * frequency * i / sample_rate
                    )
                )
                samples.append(value)

            return pygame.mixer.Sound(buffer=samples.tobytes())

        except Exception:
            return None

    def _combine_sounds(self, sound1, sound2):
        """
        Create a simple game-over sound by playing two tones
        one after another.
        """
        try:
            # Pygame Sound objects cannot be directly concatenated,
            # so return the first tone. The second tone is played
            # separately by _play_game_over_sound().
            return sound1
        except Exception:
            return None

    def _play_sound(self, sound):
        """Safely play a sound if audio is available."""
        try:
            if sound is not None:
                sound.play()
        except Exception:
            pass

    def _play_game_over_sound(self):
        """Play the game-over sound only once."""
        if self.game_over_sound_played:
            return

        self.game_over_sound_played = True

        try:
            if self.game_over_sound is not None:
                self.game_over_sound.play()

            # Play a second lower tone after the first one.
            # This is intentionally simple and non-blocking.
            if self.bomb_sound is not None:
                pygame.time.set_timer(
                    pygame.USEREVENT + 1,
                    180,
                    loops=1
                )

        except Exception:
            pass

    # =========================================================
    # TASK 3: DIFFICULTY
    # =========================================================

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

        if difficulty == "Easy":
            self.spawn_interval = 65
            self.speed_scale = 0.8
            self.bomb_chance = 0.10

        elif difficulty == "Medium":
            self.spawn_interval = 55
            self.speed_scale = 1.0
            self.bomb_chance = 0.15

        elif difficulty == "Hard":
            self.spawn_interval = 45
            self.speed_scale = 1.25
            self.bomb_chance = 0.20

    def restart(self, difficulty):
        self.set_difficulty(difficulty)

        self.fruits = []
        self.trail = []
        self.previous_mouse_pos = None

        self._spawn_timer = 0
        self.lives = 3
        self.score = 0
        self.game_over = False
        self.game_over_sound_played = False

    # =========================================================
    # GAME LOGIC
    # =========================================================

    def spawn_fruit(self):
        x = random.randint(60, self.width - 60)
        vy = -random.uniform(13, 16) * self.speed_scale
        vx = random.uniform(-2, 2)
        gravity = 0.35
        kind = "bomb" if random.random() < self.bomb_chance else "fruit"

        fruit = Fruit(
            x,
            self.height + 30,
            vx,
            vy,
            gravity,
            kind=kind
        )

        fruit.color = (
            BOMB_BLACK
            if kind == "bomb"
            else random.choice(FRUIT_COLORS)
        )

        self.fruits.append(fruit)

    def handle_event(self, event):

        # -----------------------------------------------------
        # TASK 1: EXISTING FAST SWIPE COLLISION
        # -----------------------------------------------------
        if event.type == pygame.MOUSEMOTION and not self.game_over:
            self._handle_motion(event.pos)

        # -----------------------------------------------------
        # TASK 3: GAME OVER KEYBOARD OPTIONS
        # -----------------------------------------------------
        if event.type == pygame.KEYDOWN and self.game_over:

            if event.key == pygame.K_e:
                self.restart("Easy")

            elif event.key == pygame.K_m:
                self.restart("Medium")

            elif event.key == pygame.K_h:
                self.restart("Hard")

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

        # -----------------------------------------------------
        # TASK 4: SECOND PART OF GAME-OVER SOUND
        # -----------------------------------------------------
        if event.type == pygame.USEREVENT + 1:
            try:
                if self.bomb_sound is not None:
                    self.bomb_sound.play()
            except Exception:
                pass

    # =========================================================
    # TASK 1: EXISTING COLLISION DETECTION
    # =========================================================

    def _handle_motion(self, pos):
        previous_pos = self.previous_mouse_pos

        # Safely handle the first mouse position.
        if previous_pos is None:
            previous_pos = pos

        for fruit in self.fruits:
            if (
                not fruit.sliced
                and fruit.intersects_segment(previous_pos, pos)
            ):
                self._slice(fruit)

        self.trail.append(pos)

        if len(self.trail) > 15:
            self.trail.pop(0)

        self.previous_mouse_pos = pos

    # =========================================================
    # TASK 4: SLICE SOUND
    # =========================================================

    def _slice(self, fruit):
        fruit.sliced = True

        if fruit.kind == "bomb":

            # Bomb sound
            self._play_sound(self.bomb_sound)

            # Game over
            self.game_over = True

            # Game-over sound
            self._play_game_over_sound()

        else:
            self.score += 1

            # Fruit sliced sound
            self._play_sound(self.fruit_sound)

    # =========================================================
    # INPUT
    # =========================================================

    def handle_input(self):
        # Reserved for continuously-held-key input.
        # This game is entirely mouse-driven.
        pass

    # =========================================================
    # UPDATE
    # =========================================================

    def update(self):
        if self.game_over:
            return

        self._spawn_timer += 1

        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.spawn_fruit()

        still_alive = []

        for fruit in self.fruits:
            fruit.update()

            if fruit.sliced:
                continue

            if fruit.off_screen(self.height):
                if fruit.kind == "fruit":
                    self.lives -= 1

                continue

            still_alive.append(fruit)

        self.fruits = still_alive

        # Player loses when all lives are gone.
        if self.lives <= 0:
            self.game_over = True

            # Task 4: game-over sound
            self._play_game_over_sound()

    # =========================================================
    # RENDER
    # =========================================================

    def render(self, screen):

        # -----------------------------------------------------
        # TASK 2 + TASK 3: GAME OVER SCREEN
        # -----------------------------------------------------
        if self.game_over:
            screen.fill((0, 0, 0))

            game_over_font = pygame.font.SysFont(
                "Arial",
                56,
                bold=True
            )

            score_font = pygame.font.SysFont(
                "Arial",
                32
            )

            option_font = pygame.font.SysFont(
                "Arial",
                30,
                bold=True
            )

            game_over_text = game_over_font.render(
                "GAME OVER",
                True,
                WHITE
            )

            score_text = score_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            choose_text = score_font.render(
                "Choose Difficulty",
                True,
                WHITE
            )

            easy_text = option_font.render(
                "E - Easy",
                True,
                WHITE
            )

            medium_text = option_font.render(
                "M - Medium",
                True,
                WHITE
            )

            hard_text = option_font.render(
                "H - Hard",
                True,
                WHITE
            )

            exit_text = option_font.render(
                "ESC - Exit",
                True,
                WHITE
            )

            screen.blit(
                game_over_text,
                game_over_text.get_rect(
                    center=(
                        self.width // 2,
                        90
                    )
                )
            )

            screen.blit(
                score_text,
                score_text.get_rect(
                    center=(
                        self.width // 2,
                        160
                    )
                )
            )

            screen.blit(
                choose_text,
                choose_text.get_rect(
                    center=(
                        self.width // 2,
                        220
                    )
                )
            )

            screen.blit(
                easy_text,
                easy_text.get_rect(
                    center=(
                        self.width // 2,
                        290
                    )
                )
            )

            screen.blit(
                medium_text,
                medium_text.get_rect(
                    center=(
                        self.width // 2,
                        340
                    )
                )
            )

            screen.blit(
                hard_text,
                hard_text.get_rect(
                    center=(
                        self.width // 2,
                        390
                    )
                )
            )

            screen.blit(
                exit_text,
                exit_text.get_rect(
                    center=(
                        self.width // 2,
                        440
                    )
                )
            )

            return

        # -----------------------------------------------------
        # NORMAL GAME SCREEN
        # -----------------------------------------------------

        for fruit in self.fruits:
            color = getattr(fruit, "color", WHITE)

            pygame.draw.circle(
                screen,
                color,
                (int(fruit.x), int(fruit.y)),
                fruit.radius
            )

        if len(self.trail) >= 2:
            pygame.draw.lines(
                screen,
                WHITE,
                False,
                self.trail,
                3
            )

        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        screen.blit(
            score_text,
            (10, 10)
        )

        lives_text = self.font.render(
            f"Lives: {self.lives}",
            True,
            WHITE
        )

        screen.blit(
            lives_text,
            (self.width - 130, 10)
        )

