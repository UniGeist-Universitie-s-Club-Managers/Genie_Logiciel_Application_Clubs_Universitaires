from django.db.migrations.loader import MigrationLoader
from django.db import connections
loader = MigrationLoader(connections['default'])
try:
    state = loader.project_state()
    print('project_state created successfully')
except Exception as e:
    import traceback
    traceback.print_exc()
    graph = loader.graph
    for node in graph.nodes:
        try:
            # try building state up to this node
            nodes = list(graph.nodes)[:list(graph.nodes).index(node)+1]
            s = graph.make_state(nodes=nodes)
        except Exception:
            print('\nFailed on node:', node)
            import traceback
            traceback.print_exc()
            break

print('done')
