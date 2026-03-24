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


def mark_changed(
    method: Callable[Concatenate["Node", P], R],
) -> Callable[Concatenate["Node", P], R]:
    @wraps(method)
    def wrapper(self: "Node", *args: P.args, **kwargs: P.kwargs) -> R:
        result = method(self, *args, **kwargs)
        self.touched.emit(self)
        return result

    return wrapper


class Node(QtCore.QObject, QtWidgets.QGraphicsRectItem):
    touched = QtCore.Signal(object)

    def __init__(
        self, text: str, id: str | None = None, width: int = 120, height: int = 50
    ):
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

        self.setZValue(10)

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


def rect_edge_point(rect: QtCore.QRectF, line: QtCore.QLineF) -> QtCore.QPointF:
    edges = (
        QtCore.QLineF(rect.topLeft(), rect.topRight()),
        QtCore.QLineF(rect.topRight(), rect.bottomRight()),
        QtCore.QLineF(rect.bottomRight(), rect.bottomLeft()),
        QtCore.QLineF(rect.bottomLeft(), rect.topLeft()),
    )

    for edge in edges:
        intersection_type, point = line.intersects(edge)
        if intersection_type == QtCore.QLineF.IntersectionType.BoundedIntersection:
            return point

    return rect.center()


class Link(QtWidgets.QGraphicsLineItem):
    def __init__(self, source: Node, target: Node, id=None):
        super().__init__()
        self.id: str = id or str(uuid.uuid4())
        self.source: Node = source
        self.target: Node = target
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 2)
        self.setPen(pen)
        self.update()

        self.setZValue(0)

    def paint(self, painter, option, widget=None):
        src_rect = self.source.sceneBoundingRect()
        tgt_rect = self.target.sceneBoundingRect()

        src_center = src_rect.center()
        tgt_center = tgt_rect.center()

        center_line = QtCore.QLineF(src_center, tgt_center)

        p1 = rect_edge_point(src_rect, center_line)
        p2 = rect_edge_point(tgt_rect, QtCore.QLineF(tgt_center, src_center))

        self.setLine(QtCore.QLineF(p1, p2))
        super().paint(painter, option, widget)


class Region(QtWidgets.QGraphicsRectItem):
    def __init__(
        self, name: str = "Region", id=None, width: int = 300, height: int = 200
    ):
        super().__init__(0, 0, width, height)
        self.id: str = id or str(uuid.uuid4())
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setPen(
            QtGui.QPen(QtCore.Qt.GlobalColor.blue, 2, QtCore.Qt.PenStyle.DashLine)
        )
        self.setBrush(QtGui.QBrush(QtGui.QColor(200, 200, 255, 50)))

        self.setZValue(-1)

        self.label = QtWidgets.QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(QtGui.QColor("blue"))
        self.label.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextEditable)
        self.update_label_position()

        self.setAcceptHoverEvents(True)
        self._resizing = False
        self._resize_handle_size = 12
        self._min_size = QtCore.QSizeF(80, 60)

    def update_label_position(self):
        self.label.setPos(self.rect().x() + 5, self.rect().y() + 5)

    def mousePressEvent(self, event):
        if self.cursor().shape() == QtCore.Qt.CursorShape.SizeFDiagCursor:
            self._resizing = True
            self._resize_start_rect = self.rect()
            self._resize_start_pos = event.scenePos()
        else:
            self._resizing = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.scenePos() - self._resize_start_pos
            factor = 0.5
            new_width = max(
                self._min_size.width(),
                self._resize_start_rect.width() + delta.x() * factor,
            )
            new_height = max(
                self._min_size.height(),
                self._resize_start_rect.height() + delta.y() * factor,
            )
            self.setRect(0, 0, new_width, new_height)
            self.update_label_position()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resizing = False
        super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        rect = self.rect()
        if (
            abs(event.pos().x() - rect.width()) < self._resize_handle_size
            and abs(event.pos().y() - rect.height()) < self._resize_handle_size
        ):
            self.setCursor(QtCore.Qt.CursorShape.SizeFDiagCursor)
        else:
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)


class Scene(QtWidgets.QGraphicsScene):
    pass


class MainWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.scene = Scene()
        self.view = QtWidgets.QGraphicsView(self.scene)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        shortcut_z_out = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+-"), self)
        shortcut_z_out.activated.connect(self.zoom_out)
        shortcut_z_in = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+="), self)
        shortcut_z_in.activated.connect(self.zoom_in)

        self.buttons = [
            self.add_button("Add node", self.add_node, layout),
            self.add_button("Link", self.link_selected_nodes, layout),
            self.add_button("Save", self.save, layout),
            self.add_button("Add Region", self.add_region, layout),
        ]

        self.nodes: list[Node] = []
        self.regions: list[Region] = []

        self.pair_nodes_link: dict[tuple[str, str], Link] = {}
        self.node_links: dict[str, list[Link]] = defaultdict(list)

        self.selected: deque[Node] = deque(maxlen=2)
        self._restore()

    def mouseDoubleClickEvent(self, e):
        self.add_node(e.screenPos().x(), e.screenPos().y())

    def _restore(self):
        nodes, links, regions = load_all()
        self.regions = regions
        for region in regions:
            self.scene.addItem(region)

        self.nodes = nodes
        for node in nodes:
            node.touched.connect(self._on_node_touched)

            self.scene.addItem(node)
        for link in links:
            target, source = link.target, link.source
            if source.id > target.id:
                source, target = target, source
            self.pair_nodes_link[(target.id, source.id)] = link
            self.node_links[target.id].append(link)
            self.node_links[source.id].append(link)

            self.scene.addItem(link)

    def save(self):
        save_all(self.nodes, list(self.pair_nodes_link.values()), self.regions)

    def add_button(self, name, func, layout):
        b = QtWidgets.QPushButton(name)
        b.clicked.connect(func)
        layout.addWidget(b)
        return b

    def add_node(self, x=100, y=100, text="node", color="green") -> Node:
        item = Node(text)
        item.touched.connect(self._on_node_touched)
        new_pos = self.view.mapToScene(x, y)

        self.scene.addItem(item)
        item.setPos(new_pos)
        item.setBrush(QtGui.QColor(color))
        self.nodes.append(item)
        self._select_node(item)
        return item

    def add_region(self, x=100, y=100, text="region") -> Region:
        region = Region(text)
        region.setPos(x, y)
        self.scene.addItem(region)
        self.regions.append(region)

        return region

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
        self.node_links[source.id].append(link)
        self.node_links[target.id].append(link)

    def _on_node_touched(self, node: Node) -> None:
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

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1 / 1.2, 1 / 1.2)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.showFullScreen()
    sys.exit(app.exec())
