#!/usr/bin/env python3
import sys, random
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QFont, QBrush,
    QPixmap, QGuiApplication
)

COLORS = [
    "#ff3355", "#ff8800", "#ffe600",
    "#00ff88", "#00ccff", "#aa44ff",
    "#ff44cc", "#00ffcc",
]

GLOW_PAD = 60   # extra space around logo for glow layers


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 1.0
        self.decay = random.uniform(0.018, 0.038)
        self.size  = random.uniform(2, 6)
        self.color = QColor(color)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15
        self.life -= self.decay

    def draw(self, p):
        if self.life <= 0:
            return
        c = QColor(self.color)
        c.setAlphaF(self.life * self.life)
        p.setBrush(QBrush(c))
        p.setPen(Qt.NoPen)
        r = self.size * self.life
        p.drawEllipse(QPointF(self.x, self.y), r, r)


class DVDScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DVD")
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint
        )
        self.setCursor(Qt.BlankCursor)
        self.setStyleSheet("background: black;")
        self.LW, self.LH = 260, 110
        scr = QGuiApplication.primaryScreen().geometry()
        self.SW, self.SH = scr.width(), scr.height()
        self.setGeometry(scr)
        self.show()
        self.raise_()
        self.activateWindow()
        self.grabKeyboard()
        self.grabMouse()

        self.x  = random.uniform(80, self.SW - self.LW - 80)
        self.y  = random.uniform(80, self.SH - self.LH - 80)
        self.dx = 2.5
        self.dy = 1.9

        self.color_idx = 0
        self.color     = QColor(COLORS[0])
        self.particles = []
        self.trail     = []
        self.TRAIL_LEN = 10
        self.bounces   = 0
        self.corners   = 0
        self.corner_t  = 0.0

        # pre-render logo pixmap (rebuilt on color change)
        self._logo_pm = None
        self._rebuild_logo()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        self.timer.start(16)

    # ── logo pixmap ────────────────────────────────────────────────────────
    def _rebuild_logo(self):
        pm = QPixmap(self.LW + GLOW_PAD*2, self.LH + GLOW_PAD*2)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        self._paint_logo(p, GLOW_PAD, GLOW_PAD)
        p.end()
        self._logo_pm = pm

    def _paint_logo(self, p, ox, oy):
        """Raw logo draw at offset (ox, oy) using current self.color."""
        # DVD text
        font = QFont("Arial Black", 72, QFont.Black)
        p.setFont(font)
        p.setPen(self.color)
        p.drawText(ox + 4, oy + 80, "DVD")
        # underline bar
        p.setBrush(QBrush(self.color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(ox + 4, oy + 86, 160, 8, 4, 4)
        # VIDEO label
        p.setFont(QFont("Arial", 13, QFont.Bold))
        p.setPen(self.color)
        p.drawText(ox + 170, oy + 96, "VIDEO")
        # disc ellipse
        p.setPen(QPen(self.color, 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(ox + 95, oy + 4, 80, 22))

    # ── step ────────────────────────────────────────────────────────────────
    def step(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.TRAIL_LEN:
            self.trail.pop(0)

        self.x += self.dx
        self.y += self.dy

        hit_x = hit_y = False
        if self.x <= 0:
            self.x = 0; self.dx = abs(self.dx); hit_x = True
        if self.x + self.LW >= self.SW:
            self.x = self.SW - self.LW; self.dx = -abs(self.dx); hit_x = True
        if self.y <= 0:
            self.y = 0; self.dy = abs(self.dy); hit_y = True
        if self.y + self.LH >= self.SH:
            self.y = self.SH - self.LH; self.dy = -abs(self.dy); hit_y = True

        if hit_x or hit_y:
            self.bounces += 1
            self._next_color()
            bx, by = self.x + self.LW/2, self.y + self.LH/2
            for _ in range(28):
                self.particles.append(Particle(bx, by, COLORS[self.color_idx]))
            if hit_x and hit_y:
                self.corners += 1
                self.corner_t = 1.0

        if self.corner_t > 0:
            self.corner_t = max(0.0, self.corner_t - 0.016)

        for pt in self.particles:
            pt.update()
        self.particles = [pt for pt in self.particles if pt.life > 0]
        self.update()

    def _next_color(self):
        old = self.color_idx
        while self.color_idx == old:
            self.color_idx = random.randrange(len(COLORS))
        self.color = QColor(COLORS[self.color_idx])
        self._rebuild_logo()

    # ── paint ────────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.fillRect(self.rect(), QColor(0, 0, 0))

        pm = self._logo_pm
        pw, ph = pm.width(), pm.height()

        # ── trail (faint logo ghosts)
        for i, (tx, ty) in enumerate(self.trail):
            alpha = (i / self.TRAIL_LEN) * 0.12
            p.setOpacity(alpha)
            p.drawPixmap(int(tx - GLOW_PAD), int(ty - GLOW_PAD), pm)
        p.setOpacity(1.0)

        # ── glow: draw logo pixmap scaled up with low opacity (shape-accurate bloom)
        cx = self.x - GLOW_PAD
        cy = self.y - GLOW_PAD
        for scale, alpha in [(1.20, 0.04), (1.12, 0.08), (1.06, 0.13), (1.03, 0.20)]:
            sw = int(pw * scale)
            sh = int(ph * scale)
            ox = int(cx - (sw - pw) / 2)
            oy = int(cy - (sh - ph) / 2)
            p.setOpacity(alpha)
            p.drawPixmap(ox, oy, pm.scaled(sw, sh, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        p.setOpacity(1.0)

        # ── logo sharp
        p.drawPixmap(int(cx), int(cy), pm)

        # ── particles
        for pt in self.particles:
            pt.draw(p)

        # ── corner flash
        if self.corner_t > 0:
            alpha = min(self.corner_t * 2.5, 1.0)
            scale = 1.0 + (1.0 - self.corner_t) * 0.4
            flash_c = QColor(self.color)
            flash_c.setAlphaF(alpha)
            font = QFont("Arial Black", int(72 * scale), QFont.Black)
            p.setFont(font)
            # glow passes
            for goff, ga in [(8, 0.08), (5, 0.15), (2, 0.25)]:
                gc = QColor(self.color)
                gc.setAlphaF(alpha * ga * 4)
                p.setPen(gc)
                p.drawText(QRectF(goff, goff, self.SW, self.SH), Qt.AlignCenter, "CORNER!")
            p.setPen(flash_c)
            p.drawText(QRectF(0, 0, self.SW, self.SH), Qt.AlignCenter, "CORNER!")

        # ── counters
        p.setOpacity(0.2)
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Monospace", 10))
        p.drawText(QRectF(0, self.SH - 30, self.SW - 20, 20),
                   Qt.AlignRight, f"BOUNCES: {self.bounces}   CORNERS: {self.corners}")
        p.end()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_D:
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DVDScreen()
    sys.exit(app.exec_())
