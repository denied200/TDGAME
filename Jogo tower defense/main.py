import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c


#inicia o jogo
pg.init()

#inicia o relogio/fps
clock = pg.time.Clock()

#cria a janela
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Tower Defense")

#variaveis
game_over = False   
game_outcome = 0 #-1 perde 1 ganha
level_started = False
last_enemy_spawn = pg.time.get_ticks()
placing_turrets = False
selected_turret = None

#################IMAGENS#############
#mapa
map_image = pg.image.load('Jogo tower defense/levels/level.png').convert_alpha()
#"weak" == pg.transform.scale("enemy_1.png",[100,100])

#Sprites
turret_sheet = pg.image.load('Jogo tower defense/assets/images/turrets/turret_1.png').convert_alpha()
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'Jogo tower defense/assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)

#Torre
cursor_turret = pg.image.load('Jogo tower defense/assets/images/turrets/cursor_turret.png').convert_alpha()
cursor_turret = pg.transform.scale(cursor_turret,[100,100])


#inimigos
enemy_images = {
  "weak": pg.image.load('Jogo tower defense/assets/images/enemies/enemy_1.png').convert_alpha(),
  "medium": pg.image.load('Jogo tower defense/assets/images/enemies/enemy_2.png').convert_alpha(),
  "strong": pg.image.load('Jogo tower defense/assets/images/enemies/enemy_3.png').convert_alpha(),
  "elite": pg.image.load('Jogo tower defense/assets/images/enemies/enemy_4.png').convert_alpha()
}

#imagens de botao
buy_turret_image = pg.image.load('Jogo tower defense/assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('Jogo tower defense/assets/images/buttons/cancel.png').convert_alpha()
begin_image = pg.image.load('Jogo tower defense/assets/images/buttons/begin.png').convert_alpha()
fast_forward_image = pg.image.load('Jogo tower defense/assets/images/buttons/fast_forward.png').convert_alpha()
restart_image = pg.image.load('Jogo tower defense/assets/images/buttons/restart.png').convert_alpha()
upgrade_turret_image = pg.image.load('Jogo tower defense/assets/images/buttons/upgrade_turret.png').convert_alpha()
#close_image = pg.image.load('Jogo tower defense/assets/images/buttons/close_game.png').convert_alpha()

#gui
heart_image = pg.image.load("Jogo tower defense/assets/images/gui/heart.png").convert_alpha()
coin_image = pg.image.load("Jogo tower defense/assets/images/gui/coin.png").convert_alpha()
logo_image = pg.image.load("Jogo tower defense/assets/images/gui/logo.jpg").convert_alpha()
logo_image = pg.transform.scale(logo_image,[300,200])

#carregar sons
shot_fx = pg.mixer.Sound('Jogo tower defense/assets/audio/shot.wav')
shot_fx.set_volume(1)

#################IMAGENS#############


# Music initialization
pg.mixer.init()

# Musica antes do loop
def play_game_music():
    pg.mixer.music.load('Jogo tower defense/assets/audio/musica1.mp3')
    pg.mixer.music.play(-1)  # -1 means loop indefinitely
    pg.mixer.music.set_volume(0.3)

def play_game_over_music():
    pg.mixer.music.load('Jogo tower defense/assets/audio/musica2.ogg')
    pg.mixer.music.play(-1)  # -1 means loop indefinitely
    pg.mixer.music.set_volume(0.2)

# comecar musica inicial
play_game_music()
    
#json para nivel
with open('Jogo tower defense/levels/level.tmj') as file:
    world_data = json.load(file)

#carregar fontes para aparecer na tela
text_font = pg.font.SysFont("Consolas", 24, bold = True)
large_font = pg.font.SysFont("Consolas", 36)

#funcao texto na tela
def draw_text(text, font, text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

def display_data():
  #painel
  pg.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
  pg.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
  screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
  #display data
  draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
  screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
  draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
  screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
  draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)


def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    #QUal o numero do tile?
    mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
    # O tile tem grama?
    if world.tile_map[mouse_tile_num] == 7:
        # nao botar uma torre dentro da outra
        space_is_free = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_free = False
        #Se tiver espaco bota uma torre
        if space_is_free == True:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
            turret_group.add(new_turret)
            #custo da torre
            world.money -= c.BUY_COST

def select_turret (mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
            return turret 
        
def clear_selection():
    for turret in turret_group:
        turret.selected = False

#criar mundo
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create groups
enemy_group = pg.sprite.Group()
turret_group = pg.sprite.Group()

#Criar botao
#close_button = Button(c.SCREEN_WIDTH + 60,80,close_image, True)
turret_button = Button(c.SCREEN_WIDTH + 30,100,buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50,180,cancel_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60,300,begin_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5,180,upgrade_turret_image, True)
restart_button = Button(310,300,restart_image, True)
fast_forward_button = Button(770,300,fast_forward_image, False)





#loop
run = True
while run:

    clock.tick(c.FPS)

    ############UPDATE#############

    if game_over == False:
        #Checar se o jogador perdeu vida
        if world.health <= 0:
            game_over = True
            game_outcome = -1 #perdeu
            pg.mixer.music.stop()  # parar musica do jogo
            play_game_over_music()  # comecar musica de game over
        if world.level > c.TOTAL_LEVELS:
            game_over = True
            game_outcome = 1  #ganha


        #atualiza grupo
        enemy_group.update(world)
        turret_group.update(enemy_group)

        #torre selecionada 
        if selected_turret:
            selected_turret.selected = True

    world.draw(screen)

    #desenhar grupos
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    display_data()

    if game_over == False:
        #checkar se comecou ou nao
        if level_started == False:
            if begin_button.draw(screen):
                level_started = True
        else: 
            #acelerar o jogo
            world.game_speed = 1
            if fast_forward_button.draw(screen):
                world.game_speed = 2
            #spawnar inimigos
            if pg.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
                if world.spawned_enemies < len(world.enemy_list):
                    enemy_type = world.enemy_list[world.spawned_enemies]
                    enemy = Enemy(enemy_type,world.waypoints, enemy_images)
                    enemy_group.add(enemy)
                    world.spawned_enemies += 1
                    last_enemy_spawn = pg.time.get_ticks()

        #checkar se a wave acabou
        if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pg.time.get_ticks()
            world.reset_level()
            world.process_enemies()


        #desenhar botoes
        #botao para colocar torre
        draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
        screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
        if turret_button.draw(screen):
            placing_turrets = True
        # se colocar torre ent aparece o botao de cancelar
        if placing_turrets == True:
            #torre cursor
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pg.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= c.SCREEN_WIDTH:
                screen.blit(cursor_turret, cursor_rect)
            if cancel_button.draw(screen):
                placing_turrets = False
        #se torre selecionada mostrar upgrade
        if selected_turret:
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
                #show cost of upgrade and draw the button
                draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
                screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
                if upgrade_button.draw(screen):
                    if world.money >= c.UPGRADE_COST:
                        selected_turret.upgrade()
                        world.money -= c.UPGRADE_COST

    else:
        pg.draw.rect(screen,"dodgerblue",(200,200,400,200),border_radius = 30)
        if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)   
        elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
        #restart level
        if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pg.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            #grupos vazios
            enemy_group.empty()
            turret_group.empty()
            play_game_over_music()
    #Handler
    for event in pg.event.get():
        #sair
        if event.type == pg.QUIT:
            run = False
        #mouse
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            #o mouse esta no jogo?
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                selected_turret = None
                clear_selection()
                if placing_turrets == True:
                     #checar dinheiro
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)


    #atualizar display
    pg.display.flip()

pg.quit()