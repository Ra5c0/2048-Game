# 2048 - Pygame (ZQSD + Arrows) - Menu (4x4/5x5/6x6) + Thème Clair/Sombre (C)
# pip install -r requirements.txt

import pygame, sys, random, json, os
pygame.init()

# --------------------------- Persistence ---------------------------
CFG_FILE = "2048_prefs.json"
def load_prefs():
    try:
        if os.path.exists(CFG_FILE):
            with open(CFG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"theme":"dark","best":{"4":0,"5":0,"6":0}}

def save_prefs(p):
    try:
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(p, f)
    except Exception:
        pass

PREFS = load_prefs()

# --------------------------- Themes ---------------------------
THEMES = {
    "dark": {
        "BG": (18,18,20),
        "BOARD": (35,35,40),
        "TEXT": (245,245,245),
        "SUB": (180,180,190),
        "SCORE_BG": (50,50,58),
        "EMPTY": (45,45,52),
        "overlay": (20,20,25,180),
        "menu_btn": (55,55,62),
        "menu_btn_active": (80,80,90),
    },
    "light": {
        "BG": (246,246,248),
        "BOARD": (210,210,220),
        "TEXT": (30,30,32),
        "SUB": (90,90,100),
        "SCORE_BG": (185,185,195),
        "EMPTY": (220,220,230),
        "overlay": (230,230,235,200),
        "menu_btn": (220,220,230),
        "menu_btn_active": (200,200,210),
    }
}
def theme_color(key): return THEMES[PREFS["theme"]][key]

# Tile palette (value -> (bg, fg))
PALETTE = {
    0:   ((45, 45, 52), (200, 200, 210)),
    2:   ((238, 228, 218), (119, 110, 101)),
    4:   ((237, 224, 200), (119, 110, 101)),
    8:   ((242, 177, 121), (249, 246, 242)),
    16:  ((245, 149, 99),  (249, 246, 242)),
    32:  ((246, 124, 95),  (249, 246, 242)),
    64:  ((246, 94, 59),   (249, 246, 242)),
    128: ((237, 207, 114), (249, 246, 242)),
    256: ((237, 204, 97),  (249, 246, 242)),
    512: ((237, 200, 80),  (249, 246, 242)),
    1024:((237, 197, 63),  (249, 246, 242)),
    2048:((237, 194, 46),  (249, 246, 242)),
}
def color_for(v):
    if v in PALETTE: return PALETTE[v]
    return ((60, 58, 50), (249, 246, 242))

# --------------------------- Window & Fonts ---------------------------
WIN_W = 560
TOP_UI = 120
BOARD_MARGIN = 24
TILE_MARGIN = 12
FPS = 60
ANIM_TIME = 160
POP_TIME = 120

screen = pygame.display.set_mode((WIN_W, 720), pygame.RESIZABLE)
pygame.display.set_caption("2048 — ZQSD • Menu + Thème")

FONT_NAME = pygame.font.get_default_font()
font_big   = pygame.font.SysFont(FONT_NAME, 44, bold=True)
font_tileL = pygame.font.SysFont(FONT_NAME, 40, bold=True)
font_tileM = pygame.font.SysFont(FONT_NAME, 32, bold=True)
font_tileS = pygame.font.SysFont(FONT_NAME, 24, bold=True)
font_ui    = pygame.font.SysFont(FONT_NAME, 20, bold=True)
font_small = pygame.font.SysFont(FONT_NAME, 16)

# --------------------------- Layout helpers ---------------------------
def compute_layout(grid):
    board_w = WIN_W - 2*BOARD_MARGIN
    cell = (board_w - (grid+1)*TILE_MARGIN) // grid
    board_h = (grid*cell + (grid+1)*TILE_MARGIN)
    window_h = TOP_UI + board_h + BOARD_MARGIN
    return cell, pygame.Rect(BOARD_MARGIN, TOP_UI, board_w, board_h), window_h

def cell_rect(board_rect, cell_size, r, c):
    x = board_rect.x + TILE_MARGIN + c*(cell_size + TILE_MARGIN)
    y = board_rect.y + TILE_MARGIN + r*(cell_size + TILE_MARGIN)
    return pygame.Rect(x, y, cell_size, cell_size)

# --------------------------- Game Logic ---------------------------
def empty_board(n): return [[0]*n for _ in range(n)]
def add_random_tile(b):
    n = len(b)
    empties = [(r,c) for r in range(n) for c in range(n) if b[r][c]==0]
    if not empties: return False
    r,c = random.choice(empties)
    b[r][c] = 4 if random.random() < 0.1 else 2
    return True

