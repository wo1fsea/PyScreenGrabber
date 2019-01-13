# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
Author:
    Huang Quanyong (wo1fSea)
    quanyongh@foxmail.com
Date:
    2019/1/9
Description:
    screen_grabber.py
----------------------------------------------------------------------------"""

import sys

from PyQt5.QtCore import pyqtSignal, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QRubberBand


class ScreenGrabber(QLabel):
    grabbed = pyqtSignal(QPixmap)

    def __init__(self, parent, limit_rect=None):
        self._parent = parent
        super(ScreenGrabber, self).__init__(None)
        self._rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self._rubber_band.setGeometry(0, 0, 0, 0)
        self._rubber_band.show()

        self._origin = QPoint()
        self._changing_rubber_band = False
        self.setCursor(Qt.CrossCursor)

        screens = QApplication.screens()
        if len(screens) != 1:
            print("only screens[0] can be grabbed.")

        screen = screens[0]
        screen_size = screen.size()
        screen_width, screen_height = screen_size.width(), screen_size.height()
        self._limit_rect = QRect(0, 0, screen_width, screen_height) if not limit_rect else limit_rect

        screen_shot = screen.grabWindow(0, 0, 0, screen_width, screen_height)
        screen_shot = screen_shot.scaled(screen_width, screen_height)

        pixmap = QPixmap(screen_shot)

        # make mask
        mask_pixmap = QPixmap(screen_shot.width(), screen_shot.height())
        mask_color = QColor(0, 0, 0, 64)
        mask_pixmap.fill(mask_color)
        mask_painter = QPainter()
        mask_painter.begin(mask_pixmap)
        mask_painter.fillRect(
            QRect(QPoint(0, 0), QPoint(self._limit_rect.left() - 1, self._limit_rect.bottom() - 1)),
            mask_color
        )
        mask_painter.fillRect(
            QRect(QPoint(self._limit_rect.left(), 0), QPoint(screen_width - 1, self._limit_rect.top() - 1)),
            mask_color
        )
        mask_painter.fillRect(
            QRect(QPoint(0, self._limit_rect.bottom()), QPoint(self._limit_rect.right() - 1, screen_height - 1)),
            mask_color
        )
        mask_painter.fillRect(
            QRect(QPoint(self._limit_rect.right(), self._limit_rect.top()),
                  QPoint(screen_width - 1, screen_height - 1)),
            mask_color
        )
        mask_painter.end()

        painter = QPainter()
        painter.begin(pixmap)
        painter.drawPixmap(0, 0, mask_pixmap)
        painter.end()

        self._pixmap = screen_shot
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        self.setParent(self._parent)
        rect = self._rubber_band.geometry()
        result_pixmap = self._pixmap.copy(rect)
        self.grabbed.emit(result_pixmap)

    def mousePressEvent(self, event):
        super(ScreenGrabber, self).mousePressEvent(event)
        if event.button() != Qt.LeftButton:
            return

        if not self._rubber_band.geometry().isEmpty():
            return

        pos = event.pos()
        pos = QPoint(
            min(self._limit_rect.right(), max(self._limit_rect.left(), pos.x())),
            min(self._limit_rect.bottom(), max(self._limit_rect.top(), pos.y()))
        )
        self._origin = QPoint(pos)
        self._rubber_band.setGeometry(QRect(self._origin, QSize()))
        self._changing_rubber_band = True

    def mouseMoveEvent(self, event):
        super(ScreenGrabber, self).mouseMoveEvent(event)
        pos = event.pos()
        pos = QPoint(
            min(self._limit_rect.right(), max(self._limit_rect.left(), pos.x())),
            min(self._limit_rect.bottom(), max(self._limit_rect.top(), pos.y()))
        )
        if self._changing_rubber_band:
            self._rubber_band.setGeometry(QRect(self._origin, pos).normalized())

    def mouseReleaseEvent(self, event):
        super(ScreenGrabber, self).mouseReleaseEvent(event)
        self._changing_rubber_band = False


if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.setGeometry(0, 0, 0, 0)

            self.screen_grabber = ScreenGrabber(self, QRect(100, 100, 500, 500))
            self.screen_grabber.grabbed.connect(self.save)

        def save(self, pixmap):
            import time
            local_time = time.localtime()
            string_time = time.strftime("%Y_%m_%d_%H_%M_%S", local_time)
            pixmap.save("%s.png" % string_time)
            self.close()


    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
