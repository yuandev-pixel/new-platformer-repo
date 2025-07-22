import pygame
import sys
import tiles
import player as pl
import entity
import enemy
import render
import json
import math
import const
import level
from os.path import isfile, join

pygame.init()

full_tag = pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF | pygame.HWSURFACE
test_tag = pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
screen = pygame.display.set_mode(const.SCREEN_SIZE, flags=test_tag, vsync = 1)
clock = pygame.time.Clock()
tick_count=0
font = pygame.font.Font("./fonts/Helvetica.ttf",16)
big_font = pygame.font.Font("./fonts/Helvetica.ttf",32)
biger_font = pygame.font.Font("./fonts/Helvetica.ttf",48)
show_hitboxs=False
show_debug_info = False
player = pl.Player()

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

menu = "game"

pause_items = ["resume","save map","quit"]
select_anti_buffer = False
selected_item = 0

sfx_switch = pygame.mixer.Sound("./assets/sfx/switch.wav")
sfx_select = pygame.mixer.Sound("./assets/sfx/select.wav")
sfx_lose = pygame.mixer.Sound("./assets/sfx/lose.wav")

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
    if menu=="game":
        #移动逻辑
        key = pygame.key.get_pressed()
        player.move(edit,delta,a_fake,tile_map,map_data,hit_boxes,hitbox_assign)
        
        #editor
        if edit and key[pygame.K_g]:
            player.camera_x=round(player.camera_x)
            player.camera_y=round(player.camera_y)
            real_mouse_tile_pos=(round(real_mouse_tile_pos[0]),round(real_mouse_tile_pos[1]))
            mouse_tile_pos=(round(mouse_tile_pos[0]),round(mouse_tile_pos[1])) # type: ignore
        if key[pygame.K_e]:
            try:
                the_tile = int(map_data[str(real_mouse_tile_pos[0]*75)+"."+str(real_mouse_tile_pos[1])]["type"])
            except:
                the_tile = 0
        if key[pygame.K_ESCAPE]:
            menu="pause" 
            sfx_select.play()
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
        if key[pygame.K_F8] and edit:
            show_debug_info=not show_debug_info
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
            "x":real_mouse_tile_pos[0]-player.camera_x,
            "y":real_mouse_tile_pos[1]-player.camera_y,
            "flip-x":False,
            "flip-y":False,
            "chunk-x":round((real_mouse_tile_pos[0]-27)//10),
            "chunk-y":round((real_mouse_tile_pos[1]-27)//10),
            }
            tile_map.reload(map_data)
            
        #更新角色
        player.player_idle.update(round(const.SCREEN_CENTER[0]) - 24, round(const.SCREEN_CENTER[1]) - 48)
        player.player_run.update(round(const.SCREEN_CENTER[0]) - 24, round(const.SCREEN_CENTER[1]) - 48)


        #选择格子
        mouse_pos = pygame.mouse.get_pos()
        mouse_tile_pos = mouse_pos[0]//16*16, mouse_pos[1]//16*16
        real_mouse_tile_pos = mouse_tile_pos[0]/16 + player.camera_x, mouse_tile_pos[1]/16 + player.camera_y

        #绘制部分

        #绘制格子
        pen.draw("block", player.tile_state, {"chunk_x":player.player_chunk_x,"chunk_y":player.player_chunk_y})

        if edit:
            player.camera_x=round(player.camera_x)
            if player.dy>0:
                player.camera_y=math.ceil(player.camera_y)
            else:
                player.camera_y=math.floor(player.camera_y)
            real_mouse_tile_pos=(round(real_mouse_tile_pos[0]),round(real_mouse_tile_pos[1]))
            mouse_tile_pos=(round(mouse_tile_pos[0]),round(mouse_tile_pos[1])) # type: ignore
            a_fake.shift(-player.camera_x, -player.camera_y)
            tile_map.reload(map_data)
            player.tile_state = tile_map.get_pos(player.camera_x, player.camera_y)
            if show_hitboxs:
                pygame.draw.rect(screen,"red",player.player_idle.hitbox)
                for object in player.tile_state:
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
        if player.animation=="idle":
            x_scale=player.idle_transform[tick_count%len(player.idle_transform)][0]
            y_scale=player.idle_transform[tick_count%len(player.idle_transform)][1]
        else:
            x_scale=player.jump_transform[player.jump_frames][0]
            y_scale=player.jump_transform[player.jump_frames][1]

        if player.idle:
            player.player_idle.draw(screen,player.flip,False,x_scale,y_scale)
        else:
            player.player_run.draw(screen,player.flip,False,x_scale,y_scale)

        if edit and show_debug_info:
            screen.blit(font.render("fps:"+str(round(clock.get_fps())),True,"white"),(0,0))
            screen.blit(font.render("x:"+str(player.camera_x),True,"white"),(0,16))
            screen.blit(font.render("y:"+str(player.camera_y),True,"white"),(0,32))
            screen.blit(font.render("chunk_x:"+str(player.player_chunk_x),True,"white"),(0,48))
            screen.blit(font.render("chunk_y:"+str(player.player_chunk_y),True,"white"),(0,64))
            screen.blit(font.render("dx:"+str(player.dx),True,"white"),(0,80))
            screen.blit(font.render("dy:"+str(player.dy),True,"white"),(0,96))
    elif menu=="pause":
        keys = pygame.key.get_pressed()
        s_flag = False
        if keys[pygame.K_RETURN]:
            sfx_select.play()
            if selected_item==0:
                menu="game"
            elif selected_item==1:
                active = True
                input_text=""
                while active:
                    screen.fill("#21263f")
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN and active:
                            if event.key == pygame.K_BACKSPACE:
                                input_text = input_text[:-1]  # Remove last character
                            elif event.key == pygame.K_RETURN:
                                active=False
                            else:
                                input_text += event.unicode  # Add typed character to input
                    screen.blit(big_font.render("map name:"+input_text,True,"white"),(const.SCREEN_WIDTH/2-big_font.size("map name:"+input_text)[0]/2,const.SCREEN_HIGHT/2-32))
                    pygame.display.flip()
                    pygame.display.update()
                    clock.tick()
                    tick_count+=1

                with open(join("./assets/",input_text),mode="w") as f:
                    data={"map":map_data,"other":{"cx":player.camera_x,"cy":player.camera_y,"version":1.3}}
                    json.dump(data, f, ensure_ascii=False, indent=4)
                with open(join("./assets/","hit_box.json"),mode="w") as f:
                    json.dump(hitbox_assign, f, ensure_ascii=False, indent=4)
            elif selected_item==2:
                pygame.quit()
                sys.exit()

        if keys[pygame.K_UP]:
            s_flag=True
            if not select_anti_buffer:
                sfx_switch.play()
                selected_item-=1
                select_anti_buffer=True
            if selected_item<0:
                selected_item = len(pause_items)-1
        if keys[pygame.K_DOWN]:
            s_flag=True
            if not select_anti_buffer:
                sfx_switch.play()
                selected_item+=1
                select_anti_buffer=True
            if selected_item>=len(pause_items):
                selected_item=0
        if not s_flag:
            select_anti_buffer=False
        screen.blit(biger_font.render("Paused",True,"white"),(const.SCREEN_WIDTH/2-biger_font.size("Paused")[0]/2,50))
        for i,text in enumerate(pause_items):
            if i == selected_item:
                if i==2:
                    screen.blit(biger_font.render(text,True,(250,50,75)),(const.SCREEN_WIDTH/2-biger_font.size(text)[0]/2,i*68+250))
                else:
                    screen.blit(biger_font.render(text,True,(75,50,250)),(const.SCREEN_WIDTH/2-biger_font.size(text)[0]/2,i*68+250))
            else:
                screen.blit(big_font.render(text,True,"white"),(const.SCREEN_WIDTH/2-big_font.size(text)[0]/2,i*68+250))
    #更新画面

    pygame.display.flip()
    pygame.display.update()
    clock.tick()
    tick_count+=1
