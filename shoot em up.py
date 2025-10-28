import pygame
import random
from os import path

WIDTH = 480
HEIGHT = 600
FPS = 60

# pygame init og opprettelse av game-window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shmup!")
clock = pygame.time.Clock()

# set up assets folders
img_dir = path.join(path.dirname(__file__), "img")
print(img_dir)

# load game graphics
background_img = pygame.image.load(path.join(img_dir, "space_bg.png")).convert()
background_img_rect = background_img.get_rect()
player_img = pygame.image.load(path.join(img_dir,  "enemyRed3.png"))
laser_img = pygame.image.load(path.join(img_dir, "laserRed07.png"))
mob_img = pygame.image.load(path.join(img_dir, "meteorBrown_med1.png"))


# farger
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

font_name = pygame.font.match_font("arial")
# funksjon der du kan legge inn paramtere og den skriver ut sentrert tekst
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)                       # TRUE = antia-aliast som gjør pikslene mykere og lettere å lese
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)                                           # gjør at teksten blir sentrert
    surf.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))       # skalerer bildet mindre
        self.rect = self.image.get_rect()                               # lager en firkant rundt bildet som brukes i collision-detection
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)        # tegner opp en sirkel for å sjekke hitboxen
        self.rect.centerx = WIDTH / 2               # plasserer figuren i midten
        self.rect.bottom = HEIGHT - 10              # plasseres 10 px fra bunn
        self.speedx = 0
        self.i = 0

    def update(self):
        self.speedx = 0                             # gjør at når du slipper tasten, stopper sprite å bevege seg
        keystate = pygame.key.get_pressed()         # returnerer en liste med tastene du trykker
        if keystate[pygame.K_LEFT]:
            self.speedx = - 5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx                  # endrer x-verdien til figuren

        # gjør at skuddene kommer med mellomrom når man holder inne
        self.i += 1
        if keystate[pygame.K_SPACE]:
            if self.i < 2:
                player.shoot()
        if self.i >= 7:
            self.i = 0


        # stopper fra å gå for langt tils idene
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)       # sender med x og y verdiene til class Bullet
        all_sprites.add(bullet)
        bullets.add(bullet)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = mob_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)     # tilfeldig mellom 0 og bredden av skjermen - bredden av mob
        self.rect.y = random.randrange(- 100, - 40)                 # spawner over skjermen
        self.speedy = random.randrange(2, 8)
        self.speedx = random.randrange(-2, 2)
        self.rot = 0                                                # rotasjon i grader
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()                  # hvor mange "ticks" siden forrige gang vi oppdaterte/roterte bildet

    def rotate(self):
        now = pygame.time.get_ticks()                               # finner tiden nå
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360            # hindrer verdien fra å komme over 360 grader
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            # koden under gjør at den roterer i tyngdepunktet, og ikke roterer skjevt
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()                       # finner et nytt rektangel rundt meteoren
            self.rect.center = old_center                           # setter det nye sentrum der det gamle var

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # går mob over bunnen eller ut på sidene spawner de med nye tilfeldige verdier
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)  # tilfeldig mellom 0 og bredden av skjermen - bredden av mob
            self.rect.y = random.randrange(- 100, - 40)     # spawner over skjermen
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-2, 2)

        if self.rect.left < 0 or self.rect.right > WIDTH:           # treffer mob veggen, snur x-retningen. de spretter tilbake
            self.speedx = -1 * self.speedx


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(laser_img, (15, 40))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # fjerne den hvis kula går utenfor skjermen
        if self.rect.bottom < 0:
            self.kill()                             # fjerner sprite fra alle grupper


def show_go_screen():
    screen.blit(background_img, background_img_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Aroow keys move, space to fire", 30, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 30, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


all_sprites = pygame.sprite.Group()                 # sprite er et 2D objekt i et spill
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)                             # legger til spilleren i sprite gruppen
for i in range(8):                                  # 8 mobs
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

score = 0
# game loop
running = True
game_over = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()  # sprite er et 2D objekt i et spill
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)  # legger til spilleren i sprite gruppen
        for i in range(8):  # 8 mobs
            m = Mob()
            all_sprites.add(m)
            mobs.add(m)
        score = 0

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()                                    # denne aktiverer def update()
    # sjekker om bullet treffer mob. "True, True" gjør at både mobs og bullets blir slettet
    mob_hits = pygame.sprite.groupcollide(mobs, bullets, True, True)

    for hit in mob_hits:                                    # gjør at det spawner nye mobs når noen dør
        score += 50
        m = Mob()
        all_sprites.add(m)
        mobs.add(m)

    # sjekker om mob treffer player
        # returnerer en lise med alle treffene mellom player og mobs,
        # False = sletter ikke player, circle gjør hitboxen til en sirkel
        # pygame.sprite.collide_circle finner radius variablen av seg selv
    player_hits = pygame.sprite.spritecollide(player, mobs, False, pygame.sprite.collide_circle)
    if player_hits:                                        # hvis hits inneholder noe
        game_over = True

    # oppdatering og tegning av sprite
    screen.fill(BLACK)                                  # bakgrunnsfarge
    screen.blit(background_img, background_img_rect)    # tegner bakgrunnen, starter øverst i venstre hjørne
    all_sprites.draw(screen)                            # tegner alle sprites på skjermen
    draw_text(screen, str(score), 30, WIDTH/2, 10)
    pygame.display.flip()                               # oppdaterer bildet

pygame.quit()
