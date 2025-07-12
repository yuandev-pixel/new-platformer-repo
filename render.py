import pygame

class RenderPen:
    def __init__(self,screen:pygame.Surface) -> None:
        self.screen = screen
        self.tiles = {}
        for i in range(-2, 96):
            self.tiles[i] = (pygame.transform.scale(pygame.image.load("./assets/tiles/sprite_"+str(i)+".png"),(16,16)))
    def draw(self,type:str,data:dict) -> None:
        if type == "block":
            for block in data.values():
                # print(block)
                if int(block["type"]) != -1 or int(block["type"]) != 0:
                    draw_block=self.tiles[int(block["type"])]
                    if block["flip-x"]:
                        draw_block=pygame.transform.flip(draw_block,True,False)
                    if block["flip-y"]:
                        draw_block=pygame.transform.flip(draw_block,False,True)
                    self.screen.blit(draw_block,(block["x"]*16,block["y"]*16))
        if type == "preview":
            self.screen.blit(data["preview"],data["pos"])
