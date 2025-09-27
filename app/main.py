import sys
from itertools import cycle
from collections import defaultdict, deque
from typing import Callable, Concatenate, ParamSpec, TypeVar
from PySide6 import QtCore, QtWidgets, QtGui
import uuid
from db import load_all, save_all

from functools import wraps


P = ParamSpec("P")
R = TypeVar("R")

def mark_changed(method: Callable[Concatenate["Node", P], R]) -> Callable[Concatenate["Node", P], R]:
    @wraps(method)
    def wrapper(self: "Node", *args: P.args, **kwargs: P.kwargs) -> R:
        result = method(self, *args, **kwargs)
        self.touched.emit(self)
        return result
    return wrapper


class Node(QtCore.QObject, QtWidgets.QGraphicsRectItem):
    touched = QtCore.Signal(object)

    def __init__(self, text: str, id: str | None = None, width: int = 120, height: int = 50):
        QtCore.QObject.__init__(self)
        QtWidgets.QGraphicsRectItem.__init__(self, 0, 0, width, height)
        self.id: str = id or str(uuid.uuid4())

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

    @mark_changed
    def mouseReleaseEvent(self, event):
        if not self._dragged:
            self.setBrush(next(self.colors_gen))
        super().mouseReleaseEvent(event)

    @mark_changed
    def focusOutEvent(self, event):
        self.label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextEditable)
        super().focusOutEvent(event)


class Link(QtWidgets.QGraphicsLineItem):
    def __init__(self, source: Node, target: Node, id=None):
        super().__init__()
        self.id: str = id or str(uuid.uuid4())
        self.source: Node = source
        self.target: Node = target
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 2)
        self.setPen(pen)
        self.update()

    def paint(self, painter, option, widget=None):
        p1 = self.source.sceneBoundingRect().center()
        p2 = self.target.sceneBoundingRect().center()
        self.setLine(QtCore.QLineF(p1, p2))

        super().paint(painter, option, widget)


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene) 
        self.view.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        self.buttons = [
            self.add_button('Add node', self.add_node, layout),
            self.add_button("Link", self.link_selected_nodes, layout),
            self.add_button("Save", self.save, layout)
        ]
        self.nodes: list[Node] = []

        self.pair_nodes_link: dict[tuple[str, str], Link] = {}
        self.node_links: dict[str, list[Link]] = defaultdict(list)

        self.selected: deque[Node] = deque(maxlen=2)
        self._restore()

    def _restore(self):
        nodes, links = load_all()
        self.nodes = nodes
        for node in nodes:
            node.touched.connect(self._on_node_touched)

            self.scene.addItem(node)
        for link in links:
            target, source = link.target, link.source
            if source.id > target.id:
                source, target = target, source
            key = (target.id, source.id)

            self.pair_nodes_link[key] = link
            self.node_links[target.id].append(link)
            self.node_links[source.id].append(link)

            self.scene.addItem(link)

    def save(self):
        save_all(self.nodes, list(self.pair_nodes_link.values()))

    def add_button(self, name, func, layout):
        b = QtWidgets.QPushButton(name)
        b.clicked.connect(func)
        layout.addWidget(b)
        return b

    def add_node(self, x=100, y=100, text="node", color="green") -> Node:
        item = Node(text)
        item.touched.connect(self._on_node_touched)
        self.scene.addItem(item)
        item.setPos(x, y)
        item.setBrush(QtGui.QColor(color))
        self.nodes.append(item)
        self._select_node(item)
        return item

    def link_selected_nodes(self):
        if len(self.selected) < 2:
            return

        source, target = self.selected
        if source.id > target.id:
            source, target = target, source
        key = (target.id, source.id)

        if key in self.pair_nodes_link:
            link = self.pair_nodes_link.pop(key)
            self.node_links.get(source.id, []).remove(link)
            self.node_links.get(target.id, []).remove(link)
            self.scene.removeItem(link)
            del link
            return

        link = Link(source, target)
        self.scene.addItem(link)

        self.pair_nodes_link[key] = link
        self.node_links.setdefault(source.id, []).append(link)
        self.node_links.setdefault(target.id, []).append(link)

    def _on_node_touched(self, node: Node) -> None:
        """Update node + its links when touched"""
        self._select_node(node)
        for link in self.node_links.get(node.id, []):
            link.update()

    def _select_node(self, node: Node) -> None:
        node.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.red, 2))

        if node in self.selected:
            self.selected.remove(node)
        if self.selected.maxlen == len(self.selected):
            removed = self.selected.popleft()
            removed.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.black))

        self.selected.append(node)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    widget.showFullScreen()
    sys.exit(app.exec())
