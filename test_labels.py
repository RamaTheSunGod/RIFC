from RIFC import NativeFlowCompiler

code = """
start(Inicio)
If (label:mylabel)(Cond?)(
    If1 Si (act(A))
    If2 No (act(B))
)
io(label:myio)(Data)
act(Ir a IO)
jmp(label:myio)
end(Fin)
"""

try:
    compiler = NativeFlowCompiler(code)
    compiler.parse()
    compiler.calculate_layout()
    compiler.generate_svg("test_labels.svg")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
