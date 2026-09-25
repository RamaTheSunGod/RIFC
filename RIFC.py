import os
import re
import math
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

try:
    import cairosvg
    HAS_CAIROSVG = True
except Exception:
    # Catch Exception, not just ImportError, because cairosvg raises OSError if Cairo DLLs are missing on Windows.
    HAS_CAIROSVG = False

# --- Configuración por defecto ---
PRESETS = {
    "Clásico": {
        "font": "Helvetica",
        "bg_color": "#ffffff",
        "edge_color": "#7f8c8d",
        "text_color": "#333333",
        "inicio_fill": "#A8E6CF",
        "inicio_stroke": "#27ae60",
        "fin_fill": "#FF8B94",
        "fin_stroke": "#27ae60",
        "box_fill": "#D1EAED",
        "box_stroke": "#2c3e50",
        "diamond_fill": "#FFF3B0",
        "diamond_stroke": "#f39c12",
    },
    "Moderno": {
        "font": "Segoe UI",
        "bg_color": "#ffffff",
        "edge_color": "#5c5c5c",
        "text_color": "#333333",
        "inicio_fill": "#ffb3ba",
        "inicio_stroke": "#ffb3ba",
        "fin_fill": "#ffb3ba",
        "fin_stroke": "#ffb3ba",
        "box_fill": "#bae1ff",
        "box_stroke": "#bae1ff",
        "diamond_fill": "#baffc9",
        "diamond_stroke": "#baffc9",
    },
    "Académico": {
        "font": "Times New Roman",
        "bg_color": "#ffffff",
        "edge_color": "#000000",
        "text_color": "#000000",
        "inicio_fill": "#ffffff",
        "inicio_stroke": "#000000",
        "fin_fill": "#ffffff",
        "fin_stroke": "#000000",
        "box_fill": "#ffffff",
        "box_stroke": "#000000",
        "diamond_fill": "#ffffff",
        "diamond_stroke": "#000000",
    }
}

DEFAULT_DIAGRAM_CONFIG = PRESETS["Clásico"]

