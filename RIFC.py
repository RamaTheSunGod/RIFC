import os
import re
import math
import tempfile
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk

try:
    import cairosvg
    HAS_CAIROSVG = True
except Exception:
    # Catch Exception, not just ImportError, because cairosvg raises OSError if Cairo DLLs are missing on Windows.
    HAS_CAIROSVG = False

# --- Configuración por defecto ---
DEFAULT_PRESETS = {
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
    },
    "Personalizado": {
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
    }
}

def load_presets():
    presets = DEFAULT_PRESETS.copy()
    if os.path.exists("rifc_presets.json"):
        try:
            with open("rifc_presets.json", "r", encoding="utf-8") as f:
                loaded = json.load(f)
                for k, v in loaded.items():
                    if k in presets:
                        presets[k].update(v)
                    else:
                        presets[k] = v
        except Exception:
            pass
    return presets

def save_presets(presets):
    with open("rifc_presets.json", "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=4)

PRESETS = load_presets()
DEFAULT_DIAGRAM_CONFIG = PRESETS.get("Clásico", list(PRESETS.values())[0])

# --- App Settings (Tema, Idioma, Preset) ---
DEFAULT_APP_CONFIG = {
    "theme": "Oscuro",
    "preset": "Clásico",
    "lang": "en"
}

def load_app_config():
    config = DEFAULT_APP_CONFIG.copy()
    if os.path.exists("rifc_config.json"):
        try:
            with open("rifc_config.json", "r", encoding="utf-8") as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception:
            pass
    return config

def save_app_config(config):
    with open("rifc_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

APP_CONFIG = load_app_config()

# --- I18n Dictionary ---
I18N = {
    "es": {
        "menu_file": "Archivo",
        "menu_new": "Nuevo",
        "menu_open": "Abrir Proyecto (.txt)",
        "menu_save": "Guardar Proyecto (.txt)",
        "menu_prefs": "Preferencias...",
        "menu_export": "Exportar Diagrama...",
        "menu_edit": "Editar",
        "menu_copy": "Copiar",
        "menu_paste": "Pegar",
        "menu_cut": "Cortar",
        "menu_sel_all": "Seleccionar Todo",
        "menu_help": "Ayuda",
        "menu_commands": "Comandos y Ayuda",
        "menu_about": "Acerca de RIFC",
        "menu_export_code": "Exportar a Código...",
        "about_title": "Acerca de RIFC",
        "about_text": """=============================================================================
RIFC (Rama's Instant Flow Chart)
Copyright (C) 2026 RamaTheSunGod

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Additional Term under GPLv3 Section 7(e):
Nothing in this license grants permissions to use the trade names, trademarks,
or service marks of the author ("RIFC", "Rama's Instant Flow Chart"), except
as required for reasonable and customary use in describing the origin of the
Software and reproducing the content of the logo ("icon.ico"). The logo asset
remains the copyright of the author and is provided under CC BY-ND 4.0.
=============================================================================""",
        "btn_preview": "Actualizar Vista Previa (Ctrl+Enter)",
        "btn_export": "Exportar Diagrama...",
        "pref_title": "Preferencias",
        "pref_theme": "Tema de la Interfaz:",
        "pref_style": "Estilo del Diagrama:",
        "pref_lang": "Idioma (Language):",
        "pref_colors": "Editar Colores del Estilo",
        "pref_btn_save": "Aplicar y Guardar",
        "color_bg": "Fondo",
        "color_edge": "Líneas",
        "color_text": "Texto",
        "color_io_fill": "Inicio/Fin Relleno",
        "color_io_stroke": "Inicio/Fin Borde",
        "color_box_fill": "Proceso Relleno",
        "color_box_stroke": "Proceso Borde",
        "color_dia_fill": "Decisión Relleno",
        "color_dia_stroke": "Decisión Borde",
        "msg_success": "Éxito",
        "msg_saved": "Proyecto guardado.",
        "msg_compiled": "¡Diagrama compilado con éxito!\\nGuardado en: {}",
        "msg_error": "Error",
        "msg_error_dep": "Para exportar a {} se requiere la librería 'cairosvg'.\\nInstálala con: pip install cairosvg",
        "color_picker_title": "Elegir Color para {}",
        "menu_templates": "Plantillas",
        "tpl_basic": "Básico",
        "tpl_state": "Máquina de estados con loops",
        "tpl_decision": "Decisión múltiple",
        "err_paren_miss": "Error de sintaxis: Faltan cerrar {} paréntesis ')'.",
        "err_paren_extra": "Error de sintaxis: Sobran {} paréntesis ')'.",
        "err_loop_miss_end": "Error de sintaxis: Falta cerrar un 'loopstart' con su 'loopend'.",
        "err_loop_extra_end": "Error de sintaxis: Hay un 'loopend' sin su correspondiente 'loopstart'.",
        "err_no_start": "Falta el nodo 'start(...)' en el diagrama.",
        "err_no_end": "Falta el nodo 'end(...)' en el diagrama.",
        "err_bad_jmp": "Error de sintaxis: Se intentó hacer un salto (jmp) hacia una etiqueta inexistente: '{}'",
        "help_text": (
            "Comandos Básicos de RIFC:\\n\\n"
            "- start(Texto): Comienza el diagrama (e.g. start(Inicio)).\\n"
            "- end(Texto): Termina el diagrama (e.g. end(Fin)).\\n"
            "- act(etiqueta opcional)(Descripción): Crea una caja de proceso.\\n"
            "- io(Descripción): Crea un paralelogramo (Input/Output).\\n"
            "- db(Descripción): Crea un cilindro (Base de datos).\\n"
            "- doc(Descripción): Crea un documento.\\n"
            "- If (condición)( If1 Si (act...) If2 No (act...) ): Crea decisión.\\n"
            "- loopstart(nombre): Inicia un ciclo.\\n"
            "- loopend(nombre)(condición): Finaliza el ciclo y vuelve al inicio.\\n"
            "- jmp(etiqueta): Salta a un proceso etiquetado.\\n\\n"
            "Nota: Se puede usar \\\\n dentro de los textos para crear múltiples líneas.\\n\\n"
            "Atajos:\\n"
            "- Ctrl+Enter: Actualiza la vista previa."
        )
    },
    "en": {
        "menu_file": "File",
        "menu_new": "New",
        "menu_open": "Open Project (.txt)",
        "menu_save": "Save Project (.txt)",
        "menu_prefs": "Preferences...",
        "menu_export": "Export Diagram...",
        "menu_edit": "Edit",
        "menu_copy": "Copy",
        "menu_paste": "Paste",
        "menu_cut": "Cut",
        "menu_sel_all": "Select All",
        "menu_help": "Help",
        "menu_commands": "Commands and Help",
        "menu_about": "About RIFC",
        "menu_export_code": "Export to Code...",
        "about_title": "About RIFC",
        "about_text": """=============================================================================
RIFC (Rama's Instant Flow Chart)
Copyright (C) 2026 RamaTheSunGod

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Additional Term under GPLv3 Section 7(e):
Nothing in this license grants permissions to use the trade names, trademarks,
or service marks of the author ("RIFC", "Rama's Instant Flow Chart"), except
as required for reasonable and customary use in describing the origin of the
Software and reproducing the content of the logo ("icon.ico"). The logo asset
remains the copyright of the author and is provided under CC BY-ND 4.0.
=============================================================================""",
        "btn_preview": "Update Preview (Ctrl+Enter)",
        "btn_export": "Export Diagram...",
        "pref_title": "Preferences",
        "pref_theme": "Interface Theme:",
        "pref_style": "Diagram Style:",
        "pref_lang": "Language (Idioma):",
        "pref_colors": "Edit Style Colors",
        "pref_btn_save": "Apply and Save",
        "color_bg": "Background",
        "color_edge": "Lines",
        "color_text": "Text",
        "color_io_fill": "Start/End Fill",
        "color_io_stroke": "Start/End Stroke",
        "color_box_fill": "Process Fill",
        "color_box_stroke": "Process Stroke",
        "color_dia_fill": "Decision Fill",
        "color_dia_stroke": "Decision Stroke",
        "msg_success": "Success",
        "msg_saved": "Project saved.",
        "msg_compiled": "Diagram compiled successfully!\\nSaved in: {}",
        "msg_error": "Error",
        "msg_error_dep": "To export to {} the 'cairosvg' library is required.\\nInstall it with: pip install cairosvg",
        "color_picker_title": "Choose Color for {}",
        "menu_templates": "Templates",
        "tpl_basic": "Basic",
        "tpl_state": "State machine with loops",
        "tpl_decision": "Multiple decision",
        "err_paren_miss": "Syntax Error: Missing {} closing parenthesis ')'.",
        "err_paren_extra": "Syntax Error: Found {} extra closing parenthesis ')'.",
        "err_loop_miss_end": "Syntax Error: Unclosed 'loopstart'. Missing corresponding 'loopend'.",
        "err_loop_extra_end": "Syntax Error: Found a 'loopend' without a preceding 'loopstart'.",
        "err_no_start": "Missing 'start(...)' node in diagram.",
        "err_no_end": "Missing 'end(...)' node in diagram.",
        "err_bad_jmp": "Syntax Error: Attempted a jump (jmp) to a non-existent label: '{}'",
        "help_text": (
            "RIFC Basic Commands:\\n\\n"
            "- start(Text): Starts the diagram (e.g. start(Start)).\\n"
            "- end(Text): Ends the diagram (e.g. end(End)).\\n"
            "- act(optional label)(Description): Creates a process box.\\n"
            "- io(Description): Creates a parallelogram (Input/Output).\\n"
            "- db(Description): Creates a cylinder (Database).\\n"
            "- doc(Description): Creates a document.\\n"
            "- If (condition)( If1 Yes (act...) If2 No (act...) ): Creates a decision.\\n"
            "- loopstart(name): Starts a loop.\\n"
            "- loopend(name)(condition): Ends the loop and goes back to start.\\n"
            "- jmp(label): Jumps to a labeled process.\\n\\n"
            "Note: You can use \\\\n inside texts to create multiple lines.\\n\\n"
            "Shortcuts:\\n"
            "- Ctrl+Enter: Updates the preview."
        )
    }
}

def t(key, lang=None):
    if not lang:
        lang = APP_CONFIG.get("lang", "en")
    return I18N.get(lang, I18N["en"]).get(key, key)

# --- Parser y Motor de Renderizado Nativo SVG ---
class NativeFlowCompiler:
    def __init__(self, code, config=None, lang="en"):
        self.raw_code = code
        self.config = config if config else DEFAULT_DIAGRAM_CONFIG.copy()
        self.lang = lang
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

    def validate_code(self):
        # Basic validation: unclosed parenthesis
        open_p = self.raw_code.count('(')
        close_p = self.raw_code.count(')')
        if open_p > close_p:
            raise ValueError(t("err_paren_miss", self.lang).format(open_p - close_p))
        elif close_p > open_p:
            raise ValueError(t("err_paren_extra", self.lang).format(close_p - open_p))
            
        # Basic validation: check loop closures
        starts = len(re.findall(r'(?i)\bloopstart\b', self.raw_code))
        ends = len(re.findall(r'(?i)\bloopend\b', self.raw_code))
        if starts > ends:
            raise ValueError(t("err_loop_miss_end", self.lang))
        elif ends > starts:
            raise ValueError(t("err_loop_extra_end", self.lang))

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
        # Unescape \n to actual newline
        block_tokens = [tok.replace("\\n", "\n") for tok in tokens[start:i-1]]
        return block_tokens, i

    def parse(self):
        self.validate_code()
        tokens = self.tokenize(self.raw_code)
        self.parse_sequence(tokens)
        
        if not self.has_inicio:
            raise ValueError(t("err_no_start", self.lang))
        if not self.has_fin:
            raise ValueError(t("err_no_end", self.lang))
        
        # Resolver jmps
        for src, target_label, *opt_lbl in self.pending_jmps:
            lbl = opt_lbl[0] if opt_lbl else ""
            if target_label in self.labels:
                self.edges.append({'from': src, 'to': self.labels[target_label], 'label': lbl, 'dashed': False})
            else:
                raise ValueError(t("err_bad_jmp", self.lang).format(target_label))

    def parse_sequence(self, tokens, current_source=None, current_loop_start=None):
        i = 0
        while i < len(tokens):
            tok = tokens[i]

            if tok.lower() == "start":
                block, next_i = self.extract_block(tokens, i + 1)
                start_text = " ".join(block) if block else "Start"
                i = next_i
                
                if not self.has_inicio:
                    nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': nid, 'type': 'oval', 'text': start_text, 'fill': self.config['inicio_fill'], 'stroke': self.config['inicio_stroke']})
                    if current_source: self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})
                    current_source = nid
                    self.has_inicio = True

            elif tok.lower() == "end":
                block, next_i = self.extract_block(tokens, i + 1)
                end_text = " ".join(block) if block else "End"
                i = next_i
                
                if not self.has_fin:
                    nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': nid, 'type': 'oval', 'text': end_text, 'fill': self.config['fin_fill'], 'stroke': self.config['fin_stroke']})
                    if current_source:
                        if isinstance(current_source, list):
                            for src in current_source:
                                self.edges.append({'from': src, 'to': nid, 'label': '', 'dashed': False})
                        else:
                            self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})
                    current_source = nid
                    self.has_fin = True

            elif tok.lower() == "loopstart":
                block, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                loop_name = " ".join(block)

                # Inject a merge node to serve as a definite target for the loop to return to
                merge_nid = f"n_{len(self.nodes)}"
                self.nodes.append({'id': merge_nid, 'type': 'merge', 'text': '', 'fill': 'none', 'stroke': 'none'})
                if current_source:
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.edges.append({'from': src, 'to': merge_nid, 'label': '', 'dashed': False})
                    else:
                        self.edges.append({'from': current_source, 'to': merge_nid, 'label': '', 'dashed': False})
                current_source = merge_nid
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
                    # Inject a merge node to collect all branches before looping back
                    merge_nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': merge_nid, 'type': 'merge', 'text': '', 'fill': 'none', 'stroke': 'none'})
                    
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.edges.append({'from': src, 'to': merge_nid, 'label': '', 'dashed': False})
                    else:
                        self.edges.append({'from': current_source, 'to': merge_nid, 'label': '', 'dashed': False})
                        
                    current_source = merge_nid
                    
                    target_node = self.loop_starts[loop_name]
                    if target_node is not None:
                        # Since target_node is now the merge node created exactly at loopstart, we can point directly to it
                        self.edges.append({'from': merge_nid, 'to': target_node, 'label': return_label, 'dashed': True})

            elif tok.lower() in ("act", "io", "db", "doc"):
                node_cmd = tok.lower()
                block1, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                if i < len(tokens) and tokens[i] == '(':
                    block2, next_i2 = self.extract_block(tokens, i)
                    label_name, action_text = " ".join(block1), " ".join(block2)
                    i = next_i2
                else:
                    label_name, action_text = None, " ".join(block1)

                nid = f"n_{len(self.nodes)}"
                
                # Map command to shape type
                shape_type = 'box'
                if node_cmd == 'io': shape_type = 'parallelogram'
                elif node_cmd == 'db': shape_type = 'cylinder'
                elif node_cmd == 'doc': shape_type = 'document'
                
                self.nodes.append({'id': nid, 'type': shape_type, 'text': action_text, 'fill': self.config['box_fill'], 'stroke': self.config['box_stroke']})
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
                if current_source:
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.pending_jmps.append((src, target_label))
                    else:
                        self.pending_jmps.append((current_source, target_label))
                current_source = None

            elif tok.lower() == "if":
                cond_block, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                
                # Check if next block is a second parenthesis, meaning the first was a label
                if i < len(tokens) and tokens[i] == '(':
                    branches_block_or_cond, next_i2 = self.extract_block(tokens, i)
                    # If there's a third parenthesis, we have: If (label)(cond)(branches)
                    if next_i2 < len(tokens) and tokens[next_i2] == '(':
                        branches_block_final, next_i3 = self.extract_block(tokens, next_i2)
                        label_name = " ".join(cond_block)
                        cond_text = " ".join(branches_block_or_cond)
                        branches_block = branches_block_final
                        i = next_i3
                    else:
                        label_name = None
                        cond_text = " ".join(cond_block)
                        branches_block = branches_block_or_cond
                        i = next_i2
                else:
                    label_name = None
                    cond_text = " ".join(cond_block)
                    branches_block = [] # Error case really

                nid = f"n_{len(self.nodes)}"
                if label_name:
                    self.labels[label_name] = nid
                self.nodes.append({'id': nid, 'type': 'diamond', 'text': cond_text, 'fill': self.config['diamond_fill'], 'stroke': self.config['diamond_stroke']})
                if current_source:
                    if isinstance(current_source, list):
                        for src in current_source:
                            self.edges.append({'from': src, 'to': nid, 'label': '', 'dashed': False})
                    else:
                        self.edges.append({'from': current_source, 'to': nid, 'label': '', 'dashed': False})

                # We already extracted branches_block above in the new if parsing logic.
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
                if first_tok.lower() == "jmp" and len(branch_actions) <= 4:
                    # Simple jmp inside a branch (no other actions)
                    lbl_block, _ = self.extract_block(branch_actions, 1)
                    target = " ".join(lbl_block)
                    self.pending_jmps.append((cond_node_id, target, branch_label))
                    # We inject a dummy merge node for the layout to know there was a branch here.
                    dummy_nid = f"n_{len(self.nodes)}"
                    self.nodes.append({'id': dummy_nid, 'type': 'merge', 'text': '', 'fill': 'none', 'stroke': 'none'})
                    self.edges.append({'from': cond_node_id, 'to': dummy_nid, 'label': branch_label, 'dashed': False})
                    ends.append(dummy_nid)
                else:
                    target_id_preview = f"n_{len(self.nodes)}"
                    branch_end = self.parse_sequence(branch_actions, current_source=None)
                    
                    if branch_actions:
                        self.edges.append({'from': cond_node_id, 'to': target_id_preview, 'label': branch_label, 'dashed': False})
                    else:
                        # Empty branch
                        self.nodes.append({'id': target_id_preview, 'type': 'merge', 'text': '', 'fill': 'none', 'stroke': 'none'})
                        self.edges.append({'from': cond_node_id, 'to': target_id_preview, 'label': branch_label, 'dashed': False})
                        branch_end = target_id_preview
                    
                    if branch_end:
                        if isinstance(branch_end, list):
                            ends.extend(branch_end)
                        else:
                            ends.append(branch_end)
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

        # Deterministic Branch Width Calculation (Bottom-Up)
        memo_width = {}
        def get_branch_width(node_id, visited_bw):
            if node_id in memo_width:
                return memo_width[node_id]
            if node_id in visited_bw:
                return 0 # loop detected
            
            visited_bw.add(node_id)
            
            # Identify forward children
            forward_children = [child for child in adj.get(node_id, []) if levels.get(child, 0) > levels.get(node_id, 0)]
            
            if not forward_children:
                w = 180 # Minimum base width for a single block
                memo_width[node_id] = w
                return w
            
            # The width of this subtree is the sum of its children's widths (if > 1) or just the child's width
            if len(forward_children) > 1:
                total_w = sum(get_branch_width(child, set(visited_bw)) for child in forward_children)
                w = max(180 * len(forward_children), total_w)
            else:
                child = forward_children[0]
                # If the child is a merge node, it belongs to the parent's level context logically, 
                # so we don't count its full width as uniquely belonging to this branch if it has other parents.
                forward_incoming = [src for src in incoming.get(child, []) if levels.get(src, 0) < levels.get(child, 0)]
                if len(forward_incoming) > 1 or node_coords.get(child, {}).get('type', '') == 'merge':
                    w = 180
                else:
                    w = get_branch_width(child, set(visited_bw))
            
            memo_width[node_id] = w
            return w

        # Assign X coordinates by spreading branches based on their required widths
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
                # Spread based on calculated branch widths
                total_spread = sum(get_branch_width(c, set()) for c in forward_children)
                current_offset = - (total_spread / 2)
                
                for i, child_id in enumerate(forward_children):
                    bw = get_branch_width(child_id, set())
                    child_x = curr_x + current_offset + (bw / 2)
                    current_offset += bw
                    queue.append((child_id, child_x))
            elif len(forward_children) == 1:
                child = forward_children[0]
                # Check if child is a merge point
                child_type = node_coords.get(child, {}).get('type', '')
                forward_incoming = [src for src in incoming.get(child, []) if levels.get(src, 0) < levels.get(child, 0)]
                
                if len(forward_incoming) > 1 or child_type == 'merge':
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
            f'  .edge-dashed {{ stroke: {ec}; stroke-width: 2; stroke-dasharray: 5,5; fill: none; marker-end: url(#arrow); }}',
            f'  .edge-no-arrow {{ stroke: {ec}; stroke-width: 2; fill: none; }}',
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
                
                is_src_merge = p1.get('type') == 'merge'
                is_target_merge = p2.get('type') == 'merge'

                # Ajuste básico de coordenadas verticales
                offset_y1 = 4 if is_src_merge else 25
                offset_y2 = 4 if is_target_merge else 25
                
                y1 = p1['y'] + offset_y1 if p1['y'] < p2['y'] else p1['y'] - offset_y1
                y2 = p2['y'] - offset_y2 if p1['y'] < p2['y'] else p2['y'] + offset_y2
                x1, x2 = p1['x'], p2['x']

                # Check for backward jump (loop) based on Y coordinates
                is_backward = p1['y'] >= p2['y']
                y2 = p2['y'] - (offset_y2 + 15) if is_backward else y2
                
                # Detect if the jump bypasses levels directly downwards
                is_long_jump = not is_backward and abs(p1['y'] - p2['y']) > 150 # roughly more than one spacing_y

                edge_cls = "edge-no-arrow" if is_target_merge else "edge"
                
                if is_backward:
                    # Curve for backward loops: go right, up, and back left to point into the incoming stream
                    tgt = edge['to']
                    backward_targets[tgt] = backward_targets.get(tgt, 0) + 1
                    
                    # Calculate max X to clear nodes between p2['y'] and p1['y']
                    max_inter_x = max([node_coords[nid]['x'] + max(120, len(self.nodes[node_coords[nid]['idx']]['text']) * 8)/2 
                                      for nid in node_coords 
                                      if p2['y'] - 50 <= node_coords[nid]['y'] <= p1['y'] + 50], default=x1)
                    
                    # Ensure it clears the max block width plus padding
                    control_x = max(x1 + 150, max_inter_x + 60 + (backward_targets[tgt] * 30))

                    path_d = f"M {x1+40} {p1['y']} C {control_x} {p1['y']}, {control_x} {p2['y']-60}, {x2} {y2}"
                    svg_lines.append(f'<path d="{path_d}" class="{edge_cls}" fill="none"/>')
                    if edge['label']:
                        svg_lines.append(f'<text x="{control_x - 30}" y="{(p1["y"]+p2["y"])/2}" class="text-label" font-weight="bold">{edge["label"]}</text>')
                elif is_long_jump and x1 == x2:
                    # Salto largo hacia adelante que cruzaría los bloques, curvar por la izquierda
                    path_d = f"M {x1-40} {p1['y']} C {x1-150} {p1['y']}, {x2-150} {p2['y']}, {x2-40} {p2['y']}"
                    svg_lines.append(f'<path d="{path_d}" class="{edge_cls}" fill="none"/>')
                    if edge['label']:
                        svg_lines.append(f'<text x="{x1-110}" y="{(p1["y"]+p2["y"])/2}" class="text-label" font-weight="bold">{edge["label"]}</text>')
                else:
                    # Línea recta normal o cruzada
                    if x1 != x2 and not is_backward:
                        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{edge_cls}"/>')
                        if edge['label']:
                            mid_x, mid_y = x1 + (x2-x1)*0.5, y1 + (y2-y1)*0.5
                            svg_lines.append(f'<text x="{mid_x}" y="{mid_y}" class="text-label" font-weight="bold">{edge["label"]}</text>')
                    else:
                        svg_lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{edge_cls}"/>')
                        if edge['label']:
                            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                            svg_lines.append(f'<text x="{mid_x}" y="{mid_y}" class="text-label" font-weight="bold">{edge["label"]}</text>')

        # Draw labels last so they appear on top
        def create_multiline_svg_text(x, y, text_str, font_weight="normal"):
            lines = text_str.split("\n")
            line_height = 14
            start_y = y - (len(lines) - 1) * (line_height / 2)
            markup = []
            for i, line in enumerate(lines):
                markup.append(f'<tspan x="{x}" y="{start_y + i * line_height}" font-weight="{font_weight}">{line}</tspan>')
            return f'<text x="{x}" y="{y}">{"".join(markup)}</text>'

        for node in self.nodes:
            coords = node_coords[node['id']]
            x, y = coords['x'], coords['y']
            fill = node['fill']
            
            # Auto-resizing widths based on text length (approx. 7px per char)
            # Find max line length for multiline
            max_len = max([len(line) for line in node["text"].split("\n")], default=0)
            base_width = max(120, max_len * 8)
            hw = base_width / 2

            if node['type'] == 'box':
                svg_lines.append(f'<rect x="{x-hw}" y="{y-25}" width="{base_width}" height="50" class="box" fill="{fill}"/>')
                svg_lines.append(create_multiline_svg_text(x, y, node["text"]))
            elif node['type'] == 'oval':
                cls = "oval-inicio" if node["text"].lower() == "inicio" else "oval-fin"
                svg_lines.append(f'<rect x="{x-hw}" y="{y-20}" width="{base_width}" height="40" rx="20" ry="20" class="{cls}" fill="{fill}"/>')
                svg_lines.append(create_multiline_svg_text(x, y, node["text"], "bold"))
            elif node['type'] == 'diamond':
                out_degree = coords.get('out_degree', 2)
                # Diamond width needs to accommodate text plus branch spreading
                d_width = max(hw + 20, 80 + (max(0, out_degree - 2) * 20))
                points = f"{x},{y-30} {x+d_width},{y} {x},{y+30} {x-d_width},{y}"
                svg_lines.append(f'<polygon points="{points}" class="diamond" fill="{fill}"/>')
                svg_lines.append(create_multiline_svg_text(x, y, node["text"]))
            elif node['type'] == 'parallelogram':
                points = f"{x-hw+20},{y-25} {x+hw},{y-25} {x+hw-20},{y+25} {x-hw},{y+25}"
                svg_lines.append(f'<polygon points="{points}" stroke="{self.config["box_stroke"]}" stroke-width="2" fill="{fill}"/>')
                svg_lines.append(create_multiline_svg_text(x, y, node["text"]))
            elif node['type'] == 'document':
                path_d = f"M {x-hw} {y-25} L {x+hw} {y-25} L {x+hw} {y+15} Q {x+hw/2} {y+35} {x} {y+15} T {x-hw} {y+15} Z"
                svg_lines.append(f'<path d="{path_d}" stroke="{self.config["box_stroke"]}" stroke-width="2" fill="{fill}"/>')
                svg_lines.append(create_multiline_svg_text(x, y-5, node["text"]))
            elif node['type'] == 'cylinder':
                ry = 10
                path_d = f"M {x-hw} {y-25+ry} L {x-hw} {y+25-ry} A {hw} {ry} 0 0 0 {x+hw} {y+25-ry} L {x+hw} {y-25+ry} A {hw} {ry} 0 0 1 {x-hw} {y-25+ry} Z"
                svg_lines.append(f'<path d="{path_d}" stroke="{self.config["box_stroke"]}" stroke-width="2" fill="{fill}"/>')
                # Top ellipse
                svg_lines.append(f'<ellipse cx="{x}" cy="{y-25+ry}" rx="{hw}" ry="{ry}" stroke="{self.config["box_stroke"]}" stroke-width="2" fill="{fill}"/>')
                svg_lines.append(create_multiline_svg_text(x, y+5, node["text"]))
            elif node['type'] == 'merge':
                svg_lines.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{self.config["edge_color"]}" />')

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
        def create_arrow(x1, y1, x2, y2, color, arrow_end=True, dash=None):
            arrow_param = tk.LAST if arrow_end else tk.NONE
            canvas.create_line(x1, y1, x2, y2, arrow=arrow_param, fill=color, width=2, dash=dash)
            
        def create_curved_arrow(x1, y1, cx1, cy1, cx2, cy2, x2, y2, color, arrow_end=True, dash=None):
            steps = 20
            points = []
            for i in range(steps + 1):
                t = i / steps
                px = (1-t)**3 * x1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * x2
                py = (1-t)**3 * y1 + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * y2
                points.extend([px, py])
            arrow_param = tk.LAST if arrow_end else tk.NONE
            canvas.create_line(points, arrow=arrow_param, fill=color, width=2, dash=dash, smooth=True)

        def draw_label(x, y, text):
            bg_id = canvas.create_rectangle(0, 0, 0, 0, fill=bg, outline="")
            text_id = canvas.create_text(x, y, text=text, fill=tc, font=(font, 10, "bold"), justify=tk.CENTER)
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
                
                is_src_merge = p1.get('type') == 'merge'
                is_target_merge = p2.get('type') == 'merge'
                
                offset_y1 = 4 if is_src_merge else 25
                offset_y2 = 4 if is_target_merge else 25

                y1 = p1['y'] + offset_y1 if p1['y'] < p2['y'] else p1['y'] - offset_y1
                y2 = p2['y'] - offset_y2 if p1['y'] < p2['y'] else p2['y'] + offset_y2
                x1, x2 = p1['x'], p2['x']

                # Check for backward jump (loop) based on Y coordinates
                is_backward = p1['y'] >= p2['y']
                dash_style = None # We no longer use dashed style for loops per user request
                
                # If backward, aim at the TOP of the target node (where the incoming arrow would be)
                # target node is p2. Arrow points to p2['y'] - 25 (its top border)
                # But to point "to the incoming arrow", we point slightly above it
                y2 = p2['y'] - (offset_y2 + 15) if is_backward else y2

                # Detect if the jump bypasses levels directly downwards
                is_long_jump = not is_backward and abs(p1['y'] - p2['y']) > 150 # roughly more than one spacing_y

                if is_backward:
                    tgt = edge['to']
                    backward_targets[tgt] = backward_targets.get(tgt, 0) + 1
                    
                    # Calculate max X to clear nodes between p2['y'] and p1['y']
                    max_inter_x = max([node_coords[nid]['x'] + max(120, len(self.nodes[node_coords[nid]['idx']]['text']) * 8)/2 
                                      for nid in node_coords 
                                      if p2['y'] - 50 <= node_coords[nid]['y'] <= p1['y'] + 50], default=x1)
                    
                    control_x = max(x1 + 150, max_inter_x + 60 + (backward_targets[tgt] * 30))
                    
                    # Curve for backward loops: go right, up, and back left to point into the incoming stream
                    create_curved_arrow(x1+40, p1['y'], control_x, p1['y'], control_x, p2['y']-60, x2, y2, ec, arrow_end=not is_target_merge, dash=dash_style)
                    if edge['label']:
                        edge_labels_buffer.append((control_x - 30, (p1["y"]+p2["y"])/2, edge["label"]))
                elif is_long_jump and x1 == x2:
                    # Salto largo hacia adelante que cruzaría los bloques, curvar por la izquierda
                    create_curved_arrow(x1-40, p1['y'], x1-150, p1['y'], x2-150, p2['y'], x2-40, p2['y'], ec, arrow_end=not is_target_merge, dash=dash_style)
                    if edge['label']:
                        edge_labels_buffer.append((x1-110, (p1["y"]+p2["y"])/2, edge["label"]))
                else:
                    create_arrow(x1, y1, x2, y2, ec, arrow_end=not is_target_merge, dash=dash_style)
                    if edge['label']:
                        if x1 != x2 and not is_backward:
                            mid_x, mid_y = x1 + (x2-x1)*0.5, y1 + (y2-y1)*0.5
                            edge_labels_buffer.append((mid_x, mid_y, edge["label"]))
                        else:
                            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                            edge_labels_buffer.append((mid_x, mid_y, edge["label"]))

        # Now actually draw the labels that were buffered
        for x, y, label in edge_labels_buffer:
            draw_label(x, y, label)

        for node in self.nodes:
            coords = node_coords[node['id']]
            x, y = coords['x'], coords['y']
            fill = node['fill']
            
            text_len = len(node["text"])
            base_width = max(120, text_len * 8)
            hw = base_width / 2

            if node['type'] == 'box':
                canvas.create_rectangle(x-hw, y-25, x+hw, y+25, fill=fill, outline=self.config["box_stroke"], width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10), fill=tc, justify=tk.CENTER)
            elif node['type'] == 'oval':
                stroke = self.config["inicio_stroke"] if node["text"].lower() == "inicio" else self.config["fin_stroke"]
                # Use a rounded rectangle simulation via oval coords or use actual rounded rect if possible. Canvas oval bounds are bounding box.
                canvas.create_oval(x-hw, y-20, x+hw, y+20, fill=fill, outline=stroke, width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10, "bold"), fill=tc, justify=tk.CENTER)
            elif node['type'] == 'diamond':
                out_degree = coords.get('out_degree', 2)
                d_width = max(hw + 20, 80 + (max(0, out_degree - 2) * 20))
                points = [x, y-30, x+d_width, y, x, y+30, x-d_width, y]
                canvas.create_polygon(points, fill=fill, outline=self.config["diamond_stroke"], width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10), fill=tc, justify=tk.CENTER)
            elif node['type'] == 'parallelogram':
                points = [x-hw+20, y-25, x+hw, y-25, x+hw-20, y+25, x-hw, y+25]
                canvas.create_polygon(points, fill=fill, outline=self.config["box_stroke"], width=2)
                canvas.create_text(x, y, text=node["text"], font=(font, 10), fill=tc, justify=tk.CENTER)
            elif node['type'] == 'document':
                # Since Tkinter doesn't have an easy native SVG Q/T spline equivalent, we approximate with points
                points = [x-hw, y-25, x+hw, y-25, x+hw, y+15]
                # Q to center
                for i in range(1, 10):
                    t = i / 10.0
                    px = (1-t)**2 * (x+hw) + 2*(1-t)*t * (x+hw/2) + t**2 * x
                    py = (1-t)**2 * (y+15) + 2*(1-t)*t * (y+35) + t**2 * (y+15)
                    points.extend([px, py])
                # T to left
                for i in range(1, 10):
                    t = i / 10.0
                    px = (1-t)**2 * x + 2*(1-t)*t * (x-hw/2) + t**2 * (x-hw)
                    py = (1-t)**2 * (y+15) + 2*(1-t)*t * (y-5) + t**2 * (y+15)
                    points.extend([px, py])
                canvas.create_polygon(points, fill=fill, outline=self.config["box_stroke"], width=2)
                canvas.create_text(x, y-5, text=node["text"], font=(font, 10), fill=tc, justify=tk.CENTER)
            elif node['type'] == 'cylinder':
                ry = 10
                # Base body (rectangle)
                canvas.create_rectangle(x-hw, y-25+ry, x+hw, y+25-ry, fill=fill, outline="")
                # Left / Right lines
                canvas.create_line(x-hw, y-25+ry, x-hw, y+25-ry, fill=self.config["box_stroke"], width=2)
                canvas.create_line(x+hw, y-25+ry, x+hw, y+25-ry, fill=self.config["box_stroke"], width=2)
                # Bottom arc
                canvas.create_arc(x-hw, y+25-ry*2, x+hw, y+25, start=180, extent=180, style=tk.ARC, outline=self.config["box_stroke"], width=2)
                canvas.create_arc(x-hw, y+25-ry*2, x+hw, y+25, start=180, extent=180, style=tk.CHORD, fill=fill, outline="")
                # Top oval
                canvas.create_oval(x-hw, y-25, x+hw, y-25+ry*2, fill=fill, outline=self.config["box_stroke"], width=2)
                
                canvas.create_text(x, y+5, text=node["text"], font=(font, 10), fill=tc, justify=tk.CENTER)
            elif node['type'] == 'merge':
                canvas.create_oval(x-4, y-4, x+4, y+4, fill=self.config["edge_color"], outline="")
