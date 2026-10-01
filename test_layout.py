from RIFC import NativeFlowCompiler

code = """
start(Inicio)
act(Proceso 1)
sub(label:sub1)(Llamar a MiSub)
act(Proceso 2)
end(Fin)

substart(MiSub)
act(Proceso Sub)
subend(Retorno)
"""

try:
    compiler = NativeFlowCompiler(code)
    compiler.parse()
    compiler.calculate_layout()
    compiler.generate_svg("test_layout.svg")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