def slide_line(values):
    size = len(values)
    compact = [(i,v) for i,v in enumerate(values) if v != 0]
    res = [0]*size
    moves = []
    score_gain = 0
    i = 0; dst = 0
    while i < len(compact):
        src_i, v = compact[i]
        if i+1 < len(compact) and compact[i+1][1] == v:
            merged_val = v*2
            res[dst] = merged_val
            score_gain += merged_val
            moves.append((src_i, dst, True, merged_val))
            src_i2, _ = compact[i+1]
            moves.append((src_i2, dst, True, merged_val))
            i += 2
        else:
            res[dst] = v
            moves.append((src_i, dst, False, v))
            i += 1
        dst += 1
    return res, moves, score_gain

def lines_indices(n, direction):
    if direction == "left":
        for r in range(n): yield [(r,c) for c in range(n)]
    elif direction == "right":
        for r in range(n): yield [(r,c) for c in reversed(range(n))]
    elif direction == "up":
        for c in range(n): yield [(r,c) for r in range(n)]
    elif direction == "down":
        for c in range(n): yield [(r,c) for r in reversed(range(n))]

def move_board(b, direction):
    n = len(b)
    newb = [row[:] for row in b]
    total_gain = 0; animations = []; pop_cells = set(); changed = False
    if direction not in ("left","right","up","down"): return False, b, [], set(), 0
    for line in lines_indices(n, direction):
        vals = [b[r][c] for (r,c) in line]
        if all(v==0 for v in vals): continue
        compressed, moves, gain = slide_line(vals)
        total_gain += gain
        for idx,(r,c) in enumerate(line): newb[r][c] = compressed[idx]
        if compressed != vals: changed = True
        for src_i, dst_i, merged, v in moves:
            fr = line[src_i]; to = line[dst_i]
            if fr != to:
                animations.append({"from":fr,"to":to,"value": b[fr[0]][fr[1]], "merged_to":merged})
            if merged: pop_cells.add(to)
    return changed, newb, animations, pop_cells, total_gain

def has_moves(b):
    n = len(b)
    for r in range(n):
        for c in range(n):
            if b[r][c]==0: return True
            if c+1<n and b[r][c]==b[r][c+1]: return True
            if r+1<n and b[r][c]==b[r+1][c]: return True
    return False

def won(b):
    n = len(b)
    return any(b[r][c] >= 2048 for r in range(n) for c in range(n))

