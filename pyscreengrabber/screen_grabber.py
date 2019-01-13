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

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QRubberBand


class ScreenGrabber(QLabel):
	grabbed = pyqtSignal(QPixmap)

	def __init__(self, parent):
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

		pixmap = screen.grabWindow(0, 0, 0, screen_width, screen_height)
		pixmap0 = QPixmap(pixmap)
		pixmap1 = QPixmap(pixmap.width(), pixmap.height())
		pixmap1.fill((QColor(0, 0, 0, 128)))
		painter = QPainter()
		painter.begin(pixmap0)
		painter.drawPixmap(0, 0, pixmap1)
		painter.end()

		self._pixmap = pixmap
		self.setPixmap(pixmap0)
		self.setScaledContents(True)
		self.setAlignment(Qt.AlignCenter)
		self.resize(pixmap0.width(), pixmap0.height())
		self.setGeometry(0, 0, screen_width, screen_height)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.showFullScreen()

	def mouseDoubleClickEvent(self, event):
		if event.button() != Qt.LeftButton:
			return

		self.setParent(self._parent)
		rect = self._rubber_band.geometry()
		rect.setTop(rect.top() * self._pixmap.width() / self.width())
		rect.setLeft(rect.left() * self._pixmap.height() / self.height())
		rect.setBottom(rect.bottom() * self._pixmap.width() / self.width())
		rect.setRight(rect.right() * self._pixmap.height() / self.height())

		result_pixmap = self._pixmap.copy(rect)
		self.grabbed.emit(result_pixmap)

	def mousePressEvent(self, event):
		super(ScreenGrabber, self).mousePressEvent(event)
		if event.button() != Qt.LeftButton:
			return

		if not self._rubber_band.geometry().isEmpty():
			return

		self._origin = event.pos()
		self._rubber_band.setGeometry(QRect(self._origin, QSize()))
		self._changing_rubber_band = True

	def mouseMoveEvent(self, event):
		super(ScreenGrabber, self).mouseMoveEvent(event)
		if self._changing_rubber_band:
			self._rubber_band.setGeometry(QRect(self._origin, event.pos()).normalized())

	def mouseReleaseEvent(self, event):
		super(ScreenGrabber, self).mouseReleaseEvent(event)
		self._changing_rubber_band = False


if __name__ == '__main__':
	class MainWindow(QMainWindow):
		def __init__(self):
			super(MainWindow, self).__init__()
			self.setGeometry(0, 0, 0, 0)

			self.screen_grabber = ScreenGrabber(self)
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
