# RIFC (Rama's Instant Flow Chart)

<p align="center">
  <img src="icon.ico" alt="RIFC Logo" width="128" height="128">
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

loopstart(sample_loop)
    act(read_tag)(Read analog input)
    
    If (Value in range?)(
        If1 Yes ( act(Process sample) )
        If2 No ( act(Trigger warning) jmp(read_tag) )
        If3 Error ( act(Fail-safe state) )
    )
loopend(sample_loop)(10 iterations)

io(Export CSV log)

db(Write to database)

doc(Generate PDF summary)

end(End)
```

### Installation and Execution
## Option 1: Standalone Binary (Releases)
Download the latest pre-compiled archive from the Releases section of this repository, extract the archive, and launch RIFC.exe. No Python runtime is required.
## Option 2: Running from Source Code
# Clone the repository
# Install dependencies
Note: To export to PNG or PDF, install CairoSVG via pip install cairosvg and ensure Cairo shared libraries are installed on your host system.
# Run the application

### License and Copyright
## Source Code: 
Distributed under the GNU General Public License v3.0 (GPLv3). Any modifications or derivative software must remain free and licensed under GPLv3.

## Brand and Logo: 
The name "RIFC (Rama's Instant Flow Chart)" and the raven emblem (icon.ico) are intellectual property of their author. Redistribution and reference without graphical modification are permitted under Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0).
