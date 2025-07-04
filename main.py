"""
    note:unstable
"""

import pygame
import sys
import tiles
import player
import entity
import enemy
import render
import json
import math
from os import listdir
from os.path import isfile, join

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HIGHT)
SCREEN_CENTER = (SCREEN_WIDTH / 2, SCREEN_HIGHT / 2)
full_tag = pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE
test_tag = pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
screen = pygame.display.set_mode(SCREEN_SIZE, flags=test_tag, vsync = 1)
clock = pygame.time.Clock()
camera_x = 0
camera_y = 0
target_camera_x = 0
target_camera_y = 0
previous_camera_x = 1
previous_camera_y = 1
dx = 0
dy = 0

player_idle_frames = [
    pygame.transform.scale(
        pygame.image.load(join("./assets/entitys/player/idle/", f)), (24, 48)
    )
    for f in listdir("./assets/entitys/player/idle")
    if isfile(join("./assets/entitys/player/idle", f))
]

player_idle = entity.AnimatedEntity(
    round(SCREEN_WIDTH / 2) - 12,
    round(SCREEN_WIDTH / 2) - 24,
    player_idle_frames,
    pygame.rect.Rect(SCREEN_WIDTH / 2, SCREEN_WIDTH / 2, 24, 48),
    4,
)
dirty_player_idle = player_idle

select_tile = pygame.image.load("./assets/tiles/select.png")
select_tile = pygame.transform.scale(select_tile,(16,16)).convert_alpha()
dirty_select_tile = select_tile
real_mouse_tile_pos=(0,0)

preview_tile = []
for i in range(-2,96):
    preview_tile.append(pygame.transform.scale(pygame.image.load("./assets/tiles/sprite_"+str(i)+".png"),(16,16)))
the_tile = -2

with open("./assets/map1.json") as json_file:
    try:
        data = json.load(json_file)
        map_data = data["map"]
        player_data = data["other"]
    except:
        data = {"map":{},"other":{"cx":0,"cy":0}}
        map_data = data["map"]
        player_data = data["other"]
with open("./assets/hit_box.json") as wow:
    hitbox_assign = json.load(wow)

pen = render.RenderPen(screen)
tile_map = tiles.TileGrid(map_data)
a_fake = tiles.FakeGrid()

tile_map.cx += player_data["cx"]
tile_map.cy += player_data["cy"]

lt = 0

edit = True

hit_boxes = {
    "full":pygame.Rect(0,0,16,16)
}

while True:
    #清空屏幕

    screen.fill("#21263f")

    #逻辑部分

    #帧率改变逻辑
    delta = round(60 / (clock.get_fps() + 0.000000000000000000000000000000000000000001), 2)

    #退出游戏
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #移动逻辑
    key = pygame.key.get_pressed()
    if key[pygame.K_a]:
        camera_x -= math.ceil(0.1 * delta)
        dx = math.ceil(0.1 * delta)
    if key[pygame.K_d]:
        camera_x += math.ceil(0.1 * delta)
        dx = -math.ceil(0.1 * delta)
    if key[pygame.K_s] and edit:
        camera_y += math.ceil(0.1 * delta)
        dy = math.ceil(0.1 * delta)
    if key[pygame.K_w]:
        if edit:
            camera_y -= math.ceil(0.1 * delta)
            dy = -math.ceil(0.1 * delta)
        else:
            dy=-1
    if not edit:
        camera_y+=dy
        dy+=0.05
    a_fake.shift(-camera_x, -camera_y)
    tile_map.reload(map_data)
    tile_state = tile_map.get_pos(camera_x, camera_y)
    for object in tile_state:
        print("hey")
        try:
            the_hitbox = hit_boxes[hitbox_assign[tile_map.start_pos[object]["type"]]["type"]].move(object["x"],object["y"])
            if player_idle.hitbox.colliderect(the_hitbox):
                camera_x -= dx
                camera_y -= dy
                a_fake.shift(-camera_x, -camera_y)
                tile_map.reload(map_data)
                tile_state = tile_map.get_pos(camera_x, camera_y)
                print("p")
                pygame.draw.rect(screen,"blue",(the_hitbox.topleft[0],the_hitbox.topleft[1],16,16))
                break
        except:
           print("nope")
           continue

    #editor
    if edit and key[pygame.K_g]:
        camera_x=round(camera_x)
        camera_y=round(camera_y)
        real_mouse_tile_pos=(round(real_mouse_tile_pos[0]),round(real_mouse_tile_pos[1]))
        mouse_tile_pos=(round(mouse_tile_pos[0]),round(mouse_tile_pos[1])) # type: ignore
    if key[pygame.K_e]:
        try:
            the_tile = map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["type"]
        except:
            the_tile = 0
    if (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]) and key[pygame.K_s]:
        with open(join("./assets/",input("file name:")),mode="w") as f:
            data={"map":map_data,"other":{"cx":camera_x,"cy":camera_y}}
            json.dump(data, f, ensure_ascii=False, indent=4)
    if (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]) and key[pygame.K_l]:
        with open(join("./assets/",input("file name:")),mode="r") as json_file:
            try:
                data = json.load(json_file)
                map_data = data["map"]
                player_data = data["other"]
            except:
                data = {"map":{},"other":{"cx":0,"cy":0}}
                map_data = data["map"]
                player_data = data["other"]
    if (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]) and key[pygame.K_e]:
        edit = not edit
    if lt==5:
        if key[pygame.K_DOWN]:
            the_tile += 8
            if the_tile>92:
                the_tile-=8
            lt = 0
        if key[pygame.K_UP]:
            the_tile -= 8
            if the_tile<0:
                the_tile+=8
            lt = 0
        if key[pygame.K_LEFT]:
            if the_tile%8==0:
                the_tile+=1
            the_tile -= 1
            lt = 0
        if key[pygame.K_RIGHT]:
            if the_tile%8==7:
                the_tile-=1
            the_tile += 1
            lt = 0
    else:
        if lt<5:
            lt+=1
    
    if  pygame.mouse.get_pressed()[0] and edit:
        map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]={
        "type":str(the_tile),
        "x":real_mouse_tile_pos[0]-camera_x,
        "y":real_mouse_tile_pos[1]-camera_y
        }
        tile_map.reload(map_data)
        
    #更新角色
    player_idle.update(round(SCREEN_CENTER[0]) - 24, round(SCREEN_CENTER[1]) - 48)


    #选择格子
    mouse_pos = pygame.mouse.get_pos()
    mouse_tile_pos = mouse_pos[0]//16*16, mouse_pos[1]//16*16
    real_mouse_tile_pos = mouse_tile_pos[0]/16 + camera_x, mouse_tile_pos[1]/16 + camera_y

    #绘制部分

    #绘制格子
    pen.draw("block", tile_state)
    
    #绘制preview
    if edit:
        pen.draw("preview", {"preview":preview_tile[int(the_tile)+2],"pos":mouse_tile_pos})
    
    #绘制选择
    if edit:
        screen.blit(select_tile,mouse_tile_pos)

    #绘制玩家
    player_idle.draw(screen)

    #更新画面

    pygame.display.flip()
    pygame.display.update()
    clock.tick(120)
