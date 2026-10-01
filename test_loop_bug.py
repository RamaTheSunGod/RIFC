from RIFC import NativeFlowCompiler

code = """
start(Inicio)
If (Cond?)(
    If1 Si (act(A))
    If2 No (act(B))
)
loopstart(l1)
act(Dentro del loop 1)
loopend(l1)(volver)
end(Fin)
"""

try:
    compiler = NativeFlowCompiler(code)
    compiler.parse()
    compiler.calculate_layout()
    compiler.generate_svg("test_loop_bug.svg")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
