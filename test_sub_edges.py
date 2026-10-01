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

compiler = NativeFlowCompiler(code)
compiler.parse()
for node in compiler.nodes:
    if node['type'] == 'subroutine':
        print(f"Subroutine node found: {node}")
print("Roots:")
incoming = {}
for node in compiler.nodes:
    incoming[node['id']] = []
for edge in compiler.edges:
    if not edge['dashed']:
        incoming[edge['to']].append(edge['from'])
print([n['id'] for n in compiler.nodes if not incoming.get(n['id'])])
