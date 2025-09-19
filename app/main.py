import sys
from itertools import cycle
from collections import deque
from PySide6 import QtCore, QtWidgets, QtGui
import uuid
from db import store_link, store_node, restore_all_nodes

from functools import wraps


def mark_changed(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        self.touched.emit(self)
        return result
    return wrapper


class RectWithText(QtCore.QObject, QtWidgets.QGraphicsRectItem):
    touched = QtCore.Signal(object)

    def __init__(self, text: str, width: int = 120, height: int = 50):
        QtCore.QObject.__init__(self)
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, width, height)

        self.id = uuid.uuid4()
        self.edges: list["Edge"] = []

        self.colors = [QtGui.QColor("orange"), QtGui.QColor("yellow")]
        self.colors_gen = cycle(self.colors)
        self.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black))
        self.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.yellow))
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.label = QtWidgets.QGraphicsTextItem(text, self)
        self.label.setDefaultTextColor(QtGui.QColor("black"))
        self.label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextEditable)
        self.update_text_position()

        self._dragged = False

    def update_text_position(self):
        rect_bounds = self.rect()
        text_bounds = self.label.boundingRect()
        self.label.setPos(
            rect_bounds.center().x() - text_bounds.width() / 2,
            rect_bounds.center().y() - text_bounds.height() / 2,
        )


    @mark_changed
    def mousePressEvent(self, event):
        self._dragged = False
        super().mousePressEvent(event)

    @mark_changed
    def mouseMoveEvent(self, event):
        self._dragged = True
        super().mouseMoveEvent(event)
        for edge in self.edges:
            edge.update_position()

    @mark_changed
    def mouseReleaseEvent(self, event):
        if not self._dragged:
            self.setBrush(next(self.colors_gen))
        super().mouseReleaseEvent(event)

    @mark_changed
    def focusOutEvent(self, event):
        super().focusOutEvent(event)


class Edge(QtWidgets.QGraphicsLineItem):
    def __init__(self, board,source: RectWithText, target: RectWithText):
        super().__init__()
        self.source = source
        self.target = target
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 2)
        self.setPen(pen)
        self.update_position()

        source.edges.append(self)
        target.edges.append(self)

    def update_position(self):
        p1 = self.source.sceneBoundingRect().center()
        p2 = self.target.sceneBoundingRect().center()
        self.setLine(QtCore.QLineF(p1, p2))


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene) 

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        self.buttons = [
            self.add_button('Add node', self.add_node, layout),
        self.add_button('Link last 2 nodes', self.link_last_two, layout),
        self.add_button('Remove link last 2 nodes', self.remove_last_two_link, layout),
        ]

        self.nodes: list[RectWithText] = []
        self.last_two = deque(maxlen=2)
        restore_all_nodes(self)

    def add_button(self, name, func, layout):
        b = QtWidgets.QPushButton(name)
        b.clicked.connect(func)
        layout.addWidget(b)
        return b


    def add_node(self, x=100, y=100, text="node", color="green") -> RectWithText:
        item = RectWithText(text)
        item.touched.connect(self._mark_node)
        self.scene.addItem(item)
        item.setPos(x,y)
        item.setBrush(QtGui.QColor(color))
        self.nodes.append(item)
        self._mark_node(item)
        return item

    def _mark_node(self, node: RectWithText):
        if node in self.last_two:
            self.last_two.remove(node)
        self.last_two.append(node)

    def link_2_nodes(self, node1, node2):
        edge = Edge(self, node1, node2)
        self.scene.addItem(edge)

    def link_last_two(self) -> None:
        if len(self.last_two) == 2:
            self.link_2_nodes(self.last_two[0], self.last_two[1])

    def remove_last_two_link(self) -> None:
        if len(self.last_two) == 2:
            self.get_and_remove_link_by_two_nodes(self.last_two[0], self.last_two[1])

    def get_and_remove_link_by_two_nodes(self, source: RectWithText, target: RectWithText):
        for edge in list(source.edges):
            if (edge.source is source and edge.target is target) or (
                edge.source is target and edge.target is source
            ):
                self.scene.removeItem(edge)
                if edge in source.edges:
                    source.edges.remove(edge)
                if edge in target.edges:
                    target.edges.remove(edge)
                return edge
        return None


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
