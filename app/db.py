import sqlite3
from typing import Text
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from main import RectWithText


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

def store_link(id1, id2):
    cursor.execute("insert into links (node1_id, node2_id) values (?, ?)", (id1, id2))
    conn.commit()
def store_node(node: "RectWithText"):
    res = cursor.execute("INSERT INTO nodes (text, x, y, color) VALUES (?, ?, ?, ?) returning id", (node.label.toPlainText(), node.x(),  node.y(), str(node.brush().color().name())))
    id =    res.fetchone()[0]
    conn.commit()
    return id

def delete_all_nodes():
    cursor.execute("delete from nodes")
    cursor.execute("delete from links")
def restore_all_nodes(widget):
    nodes = cursor.execute("select * from nodes").fetchall()
    links = cursor.execute("select * from links").fetchall()
    node_map = {}
    for id, text, x, y, color in nodes:
        node_map[id] = widget.add_node(int(x), int(y), text, color)
    for id, node1_id, node2_id in links:
        widget.link_2_nodes(node_map[node1_id], node_map[node2_id])

    return nodes