# --- Interfaz Gráfica de Escritorio (GUI) ---
class RIFCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RIFC (Rama's Instant Flow Chart)")
        self.root.geometry("1200x700")
        
        # Intentar cargar un icono personalizado si existe
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        if os.path.exists(icon_path):
            try:
                icon_img = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, icon_img)
            except Exception:
                try:
                    self.root.iconbitmap(icon_path)
                except Exception:
                    pass
        
        # State
        self.current_preset = APP_CONFIG["preset"]
        if self.current_preset not in PRESETS:
            self.current_preset = "Clásico"
        self.app_theme = APP_CONFIG["theme"]
        self.app_lang = APP_CONFIG["lang"]

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=5)

        self.build_menus()

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

        # Zoom support
        self.zoom_level = 1.0
        self.canvas.bind("<Control-MouseWheel>", self.on_zoom)
        self.canvas.bind("<Control-Button-4>", self.on_zoom)
        self.canvas.bind("<Control-Button-5>", self.on_zoom)

        # Keep a reference to the image to prevent garbage collection
        self.preview_image = None
        
        # Bottom Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_preview = tk.Button(btn_frame, text=t("btn_preview", self.app_lang), bg="#4dabf7", fg="white", font=("Helvetica", 10, "bold"), command=self.actualizar_preview, relief=tk.FLAT)
        self.btn_preview.pack(side="left", padx=5)

        self.btn_export = tk.Button(btn_frame, text=t("btn_export", self.app_lang), bg="#40c057", fg="white", font=("Helvetica", 10, "bold"), command=self.exportar_diagrama, relief=tk.FLAT)
        self.btn_export.pack(side="left", padx=5)

        # Configure tags for syntax highlighting
        self.text_editor.tag_configure("keyword", foreground="#c678dd", font=("Consolas", 12, "bold"))
        self.text_editor.tag_configure("bracket", foreground="#61afef")
        self.text_editor.tag_configure("control", foreground="#e5c07b", font=("Consolas", 12, "bold"))

        # Bindings
        self.text_editor.bind('<Control-Return>', self.handle_ctrl_enter)
        self.text_editor.bind("<KeyRelease>", self.highlight_syntax)
        self.text_editor.bind("(", self.auto_close_paren)
        
        # Initial apply theme, highlight and preview
        self.aplicar_tema()
        
        # Load default basic template on startup
        self.load_template('basic')

    def build_menus(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=t("menu_new", self.app_lang), command=self.nuevo_proyecto)
        
        template_menu = tk.Menu(file_menu, tearoff=0)
        template_menu.add_command(label=t("tpl_basic", self.app_lang), command=lambda: self.load_template('basic'))
        template_menu.add_command(label=t("tpl_state", self.app_lang), command=lambda: self.load_template('state'))
        template_menu.add_command(label=t("tpl_decision", self.app_lang), command=lambda: self.load_template('decision'))
        file_menu.add_cascade(label=t("menu_templates", self.app_lang), menu=template_menu)
        
        file_menu.add_command(label=t("menu_open", self.app_lang), command=self.abrir_proyecto)
        file_menu.add_command(label=t("menu_save", self.app_lang), command=self.guardar_proyecto)
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_prefs", self.app_lang), command=self.abrir_preferencias)
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_export", self.app_lang), command=self.exportar_diagrama)
        file_menu.add_command(label=t("menu_export_code", self.app_lang), command=self.exportar_codigo)
        menubar.add_cascade(label=t("menu_file", self.app_lang), menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label=t("menu_copy", self.app_lang), command=lambda: self.root.focus_get().event_generate('<<Copy>>'))
        edit_menu.add_command(label=t("menu_paste", self.app_lang), command=lambda: self.root.focus_get().event_generate('<<Paste>>'))
        edit_menu.add_command(label=t("menu_cut", self.app_lang), command=lambda: self.root.focus_get().event_generate('<<Cut>>'))
        edit_menu.add_separator()
        edit_menu.add_command(label=t("menu_sel_all", self.app_lang), command=self.seleccionar_todo)
        menubar.add_cascade(label=t("menu_edit", self.app_lang), menu=edit_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label=t("menu_commands", self.app_lang), command=self.mostrar_ayuda)
        help_menu.add_command(label=t("menu_about", self.app_lang), command=self.mostrar_about)
        menubar.add_cascade(label=t("menu_help", self.app_lang), menu=help_menu)

        self.root.config(menu=menubar)

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
        keywords = r'\b(start|end|act|io|db|doc|If|loopstart|loopend|jmp|Si|No)\b'
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
            
    def on_zoom(self, event):
        # Handle zoom in / out
        if event.num == 4 or getattr(event, "delta", 0) > 0:
            scale_factor = 1.1
        elif event.num == 5 or getattr(event, "delta", 0) < 0:
            scale_factor = 0.9
        else:
            return

        # Limit zoom
        if (self.zoom_level < 0.2 and scale_factor < 1.0) or (self.zoom_level > 5.0 and scale_factor > 1.0):
            return

        self.zoom_level *= scale_factor
        self.canvas.scale("all", 0, 0, scale_factor, scale_factor)
        
        # Scale fonts
        for item in self.canvas.find_all():
            if self.canvas.type(item) == "text":
                current_font = self.canvas.itemcget(item, "font")
                # Parse font to update size (e.g., 'Helvetica 12' or 'Helvetica 12 bold')
                font_parts = current_font.split()
                if len(font_parts) >= 2:
                    try:
                        base_size = float(font_parts[1])
                        new_size = max(1, int(base_size * scale_factor))
                        new_font = f"{font_parts[0]} {new_size} {' '.join(font_parts[2:])}"
                        self.canvas.itemconfig(item, font=new_font)
                    except ValueError:
                        pass
        
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def handle_ctrl_enter(self, event):
        self.actualizar_preview()
        return "break"

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
            compiler = NativeFlowCompiler(codigo, config, self.app_lang)
            compiler.draw_on_canvas(self.canvas)
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(0,0,0,0))
            self.canvas.create_text(20, 20, text=f"⚠️ {e}", anchor="nw", fill="#e74c3c", font=("Helvetica", 11, "bold"))
            
        # Reset zoom
        self.zoom_level = 1.0
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def seleccionar_todo(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        return 'break'
        
    def mostrar_ayuda(self):
        ayuda_texto = t("help_text", self.app_lang)
        messagebox.showinfo(t("menu_commands", self.app_lang), ayuda_texto)
        
    def mostrar_about(self):
        about_win = tk.Toplevel(self.root)
        about_win.title(t("about_title", self.app_lang))
        about_win.geometry("700x550")
        about_win.transient(self.root)
        about_win.grab_set()
        
        text_widget = tk.Text(about_win, wrap="word", font=("Courier", 10), bg="#f5f5f5")
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", t("about_text", self.app_lang))
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(about_win, text="OK", command=about_win.destroy).pack(pady=10)

    def load_template(self, tpl_type):
        self.text_editor.delete("1.0", tk.END)
        base = ""
        if tpl_type == "basic":
            base = """start(Inicio)

act(Paso 1)(Primer proceso)
act(Paso 2)(Segundo proceso)
io(Resultado)

end(Fin)"""
        elif tpl_type == "state":
            base = """start(Start)

loopstart(label:myloop)
    act(label:read)(Read sensor)
    
    If (active sensor?)(
        If1 Yes ( act(Read) )
        If2 No ( act(Turn off) jmp(label:read) )
        If3 Maybe ( act(Failure Mode) )
    )
loopend(label:myloop)(5 times)

io(Export data)
db(Save in database)
doc(Archive)

end(End)"""
        elif tpl_type == "decision":
            base = """start(Inicio)

act(Evaluar estado)

If (Estado actual)(
    If1 Alto ( act(Detener) )
    If2 Medio ( act(Precaución) )
    If3 Bajo ( act(Continuar) )
)

act(Guardar registro)

end(Fin)"""

        self.text_editor.insert("1.0", base)
        self.highlight_syntax()
        self.actualizar_preview()

    def nuevo_proyecto(self):
        self.load_template('basic')

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
            messagebox.showinfo(t("msg_success", self.app_lang), t("msg_saved", self.app_lang))

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
        lang = self.app_lang
        pref_win = tk.Toplevel(self.root)
        pref_win.title(t("pref_title", lang))
        pref_win.geometry("350x600")
        pref_win.transient(self.root)
        pref_win.grab_set()

        ttk.Label(pref_win, text=t("pref_theme", lang)).pack(pady=(10, 0))
        theme_combo = ttk.Combobox(pref_win, values=["Oscuro", "Claro"], state="readonly")
        theme_combo.set(self.app_theme)
        theme_combo.pack(pady=5)

        ttk.Label(pref_win, text=t("pref_lang", lang)).pack(pady=(10, 0))
        lang_combo = ttk.Combobox(pref_win, values=["en", "es"], state="readonly")
        lang_combo.set(self.app_lang)
        lang_combo.pack(pady=5)

        ttk.Label(pref_win, text=t("pref_style", lang)).pack(pady=(10, 0))
        preset_combo = ttk.Combobox(pref_win, values=list(PRESETS.keys()), state="readonly")
        preset_combo.set(self.current_preset)
        preset_combo.pack(pady=5)
        
        # Color customization frame
        color_frame = ttk.LabelFrame(pref_win, text=t("pref_colors", lang))
        color_frame.pack(fill="x", padx=20, pady=10)
        
        colors = {
            "bg_color": t("color_bg", lang),
            "edge_color": t("color_edge", lang),
            "text_color": t("color_text", lang),
            "inicio_fill": t("color_io_fill", lang),
            "inicio_stroke": t("color_io_stroke", lang),
            "box_fill": t("color_box_fill", lang),
            "box_stroke": t("color_box_stroke", lang),
            "diamond_fill": t("color_dia_fill", lang),
            "diamond_stroke": t("color_dia_stroke", lang)
        }
        color_btns = {}
        
        def pick_color(key):
            if preset_combo.get() != "Personalizado":
                return
            curr = PRESETS[preset_combo.get()][key]
            c = colorchooser.askcolor(title=t("color_picker_title", lang).format(colors[key]), color=curr)
            if c[1]:
                PRESETS[preset_combo.get()][key] = c[1]
                if key == "inicio_fill":
                    PRESETS[preset_combo.get()]["fin_fill"] = c[1]
                if key == "inicio_stroke":
                    PRESETS[preset_combo.get()]["fin_stroke"] = c[1]
                color_btns[key].config(bg=c[1])

        for k, label in colors.items():
            f = tk.Frame(color_frame)
            f.pack(fill="x", pady=2, padx=5)
            ttk.Label(f, text=label).pack(side="left")
            b = tk.Button(f, width=4, bg=PRESETS[self.current_preset][k], command=lambda k=k: pick_color(k))
            b.pack(side="right")
            color_btns[k] = b

        def update_ui(e=None):
            is_custom = preset_combo.get() == "Personalizado"
            for k in colors:
                color_btns[k].config(bg=PRESETS[preset_combo.get()][k], state=tk.NORMAL if is_custom else tk.DISABLED)
                
        preset_combo.bind("<<ComboboxSelected>>", update_ui)
        update_ui()

        def save_prefs():
            self.app_theme = theme_combo.get()
            self.current_preset = preset_combo.get()
            
            new_lang = lang_combo.get()
            lang_changed = (self.app_lang != new_lang)
            self.app_lang = new_lang
            
            # Save configuration
            APP_CONFIG["theme"] = self.app_theme
            APP_CONFIG["preset"] = self.current_preset
            APP_CONFIG["lang"] = self.app_lang
            save_app_config(APP_CONFIG)
            save_presets(PRESETS)
            
            self.aplicar_tema()
            self.actualizar_preview()
            
            if lang_changed:
                self.build_menus()
                self.btn_preview.config(text=t("btn_preview", self.app_lang))
                self.btn_export.config(text=t("btn_export", self.app_lang))
                
            pref_win.destroy()

        ttk.Button(pref_win, text=t("pref_btn_save", lang), command=save_prefs).pack(pady=20)

    def exportar_codigo(self):
        codigo = self.text_editor.get("1.0", tk.END)
        if not codigo.strip():
            return
            
        win = tk.Toplevel(self.root)
        win.title(t("menu_export_code", self.app_lang))
        win.geometry("600x500")
        win.transient(self.root)
        
        top_frame = ttk.Frame(win)
        top_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(top_frame, text="Language: ").pack(side="left")
        lang_combo = ttk.Combobox(top_frame, values=["Python", "JavaScript"], state="readonly")
        lang_combo.set("Python")
        lang_combo.pack(side="left", padx=10)
        
        text_preview = tk.Text(win, wrap="none", font=("Consolas", 11), bg="#282c34", fg="#abb2bf")
        text_preview.pack(expand=True, fill="both", padx=10)
        
        def update_preview(e=None):
            try:
                cg = CodeGenerator(codigo, lang_combo.get())
                gen = cg.generate()
                text_preview.delete("1.0", tk.END)
                text_preview.insert("1.0", gen)
            except Exception as ex:
                text_preview.delete("1.0", tk.END)
                text_preview.insert("1.0", f"Error:\n{ex}")
                
        lang_combo.bind("<<ComboboxSelected>>", update_preview)
        update_preview()
        
        def save_code():
            ext = ".py" if lang_combo.get() == "Python" else ".js"
            filepath = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(f"{lang_combo.get()} file", f"*{ext}")])
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(text_preview.get("1.0", tk.END))
                messagebox.showinfo(t("msg_success", self.app_lang), t("msg_saved", self.app_lang))
                win.destroy()
                
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(btn_frame, text=t("menu_save", self.app_lang), command=save_code).pack(side="right")

    def exportar_diagrama(self):
        codigo = self.text_editor.get("1.0", tk.END)
        if not codigo.strip():
            return
        filetypes = [("Archivo SVG", "*.svg"), ("Archivo PNG", "*.png"), ("Archivo PDF", "*.pdf")]
        filepath = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=filetypes)
        if filepath:
            ext = os.path.splitext(filepath)[1].lower()
            if ext in [".png", ".pdf"] and not HAS_CAIROSVG:
                messagebox.showerror(t("msg_error", self.app_lang), t("msg_error_dep", self.app_lang).format(ext))
                return
            try:
                config = PRESETS[self.current_preset].copy()
                compiler = NativeFlowCompiler(codigo, config, self.app_lang)
                
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
                    
                messagebox.showinfo(t("msg_success", self.app_lang), t("msg_compiled", self.app_lang).format(filepath))
            except Exception as e:
                messagebox.showerror(t("msg_error", self.app_lang), f"{e}")

