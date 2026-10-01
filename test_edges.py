from RIFC import NativeFlowCompiler

code = """
start(Inicio)
act(Paso 1)
end(Fin)

start(SubInicio)
act(Paso Sub)
end(SubFin)
"""

compiler = NativeFlowCompiler(code)
compiler.parse()
print(compiler.edges)
print(compiler.nodes)
