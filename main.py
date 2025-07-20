import pygame
import sys
import tiles
import player
import entity
import enemy
import render
import json
import math
import const
import level
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
font = pygame.font.Font(pygame.font.get_default_font(),16)
camera_x = 0
camera_y = 0
player_chunk_x=0
player_chunk_y=0
target_camera_x = 0
target_camera_y = 0
previous_camera_x = 1
previous_camera_y = 1
dx = 0
dy = 0
px=0
py=0
ground=False
TERMINAL_V=1.5
max_speed=0.7
accel = 0.15
deccel = 0.2
jump_hight=-1
gravity=0.12
show_hitboxs=False

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
    pygame.rect.Rect(SCREEN_WIDTH / 2-24, SCREEN_HIGHT / 2-36, 24, 36),
    4,
)
flip = False
dirty_player_idle = player_idle

select_tile = pygame.image.load("./assets/tiles/select.png")
select_tile = pygame.transform.scale(select_tile,(16,16)).convert_alpha()
dirty_select_tile = select_tile
real_mouse_tile_pos=(0,0)
mouse_tile_pos = (0,0)

preview_tile = []
for i in range(-2,96):
    preview_tile.append(pygame.transform.scale(pygame.image.load("./assets/tiles/sprite_"+str(i)+".png"),(16,16)))
the_tile = -2

with open("./assets/map1.json") as json_file:
    try:
        data = json.load(json_file)
        map_data = data["map"]
        player_data = data["other"]
        if player_data["version"] < 1.3:
            map_data = level.upgrade_level_data(map_data,player_data["version"],player_data)
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