# --- Parser y Motor de Renderizado Nativo SVG ---
class NativeFlowCompiler:
    def __init__(self, code, config=None):
        self.raw_code = code
        self.config = config if config else DEFAULT_DIAGRAM_CONFIG.copy()
        self.nodes = []  # Lista de nodos a dibujar: {'id', 'type', 'text', 'x', 'y', 'width', 'height'}
        self.edges = []  # Lista de conexiones: {'from', 'to', 'label'}
        self.labels = {}
        self.loop_starts = {}
        self.pending_jmps = []
        self.has_inicio = False
        self.has_fin = False

    def tokenize(self, text):
        pattern = r'(\(|\)|[^\s\(\)]+)'
        return [t for t in re.findall(pattern, text)]

    def extract_block(self, tokens, index):
        if index >= len(tokens) or tokens[index] != '(':
            return [], index
        depth = 1
        start = index + 1
        i = start
        while i < len(tokens) and depth > 0:
            if tokens[i] == '(': depth += 1
            elif tokens[i] == ')': depth -= 1
            i += 1
        return tokens[start:i-1], i

    def parse(self):
        tokens = self.tokenize(self.raw_code)
        self.parse_sequence(tokens)
        
        # Resolver jmps
        for src, target_label, *opt_lbl in self.pending_jmps:
            lbl = opt_lbl[0] if opt_lbl else ""
            if target_label in self.labels:
                self.edges.append({'from': src, 'to': self.labels[target_label], 'label': lbl, 'dashed': False})

    def parse_sequence(self, tokens, current_source=None, current_loop_start=None):
        i = 0
        while i < len(tokens):
            tok = tokens[i]

            if tok.lower() in ("inicio", "start"):
                if not self.has_inicio:
                    nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': nid, 'type': 'oval', 'text': 'Inicio', 'fill': self.config['inicio_fill'], 'stroke': self.config['inicio_stroke']})
                    if current_source: self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})
                    current_source = nid
                    self.has_inicio = True
                i += 1

            elif tok.lower() in ("fin", "end"):
                if not self.has_fin:
                    nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': nid, 'type': 'oval', 'text': 'Fin', 'fill': self.config['fin_fill'], 'stroke': self.config['fin_stroke']})
                    if current_source:
                        if isinstance(current_source, list):
                            for src in current_source:
                                self.edges.append({'from': src, 'to': nid, 'label': '', 'dashed': False})
                        else:
                            self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})
                    current_source = nid
                    self.has_fin = True
                i += 1

            elif tok.lower() == "loopstart":
                block, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                loop_name = " ".join(block)
                self.loop_starts[loop_name] = current_source

            elif tok.lower() == "loopend":
                block1, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                loop_name = " ".join(block1)
                return_label = ""
                if i < len(tokens) and tokens[i] == '(':
                    block2, next_i2 = self.extract_block(tokens, i)
                    return_label = " ".join(block2)
                    i = next_i2

                if current_source and loop_name in self.loop_starts:
                    # Inject a merge node to collect paths
                    merge_nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': merge_nid, 'type': 'merge', 'text': '', 'fill': 'none', 'stroke': 'none'})
                    
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.edges.append({'from': src, 'to': merge_nid, 'label': '', 'dashed': False})
                    else:
                        self.edges.append({'from': current_source, 'to': merge_nid, 'label': '', 'dashed': False})
                        
                    start_node = self.loop_starts[loop_name]
                    if start_node is not None:
                        target_node = start_node
                        for e in self.edges:
                            if e['from'] == start_node:
                                target_node = e['to']
                                break
                        
                        self.edges.append({'from': merge_nid, 'to': target_node, 'label': return_label, 'dashed': False})
                    
                    current_source = merge_nid

            elif tok.lower() == "act":
                block1, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                if i < len(tokens) and tokens[i] == '(':
                    block2, next_i2 = self.extract_block(tokens, i)
                    label_name, action_text = " ".join(block1), " ".join(block2)
                    i = next_i2
                else:
                    label_name, action_text = None, " ".join(block1)

                nid = f"n_{len(self.nodes)}"
                self.nodes.append({'id': nid, 'type': 'box', 'text': action_text, 'fill': self.config['box_fill'], 'stroke': self.config['box_stroke']})
                if label_name: self.labels[label_name] = nid
                if current_source:
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.edges.append({'from': src, 'to': nid, 'label': '', 'dashed': False})
                    else:
                        self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})
                current_source = nid

            elif tok.lower() == "jmp":
                block, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                target_label = " ".join(block)
                if current_source: self.pending_jmps.append((current_source, target_label))
                current_source = None

            elif tok.lower() == "if":
                cond_block, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                cond_text = " ".join(cond_block)
                
                nid = f"n_{len(self.nodes)}"
                self.nodes.append({'id': nid, 'type': 'diamond', 'text': cond_text, 'fill': self.config['diamond_fill'], 'stroke': self.config['diamond_stroke']})
                if current_source:
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.edges.append({'from': src, 'to': nid, 'label': '', 'dashed': False})
                    else:
                        self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})

                branches_block, next_i2 = self.extract_block(tokens, i)
                i = next_i2
                branch_ends = self.parse_if_branches(branches_block, nid)
                current_source = branch_ends
            else:
                i += 1
        return current_source

    def parse_if_branches(self, tokens, cond_node_id):
        ends = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if re.match(r'If\d+', tok, re.IGNORECASE):
                branch_label_words = []
                i += 1
                while i < len(tokens) and tokens[i] != '(':
                    branch_label_words.append(tokens[i])
                    i += 1
                branch_label = " ".join(branch_label_words)
                branch_actions, next_i = self.extract_block(tokens, i)
                i = next_i

                first_tok = branch_actions[0] if branch_actions else ""
                if first_tok.lower() == "jmp":
                    lbl_block, _ = self.extract_block(branch_actions, 1)
                    target = " ".join(lbl_block)
                    self.pending_jmps.append((cond_node_id, target, branch_label))
                else:
                    # We inject a dummy "from" node reference string just to know where to attach
                    # but actually we can just pass the condition node directly!
                    target_id_preview = f"n_{len(self.nodes)}"
                    branch_end = self.parse_sequence(branch_actions, current_source=None)
                    
                    # Add edge from condition block to the FIRST node in the branch
                    if branch_actions:
                        self.edges.append({'from': cond_node_id, 'to': target_id_preview, 'label': branch_label, 'dashed': False})
                    
                    if branch_end:
                        if isinstance(branch_end, list):
                            ends.extend(branch_end)
                        else:
                            ends.append(branch_end)
                    else:
                        ends.append(cond_node_id) # if branch is empty, it drops through
            else:
                i += 1
        return ends

    def calculate_layout(self):
        start_y = 50
        spacing_y = 120
        center_x = 300
        
        node_coords = {}
        
        # Build adjacency list
        adj = {}
        incoming = {}
        for node in self.nodes:
            adj[node['id']] = []
            incoming[node['id']] = []
            
        for edge in self.edges:
            if edge['dashed']: continue
            src, dst = edge['from'], edge['to']
            if src in adj: adj[src].append(dst)
            if dst in incoming: incoming[dst].append(src)

        # Topological sorting to identify forward edges and levels
        # Assuming n_0 is Inicio
        levels = {node['id']: 0 for node in self.nodes}
        if self.nodes:
            start_node = self.nodes[0]['id']
            queue = [start_node]
            visited = set()
            while queue:
                curr = queue.pop(0)
                visited.add(curr)
                for child in adj.get(curr, []):
                    # We define a back-edge if the child is already in visited.
                    if child not in visited:
                        # Forward edge. The child's level is max(its current level, parent level + 1)
                        levels[child] = max(levels[child], levels[curr] + 1)
                        if child not in queue:
                            queue.append(child)

        for idx, node in enumerate(self.nodes):
            lvl = levels.get(node['id'], 0)
            node_coords[node['id']] = {
                'x': center_x, 
                'y': start_y + (lvl * spacing_y), 
                'idx': idx,
                'type': node.get('type', 'box'),
                'out_degree': len(adj.get(node['id'], []))
            }

        # Assign X coordinates by spreading branches and preserving them for children
        # BFS style to traverse and pass down constraints
        queue = []
        if self.nodes:
            start_node = self.nodes[0]['id']
            queue.append((start_node, center_x))
            
        visited = set()
        
        while queue:
            curr, curr_x = queue.pop(0)
            if curr in visited: continue
            visited.add(curr)
            
            if curr in node_coords:
                node_coords[curr]['x'] = curr_x

            children = adj.get(curr, [])
            
            # Identify if it's a forward jump based on level
            forward_children = []
            for child in children:
                if levels.get(child, 0) > levels.get(curr, 0):
                    forward_children.append(child)

            if len(forward_children) > 1:
                # Spread
                width_per_branch = 220
                start_offset = - (len(forward_children) - 1) * width_per_branch / 2
                for i, child_id in enumerate(forward_children):
                    child_x = curr_x + start_offset + (i * width_per_branch)
                    queue.append((child_id, child_x))
            elif len(forward_children) == 1:
                child = forward_children[0]
                # Check if child is a merge point (has multiple forward incoming edges)
                forward_incoming = [src for src in incoming.get(child, []) if levels.get(src, 0) < levels.get(child, 0)]
                if len(forward_incoming) > 1:
                    queue.append((child, center_x))
                else:
                    queue.append((child, curr_x))
        
        # Calculate bounds and shift if necessary
        min_x = min(coords['x'] for coords in node_coords.values()) if node_coords else center_x
        shift_x = 0
        if min_x < 100:
            shift_x = 100 - min_x
            for coords in node_coords.values():
                coords['x'] += shift_x
            center_x += shift_x

        max_y = start_y + (max(levels.values()) * spacing_y) + 150 if levels else 600
        max_x = max(coords['x'] for coords in node_coords.values()) + 150 if node_coords else 600
        svg_width = max(600, max_x)
        
        return node_coords, center_x, max_y, svg_width

    def generate_svg(self, filepath):
        self.parse()
        node_coords, center_x, max_y, svg_width = self.calculate_layout()

        bg = self.config['bg_color']
        ec = self.config['edge_color']
        tc = self.config['text_color']
        font = self.config['font']
        
        svg_lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{max_y}" viewBox="0 0 {svg_width} {max_y}">',
            '<style>',
            f'  text {{ font-family: {font}, Arial, sans-serif; font-size: 12px; text-anchor: middle; dominant-baseline: middle; fill: {tc}; }}',
            f'  .text-label {{ paint-order: stroke; stroke: {bg}; stroke-width: 4px; stroke-linecap: butt; stroke-linejoin: miter; }}',
            f'  .box {{ stroke: {self.config["box_stroke"]}; stroke-width: 2; rx: 8; ry: 8; }}',
            f'  .oval-inicio {{ stroke: {self.config["inicio_stroke"]}; stroke-width: 2; rx: 20; ry: 20; }}',
            f'  .oval-fin {{ stroke: {self.config["fin_stroke"]}; stroke-width: 2; rx: 20; ry: 20; }}',
            f'  .diamond {{ stroke: {self.config["diamond_stroke"]}; stroke-width: 2; }}',
            f'  .edge {{ stroke: {ec}; stroke-width: 2; fill: none; marker-end: url(#arrow); }}',
            '</style>',
            '<defs>',
            '  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            f'    <path d="M 0 2 L 10 5 L 0 8 z" fill="{ec}"/>',
            '  </marker>',
            '</defs>',
            f'<rect width="100%" height="100%" fill="{bg}"/>'
        ]

        # Dibujar líneas de conexión (Edges)
        backward_targets = {}
        edge_labels_buffer = []
        for edge in self.edges:
            if edge['from'] in node_coords and edge['to'] in node_coords:
                p1 = node_coords[edge['from']]
                p2 = node_coords[edge['to']]
                
                # Merge nodes have no height, they are just points
                y_offset_1 = 0 if p1.get('type') == 'merge' else 25
                y_offset_2 = 0 if p2.get('type') == 'merge' else 25
                
                y1 = p1['y'] + y_offset_1 if p1['y'] < p2['y'] else p1['y'] - y_offset_1
                
                # Check for backward jump (loop) based on Y coordinates
                is_backward = p1['y'] >= p2['y']
                
                if is_backward:
                    y2 = p2['y'] - (y_offset_2 + 15) # Point above the node
                else:
                    y2 = p2['y'] - y_offset_2 if p1['y'] < p2['y'] else p2['y'] + y_offset_2
                
                x1, x2 = p1['x'], p2['x']

                # Detect if the jump bypasses levels directly downwards
                is_long_jump = not is_backward and abs(p1['y'] - p2['y']) > 150 # roughly more than one spacing_y

                if is_backward:
                    # Curve for backward loops: go right, up, and back left to point into the incoming stream
                    tgt = edge['to']
                    backward_targets[tgt] = backward_targets.get(tgt, 0) + 1
                    radius_offset = 150 + (backward_targets[tgt] * 30)
                    
                    x1_offset = 0 if p1.get('type') == 'merge' else 40
                    path_d = f"M {x1+x1_offset} {p1['y']} C {x1+radius_offset} {p1['y']}, {x2+radius_offset} {p2['y']-60}, {x2} {y2}"
                    svg_lines.append(f'<path d="{path_d}" class="edge" fill="none"/>')
                    if edge['label']:
                        edge_labels_buffer.append(f'<text x="{x1+radius_offset-50}" y="{(p1["y"]+p2["y"])/2}" class="text-label" font-weight="bold">{edge["label"]}</text>')
                elif is_long_jump and x1 == x2:
                    # Salto largo hacia adelante que cruzaría los bloques, curvar por la izquierda
                    x1_offset = 0 if p1.get('type') == 'merge' else 40
                    x2_offset = 0 if p2.get('type') == 'merge' else 40
                    path_d = f"M {x1-x1_offset} {p1['y']} C {x1-150} {p1['y']}, {x2-150} {p2['y']}, {x2-x2_offset} {p2['y']}"
                    svg_lines.append(f'<path d="{path_d}" class="edge" fill="none"/>')
                    if edge['label']:
                        edge_labels_buffer.append(f'<text x="{x1-110}" y="{(p1["y"]+p2["y"])/2}" class="text-label" font-weight="bold">{edge["label"]}</text>')
                else:
                    # Línea recta normal o cruzada
                    svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>')
                    if edge['label']:
                        if x1 != x2 and not is_backward:
                            mid_x, mid_y = x1 + (x2-x1)*0.5, y1 + (y2-y1)*0.5
                        else:
                            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                        edge_labels_buffer.append(f'<text x="{mid_x}" y="{mid_y}" class="text-label" font-weight="bold">{edge["label"]}</text>')

        # Dibujar nodos
        for node in self.nodes:
            coords = node_coords[node['id']]
            x, y = coords['x'], coords['y']
            fill = node['fill']
            
            if node['type'] == 'merge':
                continue # Do not draw anything for merge nodes

            if node['type'] == 'box':
                svg_lines.append(f'<rect x="{x-80}" y="{y-25}" width="160" height="50" class="box" fill="{fill}"/>')
                svg_lines.append(f'<text x="{x}" y="{y}">{node["text"]}</text>')
            elif node['type'] == 'oval':
                cls = "oval-inicio" if node["text"].lower() == "inicio" else "oval-fin"
                svg_lines.append(f'<rect x="{x-60}" y="{y-20}" width="120" height="40" rx="20" ry="20" class="{cls}" fill="{fill}"/>')
                svg_lines.append(f'<text x="{x}" y="{y}" font-weight="bold">{node["text"]}</text>')
            elif node['type'] == 'diamond':
                out_degree = coords.get('out_degree', 2)
                width = 80 + (max(0, out_degree - 2) * 20)
                points = f"{x},{y-30} {x+width},{y} {x},{y+30} {x-width},{y}"
                svg_lines.append(f'<polygon points="{points}" class="diamond" fill="{fill}"/>')
                svg_lines.append(f'<text x="{x}" y="{y}">{node["text"]}</text>')

        # Draw labels last so they appear on top
        svg_lines.extend(edge_labels_buffer)

        svg_lines.append('</svg>')

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_lines))
            
    def draw_on_canvas(self, canvas):
        self.parse()
        node_coords, center_x, max_y, svg_width = self.calculate_layout()
        
        bg = self.config['bg_color']
        ec = self.config['edge_color']
        tc = self.config['text_color']
        font = self.config['font']
        
        canvas.delete("all")
        canvas.configure(bg=bg)
        canvas.config(scrollregion=(0, 0, svg_width, max_y))
        
        # Helper to draw arrows
        def create_arrow(x1, y1, x2, y2, color, dash=None):
            canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=color, width=2, dash=dash)
            
        def create_curved_arrow(x1, y1, cx1, cy1, cx2, cy2, x2, y2, color, dash=None):
            steps = 20
            points = []
            for i in range(steps + 1):
                t = i / steps
                px = (1-t)**3 * x1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * x2
                py = (1-t)**3 * y1 + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * y2
                points.extend([px, py])
            canvas.create_line(points, arrow=tk.LAST, fill=color, width=2, dash=dash, smooth=True)

        def draw_label(x, y, text):
            bg_id = canvas.create_rectangle(0, 0, 0, 0, fill=bg, outline="")
            text_id = canvas.create_text(x, y, text=text, fill=tc, font=(font, 10, "bold"))
            bbox = canvas.bbox(text_id)
            if bbox:
                canvas.coords(bg_id, bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2)
                canvas.tag_raise(text_id, bg_id)

        backward_targets = {}
        edge_labels_buffer = []
        for edge in self.edges:
            if edge['from'] in node_coords and edge['to'] in node_coords:
                p1 = node_coords[edge['from']]
                p2 = node_coords[edge['to']]
                
                y_offset_1 = 0 if p1.get('type') == 'merge' else 25
                y_offset_2 = 0 if p2.get('type') == 'merge' else 25
                
                y1 = p1['y'] + y_offset_1 if p1['y'] < p2['y'] else p1['y'] - y_offset_1
                
                # Check for backward jump (loop) based on Y coordinates
                is_backward = p1['y'] >= p2['y']
                
                if is_backward:
                    y2 = p2['y'] - (y_offset_2 + 15)
                else:
                    y2 = p2['y'] - y_offset_2 if p1['y'] < p2['y'] else p2['y'] + y_offset_2
                
                x1, x2 = p1['x'], p2['x']

                # Detect if the jump bypasses levels directly downwards
                is_long_jump = not is_backward and abs(p1['y'] - p2['y']) > 150 # roughly more than one spacing_y

                if is_backward:
                    tgt = edge['to']
                    backward_targets[tgt] = backward_targets.get(tgt, 0) + 1
                    radius_offset = 150 + (backward_targets[tgt] * 30)
                    
                    # Curve for backward loops: go right, up, and back left to point into the incoming stream
                    x1_offset = 0 if p1.get('type') == 'merge' else 40
                    create_curved_arrow(x1+x1_offset, p1['y'], x1+radius_offset, p1['y'], x2+radius_offset, p2['y']-60, x2, y2, ec)
                    if edge['label']:
                        edge_labels_buffer.append((x1+radius_offset-50, (p1["y"]+p2["y"])/2, edge["label"]))
                elif is_long_jump and x1 == x2:
                    # Salto largo hacia adelante que cruzaría los bloques, curvar por la izquierda
                    x1_offset = 0 if p1.get('type') == 'merge' else 40
                    x2_offset = 0 if p2.get('type') == 'merge' else 40
                    create_curved_arrow(x1-x1_offset, p1['y'], x1-150, p1['y'], x2-150, p2['y'], x2-x2_offset, y2, ec)
                    if edge['label']:
                        edge_labels_buffer.append((x1-110, (p1["y"]+p2["y"])/2, edge["label"]))
                else:
                    create_arrow(x1, y1, x2, y2, ec)
                    if edge['label']:
                        if x1 != x2 and not is_backward:
                            mid_x, mid_y = x1 + (x2-x1)*0.5, y1 + (y2-y1)*0.5
                        else:
                            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                        edge_labels_buffer.append((mid_x, mid_y, edge["label"]))

        for node in self.nodes:
            coords = node_coords[node['id']]
            x, y = coords['x'], coords['y']
            fill = node['fill']
            
            if node['type'] == 'merge':
                continue

            if node['type'] == 'box':
                canvas.create_rectangle(x-80, y-25, x+80, y+25, fill=fill, outline=self.config["box_stroke"], width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10), fill=tc)
            elif node['type'] == 'oval':
                stroke = self.config["inicio_stroke"] if node["text"].lower() == "inicio" else self.config["fin_stroke"]
                canvas.create_oval(x-60, y-20, x+60, y+20, fill=fill, outline=stroke, width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10, "bold"), fill=tc)
            elif node['type'] == 'diamond':
                out_degree = coords.get('out_degree', 2)
                width = 80 + (max(0, out_degree - 2) * 20)
                points = [x, y-30, x+width, y, x, y+30, x-width, y]
                canvas.create_polygon(points, fill=fill, outline=self.config["diamond_stroke"], width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10), fill=tc)

        # Draw labels last so they appear on top
        for label_cmd in edge_labels_buffer:
            draw_label(*label_cmd)


