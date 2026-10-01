import sys
from RIFC import NativeFlowCompiler

code = """
start(Inicio)
act(Paso 1)
loopstart(l1)
act(Dentro del loop 1)
If (Cond?)(
    If1 Si (act(A))
    If2 No (act(B))
)
loopend(l1)(volver)
act(Fin loop)
end(Fin)
"""

compiler = NativeFlowCompiler(code)
compiler.parse()
compiler.calculate_layout()
compiler.generate_svg("test_loop_2.svg")

for e in compiler.edges:
    print(f"{e['from']} -> {e['to']} dashed={e['dashed']}")
