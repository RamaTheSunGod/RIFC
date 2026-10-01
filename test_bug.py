import sys
from RIFC import NativeFlowCompiler

code = """
start(Inicio)
act(label:lectura)(Leer)
If (A?)(
  If1 Si (act(A))
  If2 No (act(B))
)
jmp(label:lectura)
end(Fin)
"""
try:
    compiler = NativeFlowCompiler(code)
    compiler.parse()
    compiler.calculate_layout()
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