# --- Interfaz Gráfica de Escritorio (GUI) ---
class RIFCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RIFC (Rama's Instant Flow Chart)")
        self.root.geometry("1200x700")
        
        # Intentar cargar un icono personalizado si existe
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # State
        self.current_preset = "Clásico"
        self.app_theme = "Oscuro"

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=5)

        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self.nuevo_proyecto)
        file_menu.add_command(label="Abrir Proyecto (.txt)", command=self.abrir_proyecto)
        file_menu.add_command(label="Guardar Proyecto (.txt)", command=self.guardar_proyecto)
        file_menu.add_separator()
        file_menu.add_command(label="Preferencias...", command=self.abrir_preferencias)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Diagrama...", command=self.exportar_diagrama)
        menubar.add_cascade(label="Archivo", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Copiar", command=lambda: self.root.focus_get().event_generate('<<Copy>>'))
        edit_menu.add_command(label="Pegar", command=lambda: self.root.focus_get().event_generate('<<Paste>>'))
        edit_menu.add_command(label="Cortar", command=lambda: self.root.focus_get().event_generate('<<Cut>>'))
        edit_menu.add_separator()
        edit_menu.add_command(label="Seleccionar Todo", command=self.seleccionar_todo)
        menubar.add_cascade(label="Editar", menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Comandos y Ayuda", command=self.mostrar_ayuda)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.root.config(menu=menubar)

        # Main PanedWindow for split screen
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(expand=True, fill="both", padx=10, pady=10)

        # Left Frame: Editor
        left_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=1)

        self.text_editor = tk.Text(left_frame, wrap="word", font=("Consolas", 12), bg="#282c34", fg="#abb2bf", insertbackground="white")
        self.text_editor.pack(expand=True, fill="both")
        
        # Right Frame: Preview
        right_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=2)
        
        # Canvas inside right frame
        self.canvas = tk.Canvas(right_frame, bg="#ffffff", highlightthickness=1, highlightbackground="#ccc")
        
        # Add scrollbars to canvas
        vbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        hbar = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, expand=True, fill="both")

        # Keep a reference to the image to prevent garbage collection
        self.preview_image = None
        
        ejemplo = """Inicio

loopstart(mi_ciclo)
    act(leer)(leer sensor de estado)
    
    If (sensor activo)(
        If1 Si ( act(activa motor) )
        If2 No ( jmp(leer) )
        If3 Tal vez ( act(modo de fallo) )
    )
loopend(mi_ciclo)(hasta reintentar)

Fin"""
        self.text_editor.insert("1.0", ejemplo)

        # Bottom Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_preview = tk.Button(btn_frame, text="Actualizar Vista Previa (Ctrl+Enter)", bg="#4dabf7", fg="white", font=("Helvetica", 10, "bold"), command=self.actualizar_preview, relief=tk.FLAT)
        self.btn_preview.pack(side="left", padx=5)

        self.btn_export = tk.Button(btn_frame, text="Exportar Diagrama...", bg="#40c057", fg="white", font=("Helvetica", 10, "bold"), command=self.exportar_diagrama, relief=tk.FLAT)
        self.btn_export.pack(side="left", padx=5)

        # Configure tags for syntax highlighting
        self.text_editor.tag_configure("keyword", foreground="#c678dd", font=("Consolas", 12, "bold"))
        self.text_editor.tag_configure("bracket", foreground="#61afef")
        self.text_editor.tag_configure("control", foreground="#e5c07b", font=("Consolas", 12, "bold"))

        # Bindings
        self.root.bind('<Control-Return>', lambda event: self.actualizar_preview())
        self.text_editor.bind("<KeyRelease>", self.highlight_syntax)
        self.text_editor.bind("(", self.auto_close_paren)
        
        # Initial apply theme, highlight and preview
        self.aplicar_tema()

    def highlight_syntax(self, event=None):
        content = self.text_editor.get("1.0", tk.END)
        self.text_editor.mark_set("range_start", "1.0")
        
        # Clear existing tags
        for tag in ["keyword", "bracket", "control"]:
            self.text_editor.tag_remove(tag, "1.0", tk.END)
            
        # Highlight brackets
        start_idx = "1.0"
        while True:
            start_idx = self.text_editor.search(r'[\(\)]', start_idx, tk.END, regexp=True)
            if not start_idx: break
            end_idx = f"{start_idx}+1c"
            self.text_editor.tag_add("bracket", start_idx, end_idx)
            start_idx = end_idx

        # Highlight keywords
        keywords = r'\b(Inicio|Fin|act|If|loopstart|loopend|jmp|Si|No)\b'
        start_idx = "1.0"
        while True:
            start_idx = self.text_editor.search(keywords, start_idx, tk.END, regexp=True, nocase=True)
            if not start_idx: break
            length = tk.IntVar()
            self.text_editor.search(keywords, start_idx, tk.END, regexp=True, nocase=True, count=length)
            end_idx = f"{start_idx}+{length.get()}c"
            
            word = self.text_editor.get(start_idx, end_idx).lower()
            tag = "control" if word in ["inicio", "fin", "if"] else "keyword"
            
            self.text_editor.tag_add(tag, start_idx, end_idx)
            start_idx = end_idx
            
    def auto_close_paren(self, event):
        self.text_editor.insert(tk.INSERT, "()")
        self.text_editor.mark_set(tk.INSERT, f"{tk.INSERT}-1c")
        return "break" # Prevent default behavior which would insert an extra (

    def actualizar_preview(self):
        codigo = self.text_editor.get("1.0", tk.END)
        if not codigo.strip():
            self.canvas.delete("all")
            return
            
        try:
            config = PRESETS[self.current_preset].copy()
            compiler = NativeFlowCompiler(codigo, config)
            compiler.draw_on_canvas(self.canvas)
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(20, 20, text=f"Error en Preview:\n{e}", anchor="nw", fill="red")

    def seleccionar_todo(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        return 'break'
        
    def mostrar_ayuda(self):
        ayuda_texto = (
            "Comandos Básicos de RIFC:\n\n"
            "- Inicio: Comienza el diagrama.\n"
            "- Fin: Termina el diagrama.\n"
            "- act(etiqueta opcional)(Descripción): Crea una caja de proceso.\n"
            "- If (condición)( If1 Si (act...) If2 No (act...) ): Crea decisión.\n"
            "- loopstart(nombre): Inicia un ciclo.\n"
            "- loopend(nombre)(condición): Finaliza el ciclo y vuelve al inicio.\n"
            "- jmp(etiqueta): Salta a un proceso etiquetado.\n\n"
            "Atajos:\n"
            "- Ctrl+Enter: Actualiza la vista previa."
        )
        messagebox.showinfo("Ayuda y Comandos", ayuda_texto)

    def nuevo_proyecto(self):
        self.text_editor.delete("1.0", tk.END)
        base = "Inicio\n\nact(proceso_1)(Mi primer proceso)\n\nFin"
        self.text_editor.insert("1.0", base)
        self.highlight_syntax()
        self.actualizar_preview()

    def abrir_proyecto(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", f.read())

    def guardar_proyecto(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.text_editor.get("1.0", tk.END))
            messagebox.showinfo("Éxito", "Proyecto guardado.")

    def aplicar_tema(self):
        if self.app_theme == "Oscuro":
            self.text_editor.config(bg="#282c34", fg="#abb2bf", insertbackground="white")
            self.text_editor.tag_configure("keyword", foreground="#c678dd")
            self.text_editor.tag_configure("bracket", foreground="#61afef")
            self.text_editor.tag_configure("control", foreground="#e5c07b")
        else: # Claro
            self.text_editor.config(bg="#ffffff", fg="#333333", insertbackground="black")
            self.text_editor.tag_configure("keyword", foreground="#a626a4")
            self.text_editor.tag_configure("bracket", foreground="#4078f2")
            self.text_editor.tag_configure("control", foreground="#e45649")
        self.highlight_syntax()

    def abrir_preferencias(self):
        pref_win = tk.Toplevel(self.root)
        pref_win.title("Preferencias")
        pref_win.geometry("300x250")
        pref_win.transient(self.root)
        pref_win.grab_set()

        ttk.Label(pref_win, text="Tema de la Interfaz:").pack(pady=(10, 0))
        theme_combo = ttk.Combobox(pref_win, values=["Oscuro", "Claro"], state="readonly")
        theme_combo.set(self.app_theme)
        theme_combo.pack(pady=5)

        ttk.Label(pref_win, text="Estilo del Diagrama:").pack(pady=(10, 0))
        preset_combo = ttk.Combobox(pref_win, values=list(PRESETS.keys()), state="readonly")
        preset_combo.set(self.current_preset)
        preset_combo.pack(pady=5)

        def save_prefs():
            self.app_theme = theme_combo.get()
            self.current_preset = preset_combo.get()
            self.aplicar_tema()
            self.actualizar_preview()
            pref_win.destroy()

        ttk.Button(pref_win, text="Aplicar y Guardar", command=save_prefs).pack(pady=20)

    def exportar_diagrama(self):
        codigo = self.text_editor.get("1.0", tk.END)
        if not codigo.strip():
            return
        filetypes = [("Archivo SVG", "*.svg"), ("Archivo PNG", "*.png"), ("Archivo PDF", "*.pdf")]
        filepath = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=filetypes)
        if filepath:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in [".png", ".pdf"] and not HAS_CAIROSVG:
                messagebox.showerror("Error de Dependencia", f"Para exportar a {ext} se requiere la librería 'cairosvg'.\nInstálala con: pip install cairosvg")
                return
            try:
                config = PRESETS[self.current_preset].copy()
                compiler = NativeFlowCompiler(codigo, config)
                
                if ext == ".svg":
                    compiler.generate_svg(filepath)
                else:
                    # Generate to a temporary SVG file, then convert
                    fd, temp_svg_path = tempfile.mkstemp(suffix=".svg")
                    os.close(fd)
                    compiler.generate_svg(temp_svg_path)
                    
                    if ext == ".png":
                        cairosvg.svg2png(url=temp_svg_path, write_to=filepath)
                    elif ext == ".pdf":
                        cairosvg.svg2pdf(url=temp_svg_path, write_to=filepath)
                    
                    os.remove(temp_svg_path)
                    
                messagebox.showinfo("Éxito", f"¡Diagrama compilado con éxito!\nGuardado en: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Error de compilación:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RIFCApp(root)
    root.mainloop()