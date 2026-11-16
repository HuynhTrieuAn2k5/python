"""ASCII Christmas Tree 2026 — tái dựng độc lập từ hình ảnh video.

Yêu cầu: Python >=3.10, pygame >=2.5
Chạy: python -m pip install -r requirements.txt
      python christmas_tree.py

Điều khiển:
  Space   : Tạm dừng / tiếp tục
  R       : Chạy lại hoạt cảnh
  Up/Down : Tăng / giảm tốc độ quay
  F hoặc F11: Toàn màn hình
  ESC     : Thoát
"""
from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass

try:
    import pygame  # type: ignore[reportMissingImports]
except ImportError:
    print("Chưa cài pygame. Mở terminal trong thư mục python và chạy:")
    print("    python -m pip install -r requirements.txt")
    raise SystemExit(1)

WIDTH, HEIGHT, FPS = 720, 860, 30
CHAR_W, ROW_H = 6.35, 10.25
CENTER, BASE, TREE_HEIGHT, RADIUS = 358.0, 586.0, 437.0, 212.0
TAU = math.tau
GLYPHS = "+xvwoO#@&%*^=~"
PALETTE = {
    "background": (4, 8, 18),
    "green0": (11, 62, 45), "green1": (23, 107, 64),
    "green2": (33, 143, 74), "green3": (48, 189, 96),
    "gold": (243, 200, 75), "gold_soft": (177, 124, 39),
    "red": (222, 71, 101), "blue": (110, 167, 245),
    "cyan": (101, 197, 173), "purple": (152, 120, 183),
    "snow": (225, 233, 255), "gray": (125, 136, 160),
}

RNG = random.Random(240122)


@dataclass(slots=True)
class Point:
    x: float
    y: float
    z: float
    glyph: str
    shade: float = 0.0
    phase: float = 0.0
    color: str = "green1"


@dataclass(slots=True)
class Flake:
    x: float
    y: float
    speed: float
    drift: float
    glyph: str
    shade: int


def clamp(v: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, v))


def smoothstep(v: float) -> float:
    v = clamp(v)
    return v * v * (3.0 - 2.0 * v)


def make_geometry() -> tuple[list[Point], list[Point], list[Point], list[Flake]]:
    """Tạo một lần tập hạt cây 3D, kim tuyến, bóng đèn và tuyết."""
    tree: list[Point] = []
    for i in range(7300):
        y = 1.0 - math.sqrt(RNG.random())
        phi = RNG.random() * TAU
        branch = 0.72 + RNG.random() * 0.29
        tier = 1.0 + 0.075 * math.cos(9.0 * math.pi * y) + 0.03 * math.sin(63*y+phi*3)
        radial = (1.0-y)*branch*tier
        tree.append(Point(math.cos(phi)*radial,y,math.sin(phi)*radial,
                          RNG.choice(GLYPHS),RNG.random(),RNG.random()*TAU))

    ribbons: list[Point] = []
    for band in range(4):
        for i in range(360):
            phi = i/359*TAU
            y = 0.15 + band*0.2 + 0.022*math.sin(phi*1.65+band*2)
            radius = (1-y)*1.015
            ribbons.append(Point(math.cos(phi)*radius,y,math.sin(phi)*radius,
                                 RNG.choice('~=+*#')))

    bulbs: list[Point] = []
    colors = ['gold','gold','red','red','blue','cyan','purple']
    for _ in range(74):
        y = .075 + RNG.random()*.835
        phi = RNG.random()*TAU
        radial = (1-y)*(1.003 + RNG.random()*.035)
        bulbs.append(Point(math.cos(phi)*radial,y,math.sin(phi)*radial,
                           RNG.choice('@O*#'),phase=RNG.random()*TAU,
                           color=RNG.choice(colors)))

    flakes = [Flake(RNG.random()*WIDTH,RNG.random()*HEIGHT,
                    12+RNG.random()*29,RNG.random()*TAU,
                    RNG.choice('++·**..'),RNG.randrange(3)) for _ in range(220)]
    return tree,ribbons,bulbs,flakes


class Atlas:
    """Bộ nhớ đệm mặt chữ: không rasterize font hàng nghìn lần mỗi frame."""
    def __init__(self) -> None:
        self.font = pygame.font.SysFont('consolas', 12)
        self.small = pygame.font.SysFont('consolas', 12)
        self.cache: dict[tuple[str, str, int], pygame.Surface] = {}

    def draw(self, screen: pygame.Surface, glyph: str, x: float, y: float,
             color: str, brightness: float = 1.0) -> None:
        strength = 0 if brightness < .65 else 1 if brightness < .87 else 2
        key = (glyph,color,strength)
        image = self.cache.get(key)
        if image is None:
            r,g,b = PALETTE[color]
            multiplier = (.57,.79,1.0)[strength]
            image = self.font.render(glyph,True,(int(r*multiplier),int(g*multiplier),int(b*multiplier)))
            self.cache[key] = image
        screen.blit(image,(round(x),round(y)-6))

    def line(self,screen:pygame.Surface,message:str,x:int,y:int,
             color:str='gray') -> None:
        s=self.small.render(message,True,PALETTE[color])
        screen.blit(s,(x,y))


