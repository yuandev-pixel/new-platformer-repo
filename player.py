import pygame
import entity
import sys
import const
from os import listdir
from os.path import isfile, join

class Player:
    def __init__(self) -> None:
        self.camera_x = 0
        self.camera_y = 0
        self.player_chunk_x=0
        self.player_chunk_y=0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.previous_camera_x = 1
        self.previous_camera_y = 1
        self.dx = 0
        self.dy = 0
        self.px=0
        self.py=0
        self.ground=False
        self.TERMINAL_V=1.5
        self.max_speed=0.7
        self.accel = 0.15
        self.deccel = 0.25
        self.jump_hight=-1
        self.gravity=0.12
        self.tile_state={}
        self.animation = "idle"
        self.jump_frames=0
        self.idle_transform = [(24,48)]
        self.jump_transform = [(24,48),(20,52),(17,55),(15,57),(14,58),(14,58),(15,57),(17,55),(20,52),(24,48)]
                
        self.player_idle_frames = [
            pygame.transform.scale(
                pygame.image.load(join("./assets/entitys/player/idle/", f)), (24, 48)
            )
            for f in listdir("./assets/entitys/player/idle")
            if isfile(join("./assets/entitys/player/idle", f))
        ]

        self.player_run_frames = [
            pygame.transform.scale(
                pygame.image.load(join("./assets/entitys/player/running", f)), (24, 48)
            )
            for f in listdir("./assets/entitys/player/running")
            if isfile(join("./assets/entitys/player/running", f))
        ]

        self.player_idle = entity.AnimatedEntity(
            round(const.SCREEN_WIDTH / 2) - 12,
            round(const.SCREEN_WIDTH / 2) - 24,
            self.player_idle_frames,
            pygame.rect.Rect(const.SCREEN_WIDTH / 2-24, const.SCREEN_HIGHT / 2-36, 24, 36),
            4,
        )
        self.player_run = entity.AnimatedEntity(
            round(const.SCREEN_WIDTH / 2) - 12,
            round(const.SCREEN_WIDTH / 2) - 24,
            self.player_run_frames,
            pygame.rect.Rect(const.SCREEN_WIDTH / 2-24, const.SCREEN_HIGHT / 2-36, 24, 36),
            4,
        )
        self.flip = False
        self.idle = True
    def move(self,edit,delta,a_fake,tile_map,map_data,hit_boxes,hitbox_assign) -> None:
        key = pygame.key.get_pressed()
        if edit:
            self.dy=0
        if abs(self.dx)<=0.1:
            self.dx=0
        flag = False
        self.idle=True
        if key[pygame.K_a]:
            self.dx += self.accel * delta
            flag=True
            self.flip=True
            self.idle = False
        if key[pygame.K_d]:
            self.dx += -self.accel * delta
            flag=True
            self.flip=False
            self.idle = False
        if key[pygame.K_s] and edit:
            self.dy += self.accel * delta
        if key[pygame.K_w]:
            if edit:
                self.dy += -self.accel * delta
            else:
                if self.ground:
                    self.dy=self.jump_hight
                    self.animation="jump"
                    self.jump_frames=0
        if abs(self.dx)!=0 and not flag:
            if self.dx>0:
                self.dx-=self.deccel
            else:
                self.dx+=self.deccel
        if abs(self.dx)>=self.max_speed:
            if self.dx>0:
                self.dx=self.max_speed
            else:
                self.dx=-self.max_speed
        if not edit:
            self.dy+=self.gravity
        if abs(self.dy)>self.TERMINAL_V and not edit:
            self.dy=self.TERMINAL_V
        collision = False
        tile_map.reload(map_data)
        tile_state = tile_map.get_pos(self.camera_x, self.camera_y)
        tx = self.dx
        ty = self.dy
        self.ground=False
        while abs(self.dx*16) > 1:
            if self.dx>1/16:
                self.camera_x-=1/16
                self.dx-=1/16
            elif self.dx< -1/16:    
                self.camera_x+=1/16
                self.dx+=1/16
                
            a_fake.shift(-self.camera_x, -self.camera_y)
            tile_map.reload(map_data)
            tile_state = tile_map.get_pos(self.camera_x, self.camera_y)
            for object in tile_state:
                try:
                    the_hitbox = hit_boxes[hitbox_assign[tile_map.start_pos[object]["type"]]["type"]]
                except:
                    continue
                the_hitbox = the_hitbox.move(tile_map.start_pos[object]["x"]*16,tile_map.start_pos[object]["y"]*16)
                if the_hitbox.colliderect(self.player_idle.hitbox):
                    if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "half":
                        continue
                    collision = True
                    if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "kill" and (not edit):
                        pygame.quit()
                        sys.exit()
                    break
            if collision and (not edit):
                if self.dx>0:
                    self.camera_x+=1/16
                    self.dx+=1/16
                elif self.dx< 0:    
                    self.camera_x-=1/16
                    self.dx-=1/16
                
                a_fake.shift(-self.camera_x, -self.camera_y)
                tile_map.reload(map_data)
                tile_state = tile_map.get_pos(self.camera_x, self.camera_y)
                break
        collision = False
        while abs(self.dy*16) > 1:
            
            if self.dy>1/16:
                self.camera_y+=1/16
                self.dy-=1/16
            elif self.dy< -1/16:    
                self.camera_y-=1/16
                self.dy+=1/16    
            a_fake.shift(-self.camera_x, -self.camera_y)
            tile_map.reload(map_data)
            tile_state = tile_map.get_pos(self.camera_x, self.camera_y)
            for object in tile_state:
                try:
                    the_hitbox = hit_boxes[hitbox_assign[tile_map.start_pos[object]["type"]]["type"]]
                except:
                    continue
                the_hitbox = the_hitbox.move(tile_map.start_pos[object]["x"]*16,tile_map.start_pos[object]["y"]*16)
                if the_hitbox.colliderect(self.player_idle.hitbox):
                    if self.dy<=0 and hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "half":
                        continue
                    collision = True
                    if hitbox_assign[tile_map.start_pos[object]["type"]]["attribute"] == "kill" and (not edit):
                        pygame.quit()
                        sys.exit()
                    break
            if collision and (not edit):
                if self.dy>0:
                    self.camera_y-=1/16
                    self.dy+=1/16
                    self.ground = True
                elif self.dy< 0:    
                    self.camera_y+=1/16
                    self.dy-=1/16
                
                a_fake.shift(-self.camera_x, -self.camera_y)
                tile_map.reload(map_data)
                tile_state = tile_map.get_pos(self.camera_x, self.camera_y)
                ty=0
                break
        
        self.dx=tx
        self.dy=ty  
        self.player_chunk_x = round(self.camera_x//10)
        self.player_chunk_y = round(self.camera_y//10)
        if self.animation=="jump":
            self.jump_frames+=1
        if self.jump_frames==10:
            self.animation="idle"
            self.jump_frames=0
