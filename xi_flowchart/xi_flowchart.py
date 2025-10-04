#!/usr/bin/env python3
"""
xi_flowchart.py

A lightweight flowchart editor using PyQt6.
Features:
- Add draggable nodes with editable text
- Connect nodes with directed edges (arrow heads)
- Select / move / delete nodes & edges
- Save / load to JSON
- Export canvas to PNG

Dependencies:
- PyQt6

Run:
python xi_flowchart.py

"""

import sys
import json
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QInputDialog, QMessageBox, QLabel
)
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter, QPixmap
from PyQt6.QtCore import Qt, QPointF, QRectF


NODE_WIDTH = 160
NODE_HEIGHT = 60


class NodeItem(QGraphicsRectItem):
    def __init__(self, id_, text, x, y):
        super().__init__(0, 0, NODE_WIDTH, NODE_HEIGHT)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        # Darker background with border
        self.setBrush(QBrush(QColor(60, 60, 60)))
        self.setPen(QPen(QColor(200, 200, 200), 2))  # border added
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setTextWidth(NODE_WIDTH - 10)
        self.text_item.setDefaultTextColor(QColor(240, 240, 240))
        self.text_item.setPos(5, 5)
        self.id = id_
        self.edges = set()  # initialize edges before using
        self.update_position(x, y)

    def update_position(self, x, y):
        self.setPos(x, y)

    def mouseDoubleClickEvent(self, event):
        current = self.text_item.toPlainText()
        new_text, ok = QInputDialog.getMultiLineText(None, "Edit Node", "Text:", current)
        if ok:
            self.text_item.setPlainText(new_text)
        super().mouseDoubleClickEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for e in list(self.edges):
                e.update_position()
        return super().itemChange(change, value)


class EdgeItem(QGraphicsLineItem):
    def __init__(self, source: NodeItem, target: NodeItem):
        super().__init__()
        self.setZValue(-1)
        self.source = source
        self.target = target
        pen = QPen(QColor(240, 240, 240))
        pen.setWidth(2)
        self.setPen(pen)
        source.edges.add(self)
        target.edges.add(self)
        self.update_position()

    def update_position(self):
        p1 = self.source.sceneBoundingRect().center()
        p2 = self.target.sceneBoundingRect().center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        self.prepareGeometryChange()

    def paint(self, painter: QPainter, option, widget=None):
        super().paint(painter, option, widget)
        line = self.line()
        dx = line.x2() - line.x1()
        dy = line.y2() - line.y1()
        angle = math.atan2(dy, dx)
        arrow_size = 10
        p2 = QPointF(line.x2(), line.y2())
        s1 = QPointF(p2.x() - arrow_size * math.cos(angle - math.pi / 6),
                     p2.y() - arrow_size * math.sin(angle - math.pi / 6))
        s2 = QPointF(p2.x() - arrow_size * math.cos(angle + math.pi / 6),
                     p2.y() - arrow_size * math.sin(angle + math.pi / 6))
        path = QPainterPath()
        path.moveTo(p2)
        path.lineTo(s1)
        path.lineTo(s2)
        path.lineTo(p2)
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawPath(path)

    def remove(self):
        try:
            self.source.edges.discard(self)
            self.target.edges.discard(self)
            scene = self.scene()
            if scene:
                scene.removeItem(self)
        except Exception:
            pass


class FlowScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setBackgroundBrush(QColor(30, 30, 30))
        self.node_id_counter = 1
        self.mode = 'select'
        self.temp_line = None
        self.connect_source = None

    def add_node(self, x, y, text="New Node"):
        node = NodeItem(self.node_id_counter, text, x, y)
        self.node_id_counter += 1
        self.addItem(node)
        return node

    def mousePressEvent(self, event):
        if self.mode == 'add' and event.button() == Qt.MouseButton.LeftButton:
            pos = event.scenePos()
            self.add_node(pos.x(), pos.y())
            return
        if self.mode == 'connect' and event.button() == Qt.MouseButton.LeftButton:
            items = self.items(event.scenePos())
            for it in items:
                if isinstance(it, NodeItem):
                    self.connect_source = it
                    self.temp_line = QGraphicsLineItem()
                    pen = QPen(QColor(200, 200, 200))
                    pen.setStyle(Qt.PenStyle.DashLine)
                    pen.setWidth(2)
                    self.temp_line.setPen(pen)
                    p = self.connect_source.sceneBoundingRect().center()
                    self.temp_line.setLine(p.x(), p.y(), event.scenePos().x(), event.scenePos().y())
                    self.addItem(self.temp_line)
                    break
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_line:
            p = self.connect_source.sceneBoundingRect().center()
            self.temp_line.setLine(p.x(), p.y(), event.scenePos().x(), event.scenePos().y())
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_line:
            items = self.items(event.scenePos())
            target = None
            for it in items:
                if isinstance(it, NodeItem) and it is not self.connect_source:
                    target = it
                    break
            self.removeItem(self.temp_line)
            self.temp_line = None
            if target:
                edge = EdgeItem(self.connect_source, target)
                self.addItem(edge)
            self.connect_source = None
            return
        super().mouseReleaseEvent(event)

    def clear_all(self):
        for item in list(self.items()):
            self.removeItem(item)
        self.node_id_counter = 1

    def to_dict(self):
        nodes = []
        edges = []
        for it in self.items():
            if isinstance(it, NodeItem):
                nodes.append({'id': it.id, 'text': it.text_item.toPlainText(), 'x': it.pos().x(), 'y': it.pos().y()})
            elif isinstance(it, EdgeItem):
                edges.append({'source': it.source.id, 'target': it.target.id})
        return {'nodes': nodes, 'edges': edges}

    def from_dict(self, data):
        self.clear_all()
        id_map = {}
        for n in data.get('nodes', []):
            node = self.add_node(n['x'], n['y'], n.get('text', ''))
            node.id = n['id']
            id_map[node.id] = node
            self.node_id_counter = max(self.node_id_counter, node.id + 1)
        for e in data.get('edges', []):
            s = id_map.get(e['source'])
            t = id_map.get(e['target'])
            if s and t:
                edge = EdgeItem(s, t)
                self.addItem(edge)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('xi_flowchart')
        self.setMinimumSize(900, 600)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        toolbar = QHBoxLayout()
        self.mode_label = QLabel('Mode: Select')
        toolbar.addWidget(self.mode_label)
        btn_add = QPushButton('Add Node')
        btn_connect = QPushButton('Connect')
        btn_select = QPushButton('Select')
        btn_delete = QPushButton('Delete Selected')
        btn_save = QPushButton('Save')
        btn_load = QPushButton('Load')
        btn_export = QPushButton('Export PNG')
        btn_clear = QPushButton('Clear')
        for b in (btn_add, btn_connect, btn_select, btn_delete, btn_save, btn_load, btn_export, btn_clear):
            toolbar.addWidget(b)
        layout.addLayout(toolbar)
        self.scene = FlowScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        layout.addWidget(self.view)
        btn_add.clicked.connect(self.set_add_mode)
        btn_connect.clicked.connect(self.set_connect_mode)
        btn_select.clicked.connect(self.set_select_mode)
        btn_delete.clicked.connect(self.delete_selected)
        btn_save.clicked.connect(self.save_file)
        btn_load.clicked.connect(self.load_file)
        btn_export.clicked.connect(self.export_png)
        btn_clear.clicked.connect(self.clear_all)
        instr = QLabel('Double-click a node to edit text. Drag nodes to move. Use Connect mode to draw edges.')
        layout.addWidget(instr)

    def set_add_mode(self):
        self.scene.mode = 'add'
        self.mode_label.setText('Mode: Add')

    def set_connect_mode(self):
        self.scene.mode = 'connect'
        self.mode_label.setText('Mode: Connect')

    def set_select_mode(self):
        self.scene.mode = 'select'
        self.mode_label.setText('Mode: Select')

    def delete_selected(self):
        for it in list(self.scene.selectedItems()):
            if isinstance(it, NodeItem):
                for e in list(it.edges):
                    e.remove()
                self.scene.removeItem(it)
            elif isinstance(it, EdgeItem):
                it.remove()

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save flowchart', filter='JSON Files (*.json)')
        if not path:
            return
        data = self.scene.to_dict()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Load flowchart', filter='JSON Files (*.json)')
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.scene.from_dict(data)
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Export PNG', filter='PNG Files (*.png)')
        if not path:
            return
        rect = self.scene.itemsBoundingRect()
        img = QPixmap(int(rect.width()) + 20, int(rect.height()) + 20)
        img.fill(QColor(30, 30, 30))
        painter = QPainter(img)
        self.scene.render(painter, target=QRectF(img.rect()), source=rect)
        painter.end()
        img.save(path)

    def clear_all(self):
        ok = QMessageBox.question(self, 'Clear', 'Clear the canvas?')
        if ok == QMessageBox.StandardButton.Yes:
            self.scene.clear_all()


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()