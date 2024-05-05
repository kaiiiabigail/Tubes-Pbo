import sys
import random
import pygame
from pygame.locals import *
from abc import ABC, abstractmethod
 
pygame.init()
 
laser = pygame.mixer.Sound('laser.wav')
ledakan = pygame.mixer.Sound('ledakan.wav')
mulai = pygame.mixer.Sound('mulai.wav')
gameover = pygame.mixer.Sound('game_over.mp3')
screenmusic = pygame.mixer.Sound('menu.mp3')
background_music = pygame.mixer.music.load('latar.mp3')
 
pygame.mixer.init()
 
screen = pygame.display.set_mode((0,0), FULLSCREEN)
s_width, s_height = screen.get_size()
 
clock = pygame.time.Clock()
FPS = 60
 
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
pbullet_group = pygame.sprite.Group()
ebullet_group = pygame.sprite.Group()
ubullet_group = pygame.sprite.Group()
ledakan_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
 
pygame.mouse.set_visible(False)

class Pesawat(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        self.alive = True
        self.count_to_live = 0 
        self.activate_bullet = True
        self.alpha_duration = 0

    def update(self):
        pass

    def shoot(self):
        pass

    def dead(self):
        pygame.mixer.Sound.play(ledakan)
        self.alive = False
        self.activate_bullet = False

class Player(Pesawat):
    def __init__(self, img):
        super().__init__(img)
 
    def update(self):
        if self.alive:
            self.image.set_alpha(80)
            self.alpha_duration += 1
            if self.alpha_duration > 170:
                self.image.set_alpha(255)
        else:
            self.alpha_duration = 0
            expl_x = self.rect.x + 20
            expl_y = self.rect.y + 40
            explosion = Explosion(expl_x, expl_y)
            ledakan_group.add(explosion)
            sprite_group.add(explosion)
            pygame.time.delay(22)
            self.rect.y = s_height + 200
            self.count_to_live += 1
            if self.count_to_live > 100:
                self.alive = True
                self.count_to_live = 0
                self.activate_bullet = True
    
    def move(self, direction):
        if direction == 'LEFT':
            self.rect.x -= 20
        elif direction == 'RIGHT':
            self.rect.x += 20
        elif direction == 'UP':
            self.rect.y -= 20
        elif direction == 'DOWN':
            self.rect.y += 20
    
    def shoot(self):
        if self.activate_bullet:
            bullet = PlayerBullet('pbullet.png')
            bullet.rect.x = self.rect.x + 30
            bullet.rect.y = self.rect.y
            pbullet_group.add(bullet)
            sprite_group.add(bullet)
 
class Enemy(Pesawat):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = random.randrange(80, s_width-80)
        self.rect.y = random.randrange(-500, 0)
        screen.blit(self.image, (self.rect.x, self.rect.y))
 
    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(80, s_width-50)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()
 
    def shoot(self):
        if self.rect.y in (100, 300, 600):
            enemybullet = EnemyBullet('ebullet.png')
            enemybullet.rect.x = self.rect.x + 40
            enemybullet.rect.y = self.rect.y + 50
            ebullet_group.add(enemybullet)
            sprite_group.add(enemybullet)
 
class UFO(Enemy):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = -200 
        self.rect.y = 150 
        self.move = 1
 
    def update(self):
        self.rect.x += self.move 
        if self.rect.x > s_width + 200:
            self.move *= -1 
        elif self.rect.x < -200:
            self.move *= -1
        self.shoot()
 
    def shoot(self):
        if self.rect.x % 50 == 0:
            ufobullet = EnemyBullet('ubullet.png')
            ufobullet.rect.x = self.rect.x + 50
            ufobullet.rect.y = self.rect.y + 80
            ubullet_group.add(ufobullet)
            sprite_group.add(ufobullet)
 
class bullet(pygame.sprite.Sprite, ABC):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()

    @abstractmethod
    def update(self):
        pass

class PlayerBullet(bullet):
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey('black')
 
    def update(self):
        self.rect.y -= 15
        if self.rect.y < 0:
            self.kill()
 
class EnemyBullet(bullet):
    def __init__(self, img):
        super().__init__(img)
        self.image.set_colorkey('white')
 
    def update(self):
        self.rect.y += 5
        if self.rect.y > s_height:
            self.kill()
 
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = []
        for i in range(1, 6):
            img = pygame.image.load(f'exp{i}.png').convert()
            img.set_colorkey('black')
            img = pygame.transform.scale(img, (120, 120))
            self.img_list.append(img)
        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.count_delay = 0 
 
    def update(self):
        self.count_delay += 1
        if self.count_delay >= 12:
            if self.index < len(self.img_list) - 1:
                self.count_delay = 0
                self.index += 1
                self.image = self.img_list[self.index]
        if self.index >= len(self.img_list) - 1:
            if self.count_delay >= 12:
                self.kill()
 
class Game:
    def __init__(self):
        self._count_hit_enemy = 0
        self._count_hit_ufo = 0 
        self._nyawa = 5
        self._count_score = 0
        self.__init_create = True
 
        self.layar_start()
 
    def start_text(self):
        font = pygame.font.Font('ModernWarfare-OV7KP.ttf', 100)
        text = font.render('Classic War Plane', True, 'orange')
        text_rect = text.get_rect(center=(s_width/2, s_height/2-80))
        screen.blit(text, text_rect)
        font1 = pygame.font.Font('ModernWarfare-OV7KP.ttf', 50)
        font2 = pygame.font.SysFont('Calibri', 20)
        text1 = font1.render('Click ENTER', True, 'grey')
        text2 = font2.render('Rizqullah Bimo, Ihya Razky, Boy Sandro, Imad Aqil, Zedi Mumtaz', True, 'white')
        text1_rect = text1.get_rect(center=(s_width/2, s_height/2+75))
        text2_rect = text2.get_rect(center=(s_width/2, s_height/2+350))
        screen.blit(text1, text1_rect)
        screen.blit(text2, text2_rect)

    def layar_start(self):
        pygame.mixer.Sound.stop(screenmusic)
        pygame.mixer.Sound.play(screenmusic) 
        sprite_group.empty()
        while True: 
            screen.fill('black')
            self.start_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
 
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_RETURN:
                        self.run_game()
 
            pygame.display.update()
    def pause_text(self):
        font = pygame.font.Font('OriginTech personal use.ttf', 100)
        text = font.render('PAUSE GAME', True, 'orange')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)
 
    def layar_pause(self):
        self.__init_create = False
        while True: 
            self.pause_text()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
 
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_SPACE:
                        self.run_game()
 
            pygame.display.update()
 
    def gameover_text(self):
        font = pygame.font.Font('ModernWarfare-OV7KP.ttf', 150)
        text = font.render('GAME OVER', True, 'orange')
        text_rect = text.get_rect(center=(s_width/2, s_height/2))
        screen.blit(text, text_rect)
 
    def layar_gameover(self):
        pygame.mixer.music.stop()
        pygame.mixer.Sound.play(gameover)
        while True: 
            screen.fill('black')
            self.gameover_text()
 
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
 
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.layar_start()
 
            pygame.display.update()
 
    def pemain(self):
        self.player = Player('spaceship.png')
        player_group.add(self.player)
        sprite_group.add(self.player)
 
    def musuh(self):
        for i in range(10):
            self.enemy = Enemy('enemy.png')
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)
 
    def ufo(self):
        for i in range(1):
            self.ufo = UFO('ufo.png')
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)
 
    def hit_enemy(self):
        hits = pygame.sprite.groupcollide(enemy_group, pbullet_group, False, True)
        for i in hits:
            self._count_hit_enemy += 1
            if self._count_hit_enemy == 3:
                self._count_score += 10
                expl_x = i.rect.x + 20
                expl_y = i.rect.y + 40
                explosion = Explosion(expl_x, expl_y)
                ledakan_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = random.randrange(0, s_width)
                i.rect.y = random.randrange(-3000, -100)
                self._count_hit_enemy = 0
                pygame.mixer.Sound.play(ledakan)
 
    def hit_ufo(self):
        hits = pygame.sprite.groupcollide(ufo_group, pbullet_group, False, True)
        for i in hits:
            self._count_hit_ufo += 1
            if self._count_hit_ufo == 50:
                self._count_score += 30
                expl_x = i.rect.x + 50
                expl_y = i.rect.y + 60
                explosion = Explosion(expl_x, expl_y)
                ledakan_group.add(explosion)
                sprite_group.add(explosion)
                i.rect.x = -199
                self._count_hit_ufo = 0
                pygame.mixer.Sound.play(ledakan)
 
    def enemy_hit(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ebullet_group, True)
            if hits:
                self._nyawa -= 1
                self.player.dead()
                if self._nyawa < 0:
                    self.layar_gameover()
 
 
    def ufo_hit(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ubullet_group, True)
            if hits:
                self._nyawa -= 2
                self.player.dead()
                if self._nyawa < 0:
                    self.layar_gameover()
 
    def enemy_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, enemy_group, False)
            if hits:
                for i in hits:
                    i.rect.x = random.randrange(0, s_width)
                    i.rect.y = random.randrange(-3000, -100)
                    self._nyawa -= 2
                    self.player.dead()
                    if self._nyawa < 0:
                        self.layar_gameover()
 
    def ufo_crash(self):
        if self.player.image.get_alpha() == 255:
            hits = pygame.sprite.spritecollide(self.player, ufo_group, False)
            if hits:
                for i in hits:
                    i.rect.x = -199
                    self._nyawa -= 3
                    self.player.dead()
                    if self._nyawa < 0:
                        self.layar_gameover()
 
    def hp(self):
        self.live_img = pygame.image.load('hp.png')
        n = 0
        for i in range(self._nyawa):
            screen.blit(self.live_img, (s_width - n - 50, s_height - 50))
            n += 20
 
    def score(self):
        score = self._count_score 
        font = pygame.font.Font('OriginTech personal use.otf', 30)
        text = font.render("Score: "+str(score), True, 'green')
        text_rect = text.get_rect(center=(s_width -110, 50))
        screen.blit(text, text_rect)
 
    def run_update(self):
        image_bg = pygame.image.load('space_bg.jpg') 
        screen.blit(image_bg, (0,0))
        sprite_group.draw(screen)
        sprite_group.update()
 
    def run_game(self):
        pygame.mixer.Sound.stop(screenmusic)
        pygame.mixer.Sound.play(mulai)
        pygame.mixer.music.play(-1)
        if self.__init_create:
            self.pemain()
            self.musuh()
            self.ufo()
        while True:
            screen.fill('black')
            self.hit_enemy()
            self.hit_ufo()
            self.enemy_hit()
            self.ufo_hit()
            self.enemy_crash()
            self.ufo_crash()
            self.run_update()
            pygame.draw.rect(screen, 'black', (0,0,s_width,30))
            self.hp()
            self.score()
 
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
 
                    if event.key == K_SPACE:
                        pygame.mixer.Sound.play(laser)
                        self.player.shoot()
                        
                    if event.key == K_LEFT:
                        self.player.move('LEFT')
                        
                    if event.key == K_RIGHT:
                        self.player.move('RIGHT')
                        
                    if event.key == K_UP:
                        self.player.move('UP')
                        
                    if event.key == K_DOWN:
                        self.player.move('DOWN')
                    
                        
 
            pygame.display.update()
            clock.tick(FPS)
 
def main():
    game = Game()
 
if __name__ == '__main__':
    main()