import re

class CodeGenerator:
    def __init__(self, raw_code, language="python"):
        self.raw_code = raw_code
        self.language = language.lower()
        self.functions = set()
        self.main_flow = []

    def sanitize_func_name(self, text):
        # Transforma "Mi Función!" a "mi_funcion"
        text = text.lower()
        text = re.sub(r'[^a-z0-9_]', '_', text)
        text = re.sub(r'_+', '_', text)
        return text.strip('_')

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
        block_tokens = [tok.replace("\\n", "\n") for tok in tokens[start:i-1]]
        return block_tokens, i

    def generate(self):
        tokens = self.tokenize(self.raw_code)
        self.main_flow = self.parse_sequence(tokens, indent_level=1 if self.language == "python" else 1)
        return self.assemble_code()

    def parse_sequence(self, tokens, indent_level=0):
        flow = []
        i = 0
        indent = "    " * indent_level

        while i < len(tokens):
            tok = tokens[i]

            if tok.lower() in ("start", "end"):
                _, i = self.extract_block(tokens, i + 1)

            elif tok.lower() in ("act", "io", "db", "doc"):
                block1, next_i = self.extract_block(tokens, i + 1)
                i = next_i
                if i < len(tokens) and tokens[i] == '(':
                    block2, next_i2 = self.extract_block(tokens, i)
                    label_name = " ".join(block1)
                    action_text = " ".join(block2)
                    i = next_i2
                else:
                    action_text = " ".join(block1)

                func_name = self.sanitize_func_name(action_text)
                if not func_name: func_name = "do_action"
                self.functions.add((func_name, action_text))
                
                if self.language == "python":
                    flow.append(f"{indent}{func_name}()")
                elif self.language == "javascript":
                    flow.append(f"{indent}{func_name}();")

            elif tok.lower() == "loopstart":
                block, i = self.extract_block(tokens, i + 1)
                loop_name = " ".join(block)
                if self.language == "python":
                    flow.append(f"{indent}while True: # TODO: Definir condición para {loop_name}")
                elif self.language == "javascript":
                    flow.append(f"{indent}while (true) {{ // TODO: Definir condición para {loop_name}")

                # Increase indent for the body
                indent_level += 1
                indent = "    " * indent_level

            elif tok.lower() == "loopend":
                block1, i = self.extract_block(tokens, i + 1)
                if i < len(tokens) and tokens[i] == '(':
                    _, i = self.extract_block(tokens, i)
                
                # Decrease indent
                indent_level -= 1
                indent = "    " * indent_level
                if self.language == "javascript":
                    flow.append(f"{indent}}}")

            elif tok.lower() == "if":
                cond_block, i = self.extract_block(tokens, i + 1)
                cond_text = " ".join(cond_block)

                branches_block, i = self.extract_block(tokens, i)
                branches_code = self.parse_if_branches(branches_block, cond_text, indent_level)
                flow.extend(branches_code)

            elif tok.lower() == "jmp":
                block, i = self.extract_block(tokens, i + 1)
                target_label = " ".join(block)
                if self.language == "python":
                    flow.append(f"{indent}# TODO: jmp a {target_label} (Reestructurar con funciones o bucles)")
                else:
                    flow.append(f"{indent}// TODO: jmp a {target_label} (Reestructurar con funciones o bucles)")

            else:
                i += 1

        return flow

    def parse_if_branches(self, tokens, cond_text, indent_level):
        flow = []
        indent = "    " * indent_level
        inner_indent = "    " * (indent_level + 1)
        
        i = 0
        branch_count = 0
        
        if self.language == "python":
            flow.append(f"{indent}# TODO: Evaluar condición -> {cond_text}")
        elif self.language == "javascript":
            flow.append(f"{indent}// TODO: Evaluar condición -> {cond_text}")

        while i < len(tokens):
            tok = tokens[i]
            if re.match(r'If\d+', tok, re.IGNORECASE):
                branch_label_words = []
                i += 1
                while i < len(tokens) and tokens[i] != '(':
                    branch_label_words.append(tokens[i])
                    i += 1
                branch_label = " ".join(branch_label_words)
                branch_actions, i = self.extract_block(tokens, i)

                if self.language == "python":
                    kw = "if" if branch_count == 0 else "elif"
                    flow.append(f"{indent}{kw} condition == '{branch_label}':")
                elif self.language == "javascript":
                    kw = "if" if branch_count == 0 else "else if"
                    flow.append(f"{indent}{kw} (condition === '{branch_label}') {{")

                # Parse inner branch actions
                inner_flow = self.parse_sequence(branch_actions, indent_level + 1)
                if not inner_flow and self.language == "python":
                    inner_flow = [f"{inner_indent}pass"]
                    
                flow.extend(inner_flow)
                
                if self.language == "javascript":
                    flow.append(f"{indent}}}")
                
                branch_count += 1
            else:
                i += 1

        return flow

    def assemble_code(self):
        lines = []
        
        if self.language == "python":
            for func_name, doc in self.functions:
                lines.append(f"def {func_name}():")
                doc_clean = doc.replace('\n', ' ')
                lines.append(f'    """ {doc_clean} """')
                lines.append(f"    pass\n")
            
            lines.append("def main():")
            if not self.main_flow:
                lines.append("    pass")
            else:
                lines.extend(self.main_flow)
                
            lines.append("\nif __name__ == '__main__':")
            lines.append("    main()")

        elif self.language == "javascript":
            for func_name, doc in self.functions:
                doc_clean = doc.replace('\n', ' ')
                lines.append(f"// {doc_clean}")
                lines.append(f"function {func_name}() {{")
                lines.append(f"    // TODO: Implementar")
                lines.append(f"}}\n")
            
            lines.append("function main() {")
            lines.extend(self.main_flow)
            lines.append("}\n")
            lines.append("main();")

        return "\n".join(lines)

if __name__ == '__main__':
    root = tk.Tk()
    app = RIFCApp(root)
    root.mainloop()