import pygame as pg
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'img')

WIDTH = 720
HEIGHT = 900
FPS = 60

# COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BACKGROUND = (72, 172, 183)

# INIT
pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("___Shmup___")
clock = pg.time.Clock()


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(player_img, (75, 58))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 30
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0

    def update(self):
        self.speedx = 0

        key_states = pg.key.get_pressed()
        if key_states[pg.K_LEFT]:
            self.speedx = -6
        if key_states[pg.K_RIGHT]:
            self.speedx = 6

        self.rect.x += self.speedx

        # Constrain into walls
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mob(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image_orig = pg.transform.scale(random.choice(meteors), (50, 48))
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.bottom = random.randint(-100, -40)
        self.speedy = random.randint(2, 5)
        self.speedx = random.randint(4, 5)
        self.rot = 0
        self.rot_speed = random.randint(-8, 8)
        self.last_update = pg.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.rotate()

        # Going to bottom spawns upside
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.bottom = random.randint(-100, -40)
            self.speedy = random.randint(3, 8)

        # Make the mobs jump back from sides
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speedx = -1 * self.speedx

    def rotate(self):
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = laser_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

        # Destruct if moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


# LOAD GAME GRAPHICS
background = pg.image.load(path.join(img_dir, "background.png")).convert()
background = pg.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect()
player_img = pg.image.load(path.join(img_dir, "player.png")).convert()
meteor_img_1 = pg.image.load(path.join(img_dir, "meteor_1.png")).convert()
meteor_img_2 = pg.image.load(path.join(img_dir, "meteor_2.png")).convert()
meteors = [meteor_img_1, meteor_img_2]
laser_img = pg.image.load(path.join(img_dir, "laser.png")).convert()


all_sprites = pg.sprite.Group()
mobs = pg.sprite.Group()
bullets = pg.sprite.Group()

player = Player()
all_sprites.add(player)

for i in range(5):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# GAME LOOP
running = True
while running:
    clock.tick(FPS)

    # Process input events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                player.shoot()

    # Update
    all_sprites.update()

    # Check to see if a bullet hits a mob / True True if hits both sprites deleted
    hits = pg.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # Check for player collisions with mob
    hits = pg.sprite.spritecollide(
        player, mobs, False, pg.sprite.collide_circle)
    if hits:
        running = False

    # Draw/Render
    screen.fill(BACKGROUND)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)

    # After drawing everything, flip the display
    pg.display.flip()

pg.quit()
