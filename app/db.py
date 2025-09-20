import sqlite3
from typing import Text
from typing import TYPE_CHECKING

from PySide6 import QtGui

if TYPE_CHECKING:

    from main import Node, Link


conn = sqlite3.connect("my_database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    x INTEGER,
    y INTEGER,
    color TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node1_id INTEGER,
    node2_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nodes2 (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    x INTEGER,
    y INTEGER,
    color TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS links2 (
    id TEXT PRIMARY KEY,
    node1_id INTEGER,
    node2_id INTEGER
)
""")
def save_all(nodes: list["Node"], links: list["Link"]):
    for node in nodes:
        cursor.execute("""
            INSERT INTO nodes2 (id, text, x, y, color)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                text = excluded.text,
                x = excluded.x,
                y = excluded.y,
                color = excluded.color
        """, (
            str(node.id),
            node.label.toPlainText(),
            node.scenePos().x(),
            node.scenePos().y(),
            node.brush().color().name()
        ))

    for link in links:
        cursor.execute("""
            INSERT INTO links2 (id, node1_id, node2_id)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                node1_id = excluded.node1_id,
                node2_id = excluded.node2_id
        """, (
            str(link.id),
            link.source.id,
            link.target.id
        ))
    conn.commit()


def load_all() -> tuple[list["Node"], list["Link"]]:

    from main import Node, Link
    nodes_db = cursor.execute("select * from nodes2").fetchall()
    links_db = cursor.execute("select * from links2").fetchall()
    nodes = []
    nodes_dict = {}
    for id_, text, x, y, color in nodes_db:
        n = Node(id=id_, text=text)
        n.setPos(x, y)
        n.setBrush(QtGui.QColor(color))
        nodes.append(n)
        nodes_dict[n.id] = n

    links = []
    for id_, n1_id, n2_id in links_db:
        n1 = nodes_dict.get(str(n1_id))
        n2 = nodes_dict.get(str(n2_id))
        if not n1 or not n2:
            continue
        l = Link(n1, n2, id=id_)
        links.append(l)

    return nodes, links

