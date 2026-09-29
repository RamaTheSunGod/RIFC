# RIFC (Rama's Instant Flow Chart)

<p align="center">
  <img src="icon.ico" alt="RIFC Logo" width="128" height="128">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-GPLv3-green.svg" alt="License">
</p>

<p align="center">
  <b>Instant, standalone, and lightweight flowchart generator powered by structured pseudo-code.</b>
</p>

---

## Introduction

RIFC (Rama's Instant Flow Chart) is a desktop application designed for engineers, students, and developers to rapidly prototype and visualize flowcharts from clean, concise pseudo-code.

Unlike alternatives that require heavy Java runtime environments, background headless web browsers, or active internet connectivity, RIFC features an integrated native layout and rendering engine capable of rendering and exporting diagrams instantly in fully offline environments.

---

## Features

- Real-Time Native Rendering: Instant interactive canvas preview with zoom support (Ctrl + Mouse Wheel) without external layout dependencies.
- Vector SVG Engine: Generates scalable SVG output with auto-calculated curved paths for loops and long jumps.
- Multi-format Export: Native export to SVG, with optional compilation to PNG and PDF via CairoSVG.
- *Export your charts as boilerplate code for python and JavaScript*
- Expressive Minimalist DSL: Block-based syntax covering processes, conditional branches, loops, and jumps.
- Syntax-Highlighted Editor: Real-time keyword tagging, bracket detection, and automatic parentheses pairing.
- Customization Presets: Built-in styles (Classic, Modern, Academic) and a Custom mode with a dedicated palette editor.
- Internationalization (i18n): Built-in runtime switching between English and Spanish.
- UI Themes: Dark and Light application themes.

---

## Command Syntax (DSL)

RIFC uses an intuitive block-based syntax enclosed in parentheses:

| Command | Syntax | Description |
| :--- | :--- | :--- |
| Start | `start(Text)` | Defines the diagram start node. Required. |
| End | `end(Text)` | Defines the terminal node. Required. |
| Process | `act(Description)` or `act(label)(Description)` | Standard rectangular process block. |
| Input/Output | `io(Description)` | Parallelogram block for I/O operations. |
| Database | `db(Description)` | Cylinder block representing persistent storage. |
| Document | `doc(Description)` | Document block with a curved bottom edge. |
| Decision | `If (condition)( If1 Option (act...) If2 Option (act...) )` | Diamond block supporting multiple branch outputs. |
| Loop Start | `loopstart(loop_name)` | Declares the beginning of a looped segment. |
| Loop End | `loopend(loop_name)(condition)` | Closes the loop and routes a return edge to loop start. |
| Jump | `jmp(target_label)` | Direct branch jump to an action node with matching label. |

### Code Example

```text
start(Start)

    act(label:read)(Read sensor)
    
    If (active sensor?)(
        If1 Yes ( act(Read) )
        If2 No ( act(Turn off) jmp(label:read) )
        If3 Maybe ( act(Failure Mode) )
    )


io(Export data)
db(Save in database)
doc(Archive)

end(End)
```
<img width="345" height="605" alt="image" src="https://github.com/user-attachments/assets/507e41b1-7b1d-4d27-a2d4-a8fc18243a27" />

# Installation and Execution
## Option 1: Standalone Binary (Releases)
Download the latest pre-compiled archive from the Releases section of this repository, extract the archive, and launch RIFC.exe. No Python runtime is required.
## Option 2: Running from Source Code
### Clone the repository
```git clone [https://github.com/RamaTheSunGod/RIFC.git](https://github.com/RamaTheSunGod/RIFC.git)```
cd RIFC
### Install dependencies
```pip install -r requirements.txt```
Note: To export to PNG or PDF, install CairoSVG via pip install cairosvg and ensure Cairo shared libraries are installed on your host system.
### Run the application

# License and Copyright
## Source Code: 
Distributed under the GNU General Public License v3.0 (GPLv3). Any modifications or derivative software must remain free and licensed under GPLv3.

## Brand and Logo: 
The name "RIFC (Rama's Instant Flow Chart)" and the raven emblem (icon.ico) are intellectual property of their author. Redistribution and reference without graphical modification are permitted under Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0).
