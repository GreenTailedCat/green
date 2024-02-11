import pygame
import random
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Game variables
score = 0
raindrop_speed = 2
raindrop_speed_increment = 0.01
lightning_speed = 10
lightning_counter = 0
raindrop_streak = 0  # New variable for raindrop streak
game_active = False
pause = False

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("Raindrop Catcher")

# Load images
bucket_img = pygame.image.load("bucket.png")
lightning_img = pygame.image.load("lightning.png")
raindrop_img = pygame.image.load("raindrop.png")
start_button_img = pygame.image.load("start.png")
pause_button_img = pygame.image.load("pause.png")
quit_button_img = pygame.image.load("quit.png")

# Resize images
bucket_img = pygame.transform.scale(bucket_img, (50, 50))
lightning_img = pygame.transform.scale(lightning_img, (50, 50))
raindrop_img = pygame.transform.scale(raindrop_img, (50, 50))
start_button_img = pygame.transform.scale(start_button_img, (100, 50))
pause_button_img = pygame.transform.scale(pause_button_img, (50, 50))
quit_button_img = pygame.transform.scale(quit_button_img, (50, 50))

# Create the pause button rectangle
pause_button_rect = pause_button_img.get_rect(topleft=(10, 10))
# Create the quit button rectangle
quit_button_rect = quit_button_img.get_rect(topleft=(70, 10))

# Create the barrier rectangle behind the pause button
barrier_rect = pygame.Rect(0, 0, pause_button_rect.width + 10, HEIGHT)

# Create the start button rectangle
start_button_rect = start_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Create clock object to control the frame rate
clock = pygame.time.Clock()

# Create fonts
font = pygame.font.Font(None, 36)

# Create bucket object
bucket_rect = bucket_img.get_rect(midbottom=(WIDTH // 2, HEIGHT))
bucket_speed = 5

# Create lists for raindrops and lightning
raindrops = []
lightnings = []

# Initialize sound effects
water_sound = pygame.mixer.Sound("water_in_bucket.mp3")
game_over_sound = pygame.mixer.Sound("game_over.mp3")

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION and game_active and not pause:
            if not pause and not barrier_rect.collidepoint(event.pos):
                bucket_rect.x = event.pos[0] - bucket_rect.width // 2
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_active and not pause:
            if start_button_rect.collidepoint(event.pos):
                pygame.mixer.stop()  # Stop any lingering game over sound
                game_active = True
                score = 0
                raindrop_streak = 0
                raindrops = []
                lightnings = []
        elif event.type == pygame.MOUSEBUTTONDOWN and game_active:
            if pause_button_rect.collidepoint(event.pos):
                pause = not pause
            elif quit_button_rect.collidepoint(event.pos):
                game_active = False
                score = 0
                raindrop_streak = 0  # Reset the raindrop streak when quitting
                raindrops = []
                lightnings = []
                pause = False  # Reset the pause when quitting

    # Draw background
    screen.fill(WHITE)

    if not game_active:
        screen.blit(start_button_img, start_button_rect)

    if game_active:
        if not pause:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and bucket_rect.left > 0 and not barrier_rect.collidepoint(
                (bucket_rect.left - bucket_speed, bucket_rect.centery)
            ):
                bucket_rect.x -= min(bucket_speed, bucket_rect.left)
            if keys[pygame.K_RIGHT] and bucket_rect.right < WIDTH and not barrier_rect.collidepoint(
                (bucket_rect.right + bucket_speed, bucket_rect.centery)
            ):
                bucket_rect.x += min(bucket_speed, WIDTH - bucket_rect.right)

            if random.randint(0, 100) < 3:
                margin = 50  # Adjust the margin as needed
                raindrop_rect = raindrop_img.get_rect(center=(random.randint(margin, WIDTH - margin), 0))
                raindrops.append(raindrop_rect)

            raindrops_to_remove = []
            for raindrop_rect in raindrops:
                raindrop_rect.y += raindrop_speed

                if raindrop_rect.y > HEIGHT:
                    # Reset the streak count when a raindrop goes out of the scenario
                    raindrop_streak = 0
                elif raindrop_rect.colliderect(bucket_rect):
                    raindrops_to_remove.append(raindrop_rect)
                    score += 1
                    raindrop_streak += 1

                    # Reset the streak count when a raindrop is caught
                    water_sound.set_volume(0.25)
                    water_sound.play()

            # Remove raindrops after the iteration
            for raindrop_rect in raindrops_to_remove:
                raindrops.remove(raindrop_rect)

            if score >= 60 and random.randint(0, 100) < 3:
                lightning_rect = lightning_img.get_rect(center=(random.randint(0, WIDTH), 0))
                lightnings.append(lightning_rect)

            lightnings_to_remove = []
            for lightning_rect in lightnings:
                lightning_rect.y += lightning_speed

                if lightning_rect.colliderect(bucket_rect):
                    game_active = False
                    pygame.mixer.stop()  # Stop any lingering game over sound
                    game_over_sound.play()  # Play game over sound
                    pygame.time.delay(2000)  # Delay for 2 seconds before restarting
                    score = 0
                    raindrop_streak = 0  # Reset the raindrop streak
                elif lightning_rect.y > HEIGHT:
                    lightnings_to_remove.append(lightning_rect)

            # Remove lightnings after the iteration
            for lightning_rect in lightnings_to_remove:
                lightnings.remove(lightning_rect)

        screen.blit(pause_button_img, (10, 10))
        screen.blit(quit_button_img, (70, 10))

        for raindrop_rect in raindrops:
            screen.blit(raindrop_img, raindrop_rect)

        for lightning_rect in lightnings:
            screen.blit(lightning_img, lightning_rect)

        screen.blit(bucket_img, bucket_rect)

        score_text = font.render(f"Score: {score}", True, BLUE)
        streak_text = font.render(f"Streak: {raindrop_streak}", True, BLUE)
        screen.blit(score_text, (10, 60))
        screen.blit(streak_text, (10, 100))

    pygame.display.flip()

    if raindrop_speed < 5:
        raindrop_speed += raindrop_speed_increment

    if not pause:
        for raindrop_rect in raindrops:
            if raindrop_rect.y > HEIGHT:
                raindrops.remove(raindrop_rect)

        for lightning_rect in lightnings:
            if lightning_rect.y > HEIGHT:
                lightnings.remove(lightning_rect)

    clock.tick(FPS)

pygame.quit()
sys.exit()