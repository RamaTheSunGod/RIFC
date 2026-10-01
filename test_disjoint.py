from RIFC import NativeFlowCompiler

code = """
start(Inicio)
act(Paso 1)
end(Fin)

start(SubInicio)
act(Paso Sub)
end(SubFin)
"""

try:
    compiler = NativeFlowCompiler(code)
    # The parser currently raises an error if start is called twice?
    # Wait, let's look at parse_sequence for start/end
except Exception as e:
    pass