class ChristmasTree:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption('ASCII Christmas Tree | 2026 — Space / R / F / Esc')
        self.clock=pygame.time.Clock()
        self.atlas=Atlas()
        self.tree,self.ribbons,self.bulbs,self.flakes=make_geometry()
        self.time=0.0
        self.speed=1.0
        self.paused=False
        self.fullscreen=False
        self.glyph_count=0

    def project(self,x:float,z:float,y:float,rotation:float) -> tuple[float,float,float]:
        cosine,sine=math.cos(rotation),math.sin(rotation)
        xr=x*cosine-z*sine
        zr=x*sine+z*cosine
        perspective=1+zr*.105
        return CENTER+RADIUS*xr*perspective,BASE-TREE_HEIGHT*y+zr*(1-y)*14,zr

    @staticmethod
    def put(grid:dict[int,tuple],x:float,y:float,z:float,
            glyph:str,color:str,bright:float=1.0,force:bool=False)->None:
        col,row=round(x/CHAR_W),round(y/ROW_H)
        if not(0<=col<114 and 0<=row<84): return
        key=row*120+col
        if force or key not in grid or z >= grid[key][0]:
            grid[key]=(z,glyph,color,bright,col*CHAR_W,row*ROW_H)

    def build_tree(self) -> tuple[dict[int,tuple],int,float]:
        t=self.time
        growth=smoothstep(t/7.9)
        floor_y=1.0-growth
        rot=t*.27*self.speed
        grid:dict[int,tuple]={}
        sine,cosine=math.sin(rot),math.cos(rot)
        # Vùng cây: phép quay ma trận và phép chiếu góc nhìn được nội tuyến để tiết kiệm CPU.
        for p in self.tree:
            if p.y<floor_y:continue
            xr=p.x*cosine-p.z*sine
            zr=p.x*sine+p.z*cosine
            x=CENTER+RADIUS*xr*(1+zr*.105)
            y=BASE-TREE_HEIGHT*p.y+zr*(1-p.y)*14
            depth=(zr+1)*.5
            shade=p.shade*.37+depth*.58+math.sin(t*2.1+p.phase)*.06
            color=('green3' if shade>.69 else 'green2' if shade>.48
                   else 'green1' if shade>.31 else 'green0')
            self.put(grid,x,y,zr,p.glyph,color,.70+depth*.38)

        for i in range(250):
            y=-.085+((i*53)%250)/250*.115
            x,z=math.sin(i*22.3)*.06,math.cos(i*17.7)*.06
            xx,yy,zz=self.project(x,z,y,rot)
            self.put(grid,xx,yy,zz+.01,'#','gold_soft',.58)

        if t>3.6:
            count=int(len(self.ribbons)*smoothstep((t-3.6)/3.9))
            for idx,p in enumerate(self.ribbons[:count]):
                if p.y<floor_y:continue
                x,y,z=self.project(p.x,p.z,p.y,rot)
                if z<-.18:continue
                color='gold' if math.sin(t*1.7+idx*.7)>.36 else 'gold_soft'
                self.put(grid,x,y,z+.08,p.glyph,color,.95)

        light_count=round(len(self.bulbs)*smoothstep((t-6.2)/4.8))
        for p in self.bulbs[:light_count]:
            if p.y<floor_y:continue
            x,y,z=self.project(p.x,p.z,p.y,rot)
            if z<-.12:continue
            twinkle=.70+.30*math.sin(t*4.2+p.phase)
            self.put(grid,x,y,z+.24,p.glyph,p.color,twinkle,True)
        self.glyph_count=len(grid)
        return grid,light_count,rot

    def draw_background(self) -> None:
        self.screen.fill(PALETTE['background'])
        for row in range(57,75):
            y=row*10.25
            faded=(120,128,148) if row<64 else (44,52,73)
            for col in range(1,114,3):
                if (col*17+row*31)%7<5:
                    pygame.draw.line(self.screen,faded,(col*CHAR_W,y),
                                     (col*CHAR_W+4,y),1)
        # Sao xa màu xanh lam rất mờ
        for i in range(70):
            x=int((i*113.73+17.8)%WIDTH)
            y=int((i*187.41+3.7)%710)
            pygame.draw.circle(self.screen,(19,29,47),(x,y),1)

    def draw_snow(self) -> None:
        t=self.time
        for f in self.flakes:
            x=(f.x+math.sin(t*.8+f.drift)*9)%WIDTH
            y=(f.y+t*f.speed)%(HEIGHT+30)-15
            color=['gray','snow','snow'][f.shade]
            self.atlas.draw(self.screen,f.glyph,x,y,color,.66 if f.shade==0 else 1.0)

    def draw_glyphs(self,grid:dict[int,tuple]) -> None:
        for _,glyph,color,bright,x,y in grid.values():
            if color in ('gold','red','blue','cyan','purple') and bright>.73:
                pygame.draw.circle(self.screen,tuple(c//4 for c in PALETTE[color]),
                    (round(x+3),round(y)),5)
            self.atlas.draw(self.screen,glyph,x,y,color,bright)

    def draw_star(self) -> None:
        appearance=smoothstep((self.time-10.0)/2.2)
        if appearance<.01:return
        lines=('    *    ','  * # *  ','* * @ * *','  # * #  ','    *    ')
        for r,line in enumerate(lines):
            for c,glyph in enumerate(line):
                if glyph==' ':continue
                x=CENTER+(c-4)*6.5-2
                y=130+(r-2)*10.2
                pygame.draw.circle(self.screen,(66,51,11),(round(x+3),round(y)),6)
                self.atlas.draw(self.screen,glyph,x,y,'gold',appearance)

    def draw_gift(self,x:float,y:float,cols:int,body:str,ribbon:str) -> None:
        rows=max(4,round(cols*.65))
        for r in range(rows):
            for c in range(cols):
                border=r in (0,rows-1) or c in (0,cols-1)
                bow=c==cols//2 or r==round(rows/2)
                glyph='@' if bow else '#' if border else '%' if (c+r)%4==0 else 'x'
                color=ribbon if bow else body
                self.atlas.draw(self.screen,glyph,x+c*CHAR_W,y+r*ROW_H,color)
        self.atlas.draw(self.screen,'*',x+cols*CHAR_W/2-9,y-12,ribbon)
        self.atlas.draw(self.screen,'*',x+cols*CHAR_W/2+4,y-12,ribbon)

    def draw_gifts(self) -> None:
        gifts=((9.3,150,575,10,'red','gold'),
               (10.4,293,595,10,'blue','gold'),
               (11.3,518,573,9,'red','gold'))
        for start,x,y,size,body,ribbon in gifts:
            progress=smoothstep((self.time-start)/1.0)
            if progress>0:self.draw_gift(x,y-(1-progress)*20,size,body,ribbon)

    def draw_hud(self,bulbs:int,angle:float)->None:
        self.atlas.line(self.screen,f'◆ t {self.time:05.2f}s',620,25,'gold')
        if self.time>=8.2:
            message='M E R R Y   C H R I S T M A S   2 0 2 6'
            self.atlas.line(self.screen,message,200,751,'gold')
        self.atlas.line(self.screen,'@cfs.ascii',20,787)
        self.atlas.line(self.screen,f'-rotation {math.degrees(angle)%360:06.2f}°   -lights x{bulbs}',20,805)
        self.atlas.line(self.screen,f'-letters {self.glyph_count:,}',20,823)

    def run(self) -> None:
        running=True
        while running:
            dt=min(self.clock.tick(FPS)/1000.0,.05)
            for event in pygame.event.get():
                if event.type==pygame.QUIT:running=False
                elif event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:running=False
                    elif event.key==pygame.K_SPACE:self.paused=not self.paused
                    elif event.key==pygame.K_r:self.time=0.0;self.paused=False
                    elif event.key==pygame.K_UP:self.speed=min(4.0,self.speed+.25)
                    elif event.key==pygame.K_DOWN:self.speed=max(.25,self.speed-.25)
                    elif event.key in (pygame.K_f,pygame.K_F11):
                        self.fullscreen=not self.fullscreen
                        flag=pygame.FULLSCREEN if self.fullscreen else 0
                        self.screen=pygame.display.set_mode((WIDTH,HEIGHT),flag)
            if not self.paused:self.time+=dt
            self.draw_background()
            self.draw_snow()
            grid,bulbs,angle=self.build_tree()
            self.draw_glyphs(grid)
            self.draw_star()
            self.draw_gifts()
            self.draw_hud(bulbs,angle)
            pygame.display.flip()
        pygame.quit()

def main() -> int:
    try:
        ChristmasTree().run()
        return 0
    except pygame.error as err:
        print(f'Pygame gặp lỗi: {err}', file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())