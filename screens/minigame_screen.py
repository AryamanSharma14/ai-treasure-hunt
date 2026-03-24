"""Mini Game Screen — launches Pacman AI in the browser, shows instructions."""

import os
import webbrowser
import pygame
from game.constants import WINDOW_W, WINDOW_H, COLORS, STATE_TITLE


class MiniGameScreen:

    def __init__(self, surface, state_dict):
        self.surface    = surface
        self.state      = state_dict
        self.tick       = 0
        self._launched  = False
        self._init_fonts()
        self._launch_browser()

    def _init_fonts(self):
        def _f(size, bold=False):
            for fam in ('segoe ui', 'arial', 'helvetica', None):
                try:
                    return pygame.font.SysFont(fam, size, bold=bold)
                except Exception:
                    pass
            return pygame.font.Font(None, size)

        self.font_title = _f(42, bold=True)
        self.font_sub   = _f(20)
        self.font_body  = _f(16)
        self.font_hint  = _f(14)

    def _launch_browser(self):
        """Open web/index.html in the default browser."""
        web_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'index.html')
        web_path = os.path.abspath(web_path)
        if os.path.exists(web_path):
            webbrowser.open('file:///' + web_path.replace('\\', '/'))
            self._launched = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q, pygame.K_RETURN,
                             pygame.K_SPACE, pygame.K_KP_ENTER):
                return STATE_TITLE
        if event.type == pygame.MOUSEBUTTONDOWN:
            return STATE_TITLE
        return None

    def update(self, dt):
        self.tick += 1

    def draw(self):
        surf = self.surface
        surf.fill(COLORS['bg'])

        cx = WINDOW_W // 2
        cy = WINDOW_H // 2

        # Title
        t = self.font_title.render('Pacman Mini Game', True, (255, 224, 64))
        surf.blit(t, t.get_rect(center=(cx, cy - 140)))

        # Status
        status = 'Launched in your browser!' if self._launched else 'web/index.html not found.'
        color  = (80, 227, 164) if self._launched else (255, 107, 107)
        s = self.font_sub.render(status, True, color)
        surf.blit(s, s.get_rect(center=(cx, cy - 80)))

        # Info lines
        lines = [
            '4 ghosts each using a different search algorithm:',
            '  BFS (blue)  —  shortest path, level-by-level',
            '  DFS (amber) —  winding depth-first paths',
            '  A*  (green) —  optimal, f = g + h',
            '  Greedy (red)—  heuristic only, aggressive',
            '',
            '[A] AI autopilot   [V] Ghost paths   [M] Cycle maze',
        ]
        y = cy - 30
        for line in lines:
            col = COLORS['text_secondary'] if line.startswith('  ') else COLORS['text_primary']
            if not line:
                y += 10
                continue
            ls = self.font_body.render(line, True, col)
            surf.blit(ls, ls.get_rect(center=(cx, y)))
            y += 26

        # Hint
        blink = int((pygame.time.get_ticks() / 800) % 2)
        if blink:
            h = self.font_hint.render('[Esc / Enter]  Back to AI Treasure Hunt', True, COLORS['text_dim'])
            surf.blit(h, h.get_rect(center=(cx, WINDOW_H - 40)))
