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
try:
    compiler = NativeFlowCompiler(code)
    compiler.parse()
    compiler.calculate_layout()
    compiler.generate_svg("test_loop.svg")
    print("Success SVG")
except Exception as e:
    import traceback
    traceback.print_exc()