# --------------------------- Drawing ---------------------------
def round_rect(surf, rect, color, radius=12):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_label_box(surf, rect, title, value):
    round_rect(surf, rect, theme_color("SCORE_BG"), 10)
    t = font_small.render(title, True, tuple(theme_color("TEXT")))
    v = font_ui.render(str(value), True, (255,255,255) if PREFS["theme"]=="dark" else (20,20,20))
    surf.blit(t, (rect.x + (rect.w - t.get_width())//2, rect.y + 6))
    surf.blit(v, (rect.x + (rect.w - v.get_width())//2, rect.y + 26))

def draw_board_bg(board_rect, grid):
    round_rect(screen, board_rect, theme_color("BOARD"), 16)
    n = grid
    cell_size = (board_rect.w - (n+1)*TILE_MARGIN)//n
    for r in range(n):
        for c in range(n):
            round_rect(screen, cell_rect(board_rect, cell_size, r, c), theme_color("EMPTY"), 8)

def draw_tile_value(v, rect, scale=1.0):
    bg, fg = color_for(v)
    if PREFS["theme"]=="light" and v==0:
        bg = theme_color("EMPTY")
    if scale != 1.0:
        cx, cy = rect.center
        w = int(rect.w * scale); h = int(rect.h * scale)
        rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
    round_rect(screen, rect, bg, 8)
    s = str(v)
    f = font_tileL if len(s)<=2 else (font_tileM if len(s)==3 else font_tileS)
    img = f.render(s, True, fg)
    screen.blit(img, (rect.x + (rect.w - img.get_width())//2,
                      rect.y + (rect.h - img.get_height())//2))

def draw_tiles(board, board_rect, cell_size, anim_overrides=None, pop_cells=set(), pop_phase=0.0):
    n = len(board)
    for r in range(n):
        for c in range(n):
            v = board[r][c]
            if v==0: continue
            rect = cell_rect(board_rect, cell_size, r, c)
            scale = 1.0
            if (r,c) in pop_cells and pop_phase>0:
                amp = 0.12
                scale = 1 + amp * (1 - abs(2*pop_phase - 1))
            draw_tile_value(v, rect, scale)
    if anim_overrides:
        for (r,c),(px,py,v) in anim_overrides.items():
            rect = pygame.Rect(px, py, cell_size, cell_size)
            draw_tile_value(v, rect, 1.0)

# --------------------------- Menu ---------------------------
def draw_menu(selected_idx):
    screen.fill(theme_color("BG"))
    title = font_big.render("2048", True, theme_color("TEXT"))
    sub = font_small.render("Choisis la taille de grille • C pour thème clair/sombre", True, theme_color("SUB"))
    screen.blit(title, (BOARD_MARGIN, 32))
    screen.blit(sub,   (BOARD_MARGIN, 32 + title.get_height() + 6))

    # Buttons 4x4, 5x5, 6x6
    labels = ["4 × 4", "5 × 5", "6 × 6"]
    btns = []
    w = 130; h = 64; gap = 18
    base_x = BOARD_MARGIN
    y = 120
    for i,lab in enumerate(labels):
        rect = pygame.Rect(base_x + i*(w+gap), y, w, h)
        btns.append(rect)
        color = theme_color("menu_btn_active") if i==selected_idx else theme_color("menu_btn")
        round_rect(screen, rect, color, 14)
        t = font_ui.render(lab, True, theme_color("TEXT"))
        screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))
    pygame.display.flip()
    return btns

def menu_loop():
    idx = 0
    clock = pygame.time.Clock()
    while True:
        btns = draw_menu(idx)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_q): idx = (idx-1)%3
                if e.key in (pygame.K_RIGHT, pygame.K_d): idx = (idx+1)%3
                if e.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z, pygame.K_s):
                    return [4,5,6][idx]
                if e.key == pygame.K_4: return 4
                if e.key == pygame.K_5: return 5
                if e.key == pygame.K_6: return 6
                if e.key == pygame.K_c:
                    PREFS["theme"] = "light" if PREFS["theme"]=="dark" else "dark"
                    save_prefs(PREFS)
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit(0)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
                pos = e.pos
                for i,rect in enumerate(btns):
                    if rect.collidepoint(pos): return [4,5,6][i]
        clock.tick(60)

# --------------------------- Game Object ---------------------------
class Game:
    def __init__(self, grid):
        self.grid = grid
        self.best = PREFS["best"].get(str(grid), 0)
        self.reset()

    def reset(self):
        self.cell, self.board_rect, window_h = compute_layout(self.grid)
        pygame.display.set_mode((WIN_W, window_h), pygame.RESIZABLE)
        self.board = empty_board(self.grid)
        self.score = 0
        add_random_tile(self.board); add_random_tile(self.board)
        self.animating = False
        self.anim_start = 0
        self.anim_list = []
        self.post_board = None
        self.pre_board = None          # <--- ajouté
        self.pop_cells = set()
        self.pop_start = 0
        self.state = "play"


    def input_dir(self, key):
        if key in (pygame.K_LEFT, pygame.K_q): return "left"
        if key in (pygame.K_RIGHT, pygame.K_d): return "right"
        if key in (pygame.K_UP, pygame.K_z): return "up"
        if key in (pygame.K_DOWN, pygame.K_s): return "down"
        return None

    def handle_move(self, direction):
        if self.animating or self.state != "play":
            return
        self.pre_board = [row[:] for row in self.board]   # <--- mémorise l'ancien plateau
        changed, newb, anims, pops, gain = move_board(self.board, direction)
        if not changed:
            self.pre_board = None
            return
        self.score += gain
        self.animating = True
        self.anim_start = pygame.time.get_ticks()
        self.anim_list = anims
        self.post_board = newb
        self.pop_cells = pops
        self.pop_start = 0


    def update(self):
        now = pygame.time.get_ticks()
        if self.animating:
            t = (now - self.anim_start) / ANIM_TIME
            if t >= 1.0:
                self.board = self.post_board
                add_random_tile(self.board)
                self.animating = False
                self.anim_list.clear()
                self.post_board = None
                self.pre_board = None          # <--- libère l'ancien plateau
                if self.pop_cells: self.pop_start = pygame.time.get_ticks()
                if self.score > self.best:
                    self.best = self.score
                    PREFS["best"][str(self.grid)] = int(self.best)
                    save_prefs(PREFS)
                if won(self.board): self.state = "won"
                elif not has_moves(self.board): self.state = "over"

    def draw(self):
        screen.fill(theme_color("BG"))
        title = font_big.render("2048", True, theme_color("TEXT"))
        sub = font_small.render("ZQSD / Flèches • R rejouer • C thème", True, theme_color("SUB"))
        screen.blit(title, (BOARD_MARGIN, 24))
        screen.blit(sub,   (BOARD_MARGIN, 24 + title.get_height() + 6))
        box_w, box_h = 120, 56
        draw_label_box(screen, pygame.Rect(WIN_W - BOARD_MARGIN - box_w*2 - 10, 24, box_w, box_h), "SCORE", self.score)
        draw_label_box(screen, pygame.Rect(WIN_W - BOARD_MARGIN - box_w, 24, box_w, box_h), "BEST", self.best)

        draw_board_bg(self.board_rect, self.grid)

        overrides = {}
        base_board = self.board  # par défaut (pas d’anim)

        if self.animating and self.anim_list:
            # 1) Base = plateau AVANT le coup
            base_board = [row[:] for row in (self.pre_board or self.board)]
            # 2) Masquer les tuiles qui bougent sur le plateau de base
            for a in self.anim_list:
                r, c = a["from"]
                base_board[r][c] = 0

            # 3) Positions interpolées des tuiles animées (avec leur valeur d'origine)
            t = (pygame.time.get_ticks() - self.anim_start) / ANIM_TIME
            t = max(0.0, min(1.0, t))
            for a in self.anim_list:
                (r1, c1) = a["from"]; (r2, c2) = a["to"]
                x1, y1 = cell_rect(self.board_rect, self.cell, r1, c1).topleft
                x2, y2 = cell_rect(self.board_rect, self.cell, r2, c2).topleft
                px = x1 + (x2 - x1) * t
                py = y1 + (y2 - y1) * t
                overrides[(r1, c1)] = (px, py, a["value"])  # valeur d'origine, pas la valeur fusionnée

        # 4) Pop de fusion (uniquement après l’anim)
        pop_phase = 0.0
        if self.pop_cells and not self.animating and self.pop_start:
            dt = (pygame.time.get_ticks() - self.pop_start)
            pop_phase = max(0.0, min(1.0, dt / POP_TIME))
            if pop_phase >= 1.0:
                self.pop_cells = set()
                self.pop_start = 0

        # Dessin final : plateau de base (ancien si anim) + tuiles animées par-dessus
        draw_tiles(base_board, self.board_rect, self.cell,
                overrides if self.animating else None,
                self.pop_cells, pop_phase)

        # Overlays victoire/fin identiques...
        if self.state in ("won","over"):
            overlay = pygame.Surface((self.board_rect.w, self.board_rect.h), pygame.SRCALPHA)
            overlay.fill(theme_color("overlay"))
            screen.blit(overlay, self.board_rect.topleft)
            msg = "Bravo ! 2048 atteint ! Gagné !" if self.state=="won" else "Plus de coups possibles... Perdu !"
            txt = font_ui.render(msg, True, (255,255,255) if PREFS["theme"]=="dark" else (10,10,10))
            txt2 = font_small.render("Appuie sur R pour rejouer • Échap pour quitter", True, theme_color("TEXT"))
            screen.blit(txt, (self.board_rect.centerx - txt.get_width()//2, self.board_rect.y + self.board_rect.h//2 - 24))
            screen.blit(txt2,(self.board_rect.centerx - txt2.get_width()//2, self.board_rect.y + self.board_rect.h//2 + 6))

        pygame.display.flip()


# --------------------------- Main ---------------------------
def main():
    clock = pygame.time.Clock()

    while True:
        # --- MENU DE DÉMARRAGE ---
        grid = menu_loop()
        game = Game(grid)

        # --- BOUCLE DE JEU ---
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit(0)
                    if e.key == pygame.K_r:
                        # 🔁 retour au menu pour choisir la grille
                        running = False
                        break
                    if e.key == pygame.K_c:
                        PREFS["theme"] = "light" if PREFS["theme"]=="dark" else "dark"
                        save_prefs(PREFS)
                    dirn = game.input_dir(e.key)
                    if dirn:
                        game.handle_move(dirn)

            if not running:
                break  # sort du while pour revenir au menu

            game.update()
            game.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    main()
