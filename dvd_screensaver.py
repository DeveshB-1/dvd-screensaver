#!/usr/bin/env python3
import sys, random
from math import gcd
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPixmap, QGuiApplication

COLORS = [
    "#ff0000", "#00ff00", "#0000ff",
    "#ffff00", "#ff00ff", "#00ffff",
    "#ff8800", "#ffffff",
]


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

        self.LW, self.LH = 220, 90
        scr = QGuiApplication.primaryScreen().geometry()
        self.SW, self.SH = scr.width(), scr.height()
        self.setGeometry(scr)
        self.show()
        self.raise_()
        self.activateWindow()
        self.grabKeyboard()
        self.grabMouse()

        self.x = random.uniform(0, self.SW - self.LW)
        self.y = random.uniform(0, self.SH - self.LH)

        # compute dx:dy = effective_w:effective_h so path always hits corners
        ew = self.SW - self.LW
        eh = self.SH - self.LH
        g  = gcd(ew, eh)
        speed = 3.0
        self.dx = (ew // g) * speed / (ew // g)   # = speed
        self.dy = (eh // g) * speed / (ew // g)
        if random.random() < 0.5: self.dx *= -1
        if random.random() < 0.5: self.dy *= -1

        self.color_idx = 0
        self.color     = QColor(COLORS[0])
        self.bounces   = 0
        self.corners   = 0
        self.corner_t  = 0.0

        self._logo_pm = None
        self._rebuild_logo()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.step)
        self.timer.start(16)

    def _rebuild_logo(self):
        pm = QPixmap(self.LW, self.LH)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        # DVD text
        p.setFont(QFont("Arial Black", 58, QFont.Black))
        p.setPen(self.color)
        p.drawText(0, 68, "DVD")
        # underline
        p.setBrush(QBrush(self.color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 74, 130, 6, 3, 3)
        # VIDEO
        p.setFont(QFont("Arial", 11, QFont.Bold))
        p.setPen(self.color)
        p.drawText(138, 82, "VIDEO")
        # disc ellipse
        p.setPen(QPen(self.color, 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(78, 2, 64, 18))
        p.end()
        self._logo_pm = pm

    def step(self):
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
            old = self.color_idx
            while self.color_idx == old:
                self.color_idx = random.randrange(len(COLORS))
            self.color = QColor(COLORS[self.color_idx])
            self._rebuild_logo()
            if hit_x and hit_y:
                self.corners += 1
                self.corner_t = 1.5

        if self.corner_t > 0:
            self.corner_t = max(0.0, self.corner_t - 0.02)

        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0))
        p.drawPixmap(int(self.x), int(self.y), self._logo_pm)

        if self.corner_t > 0:
            alpha = min(self.corner_t, 1.0)
            c = QColor(self.color)
            c.setAlphaF(alpha)
            p.setPen(c)
            p.setFont(QFont("Arial Black", 64, QFont.Black))
            p.drawText(QRectF(0, 0, self.SW, self.SH), Qt.AlignCenter, "CORNER!")

        p.setOpacity(0.25)
        p.setPen(QColor(255, 255, 255))
        p.setFont(QFont("Monospace", 10))
        p.drawText(QRectF(0, self.SH - 28, self.SW - 16, 20),
                   Qt.AlignRight, f"BOUNCES: {self.bounces}   CORNERS: {self.corners}")
        p.end()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_D:
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DVDScreen()
    sys.exit(app.exec_())