hb_list = ["full","top-half","bottom-half"]
atr_list = ["collide","half","kill"]
atr_list_id = 0
list_id = 0
hit_boxes = {
    "full":pygame.Rect(0,0,16,16),
    "top-half":pygame.Rect(0,0,16,8),
    "bottom-half":pygame.Rect(0,8,16,8)
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
    if edit:
        dy=0
    if abs(dx)<=0.1:
        dx=0
    flag = False
    if key[pygame.K_a]:
        dx += accel * delta
        flag=True
        flip=True
    if key[pygame.K_d]:
        dx += -accel * delta
        flag=True
        flip=False
    if key[pygame.K_s] and edit:
        dy += accel * delta
    if key[pygame.K_w]:
        if edit:
            dy = -accel * delta
        else:
            if ground:
                dy=jump_hight
    if abs(dx)!=0 and not flag:
        if dx>0:
            dx-=deccel
        else:
            dx+=deccel
    if abs(dx)>=max_speed:
        if dx>0:
            dx=max_speed
        else:
            dx=-max_speed
    if not edit:
        dy+=gravity
    if dy>TERMINAL_V:
        dy=TERMINAL_V
    collision = False
    a_fake.shift(-camera_x, -camera_y)
    tile_map.reload(map_data)
    tile_state = tile_map.get_pos(camera_x, camera_y)
    tx = dx
    ty = dy
    ground=False
    while abs(dx*16) > 1:# or abs(dy*16) >1:
        if dx>1/16:
            camera_x-=1/16
            dx-=1/16
        elif dx< -1/16:    
            camera_x+=1/16
            dx+=1/16
            
        a_fake.shift(-camera_x, -camera_y)
        tile_map.reload(map_data)
        tile_state = tile_map.get_pos(camera_x, camera_y)
        for object in tile_state:
            try:
                the_hitbox = hit_boxes[hitbox_assign[tile_map.start_pos[object]["type"]]["type"]]
            except:
                continue
            the_hitbox = the_hitbox.move(tile_map.start_pos[object]["x"]*16,tile_map.start_pos[object]["y"]*16)
            if the_hitbox.colliderect(player_idle.hitbox):
                if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "half":
                    continue
                collision = True
                if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "kill" and (not edit):
                    pygame.quit()
                    sys.exit()
                break
        if collision and (not edit):
            if dx>0:
                camera_x+=1/16
                dx+=1/16
            elif dx< 0:    
                camera_x-=1/16
                dx-=1/16
            
            a_fake.shift(-camera_x, -camera_y)
            tile_map.reload(map_data)
            tile_state = tile_map.get_pos(camera_x, camera_y)
            break
    collision = False
    while abs(dy*16) > 1:# or abs(dy*16) >1:
        
        if dy>1/16:
            camera_y+=1/16
            dy-=1/16
        elif dy< -1/16:    
            camera_y-=1/16
            dy+=1/16    
        a_fake.shift(-camera_x, -camera_y)
        tile_map.reload(map_data)
        tile_state = tile_map.get_pos(camera_x, camera_y)
        for object in tile_state:
            try:
                the_hitbox = hit_boxes[hitbox_assign[tile_map.start_pos[object]["type"]]["type"]]
            except:
                continue
            the_hitbox = the_hitbox.move(tile_map.start_pos[object]["x"]*16,tile_map.start_pos[object]["y"]*16)
            if the_hitbox.colliderect(player_idle.hitbox):
                # print(the_hitbox.bottom<=player_idle.hitbox.bottom)
                if dy<=0 and hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "half":
                    continue
                collision = True
                if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "kill" and (not edit):
                    pygame.quit()
                    sys.exit()
                break
        if collision and (not edit):
            if dy>0:
                camera_y-=1/16
                dy+=1/16
                ground = True
            elif dy< 0:    
                camera_y+=1/16
                dy-=1/16
            
            a_fake.shift(-camera_x, -camera_y)
            tile_map.reload(map_data)
            tile_state = tile_map.get_pos(camera_x, camera_y)
            break
    
    dx=tx
    dy=ty  
    player_chunk_x = round(camera_x//10)
    player_chunk_y = round(camera_y//10)

    #editor
    if edit and key[pygame.K_g]:
        camera_x=round(camera_x)
        camera_y=round(camera_y)
        real_mouse_tile_pos=(round(real_mouse_tile_pos[0]),round(real_mouse_tile_pos[1]))
        mouse_tile_pos=(round(mouse_tile_pos[0]),round(mouse_tile_pos[1])) # type: ignore
    if key[pygame.K_e]:
        try:
            the_tile = int(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["type"])
        except:
            the_tile = 0
    if key[pygame.K_c] and edit:
        # print(real_mouse_tile_pos[0])
        hitbox_assign[str(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["type"])]={"type":hb_list[list_id],"attribute":"collide"}
        # print(str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1]))
        # print(list_id)
        list_id+=1
        # print(str(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["type"]))
        
        if list_id==len(hb_list):
            list_id=0
    if key[pygame.K_c] and edit and (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]):
        hitbox_assign[str(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["type"])]["attribute"]=atr_list[atr_list_id]
        atr_list_id+=1
        if atr_list_id==len(atr_list):
            atr_list_id=0
    try:
        if key[pygame.K_f] and edit:
            # print(real_mouse_tile_pos[0])
            map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["flip-x"]=not(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["flip-x"])
        if key[pygame.K_f] and edit and (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]):
            # print(real_mouse_tile_pos[0])
            map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["flip-y"]=not(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["flip-y"])
    except:
        print("stupid")
    if key[pygame.K_F9] and edit:
        show_hitboxs=not show_hitboxs
    if (key[pygame.K_LSHIFT] or key[pygame.K_RSHIFT]) and key[pygame.K_s]:
        with open(join("./assets/",input("file name:")),mode="w") as f:
            data={"map":map_data,"other":{"cx":camera_x,"cy":camera_y,"version":1.3}}
            json.dump(data, f, ensure_ascii=False, indent=4)
        with open(join("./assets/","hit_box.json"),mode="w") as f:
            json.dump(hitbox_assign, f, ensure_ascii=False, indent=4)
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
            # print(type(the_tile))
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
        "y":real_mouse_tile_pos[1]-camera_y,
        "flip-x":False,
        "flip-y":False,
        "chunk-x":round((real_mouse_tile_pos[0]-camera_x)//10),
        "chunk-y":round((real_mouse_tile_pos[1]-camera_y)//10),
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
    pen.draw("block", tile_state, {"chunk_x":player_chunk_x,"chunk_y":player_chunk_y})

    if edit:
        camera_x=round(camera_x)
        camera_y=round(camera_y)
        real_mouse_tile_pos=(round(real_mouse_tile_pos[0]),round(real_mouse_tile_pos[1]))
        mouse_tile_pos=(round(mouse_tile_pos[0]),round(mouse_tile_pos[1])) # type: ignore
        a_fake.shift(-camera_x, -camera_y)
        tile_map.reload(map_data)
        tile_state = tile_map.get_pos(camera_x, camera_y)
        if show_hitboxs:
            pygame.draw.rect(screen,"red",player_idle.hitbox)
            for object in tile_state:
                try:
                    the_hitbox = hit_boxes[hitbox_assign[tile_map.start_pos[object]["type"]]["type"]]
                except:
                    continue
                the_hitbox = the_hitbox.move(tile_map.start_pos[object]["x"]*16,tile_map.start_pos[object]["y"]*16)
                if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "collide":
                    pygame.draw.rect(screen,"blue",the_hitbox)
                elif hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "kill":
                    pygame.draw.rect(screen,"red",the_hitbox)
                elif hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "half":
                    pygame.draw.rect(screen,"cyan",the_hitbox)
    
    #绘制preview
    if edit:
        pen.draw("preview", {"preview":preview_tile[int(the_tile)+2],"pos":mouse_tile_pos},{"type":-1})
    
    #绘制选择
    if edit:
        screen.blit(select_tile,mouse_tile_pos)

    #绘制玩家
    player_idle.draw(screen)

    screen.blit(font.render("fps:"+str(round(clock.get_fps())),True,"white"),(0,0))
    screen.blit(font.render("x:"+str(camera_x),True,"white"),(0,16))
    screen.blit(font.render("y:"+str(camera_y),True,"white"),(0,32))
    screen.blit(font.render("chunk_x:"+str(player_chunk_x),True,"white"),(0,48))
    screen.blit(font.render("chunk_y:"+str(player_chunk_y),True,"white"),(0,64))
    screen.blit(font.render("dx:"+str(dx),True,"white"),(0,80))
    screen.blit(font.render("dy:"+str(dy),True,"white"),(0,96))

    #更新画面

    pygame.display.flip()
    pygame.display.update()
    clock.tick()
