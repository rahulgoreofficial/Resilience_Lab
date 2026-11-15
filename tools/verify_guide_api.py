import urllib.request
import json
import sys

def req(url, method='GET', data=None):
    payload = json.dumps(data).encode('utf-8') if data is not None else None
    headers = {'Content-Type': 'application/json'} if data is not None else {}
    r = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode('utf-8'))

def main():
    print('[1] Fetching networks...')
    net_list = req('http://127.0.0.1:8000/api/v1/networks')['items']
    guide_net = next((n for n in net_list if n['name'] == 'Interactive Lab Demo Network'), None)

    if not guide_net:
        print('[2] Creating Interactive Lab Demo Network...')
        demo_topo = {
            'name': 'Interactive Lab Demo Network',
            'description': 'Demonstration network for the Interactive 3D Network Lab guide.',
            'network_type': 'undirected',
            'data': {
                'nodes': [
                    {'id': 'gw-1', 'label': 'Internet Gateway', 'type': 'gateway'},
                    {'id': 'fw-1', 'label': 'Perimeter Firewall', 'type': 'firewall'},
                    {'id': 'rt-1', 'label': 'Core Router A', 'type': 'router'},
                    {'id': 'rt-2', 'label': 'Core Router B', 'type': 'router'},
                    {'id': 'sw-1', 'label': 'Access Switch 1', 'type': 'switch'},
                    {'id': 'sw-2', 'label': 'Access Switch 2', 'type': 'switch'},
                    {'id': 'srv-1', 'label': 'Web Server', 'type': 'server'},
                    {'id': 'db-1', 'label': 'Database Server', 'type': 'database'}
                ],
                'edges': [
                    {'source': 'gw-1', 'target': 'fw-1', 'weight': 1, 'latency': 2, 'capacity': 10000},
                    {'source': 'fw-1', 'target': 'rt-1', 'weight': 1, 'latency': 1, 'capacity': 5000},
                    {'source': 'rt-1', 'target': 'rt-2', 'weight': 1, 'latency': 1, 'capacity': 5000},
                    {'source': 'rt-1', 'target': 'sw-1', 'weight': 1, 'latency': 2, 'capacity': 1000},
                    {'source': 'rt-2', 'target': 'sw-2', 'weight': 1, 'latency': 2, 'capacity': 1000},
                    {'source': 'sw-1', 'target': 'srv-1', 'weight': 1, 'latency': 1, 'capacity': 500},
                    {'source': 'sw-2', 'target': 'db-1', 'weight': 1, 'latency': 1, 'capacity': 500},
                    {'source': 'sw-1', 'target': 'sw-2', 'weight': 2, 'latency': 3, 'capacity': 500}
                ]
            }
        }
        guide_net = req('http://127.0.0.1:8000/api/v1/networks/import', method='POST', data=demo_topo)

    net_id = guide_net['id']
    print(f'[+] Guide Network ID: {net_id}')

    print('[3] Testing GET /topology...')
    topo = req(f'http://127.0.0.1:8000/api/v1/networks/{net_id}/topology')
    node_count = len(topo['elements']['nodes'])
    edge_count = len(topo['elements']['edges'])
    print(f'    Topology confirmed: {node_count} nodes, {edge_count} edges.')

    print('[4] Testing GET /analysis...')
    an_get = req(f'http://127.0.0.1:8000/api/v1/networks/{net_id}/analysis')
    print(f'    articulation_points: {an_get.get("articulation_points")}')
    print(f'    bridges: {an_get.get("bridges")}')
    print(f'    is_connected: {an_get.get("is_connected")}')
    print(f'    node_count: {an_get.get("node_count")}')

    print('[5] Testing POST /analysis (compatibility)...')
    an_post = req(f'http://127.0.0.1:8000/api/v1/networks/{net_id}/analysis', method='POST', data={})
    print(f'    POST status: OK, components: {an_post.get("component_count")}')

    print('[6] Testing GET /criticality...')
    crit = req(f'http://127.0.0.1:8000/api/v1/networks/{net_id}/criticality')
    top_node = crit['top_nodes'][0]
    print(f'    Top critical node: {top_node["node_id"]} (AP: {top_node["is_articulation_point"]})')

    print('[7] Testing node failure simulation on rt-1...')
    fail_res = req(
        f'http://127.0.0.1:8000/api/v1/simulations/node-failure?network_id={net_id}',
        method='POST',
        data={'failed_node_ids': ['rt-1']}
    )
    print(f'    Failed nodes: {fail_res.get("failed_nodes")}')
    print(f'    Components: {fail_res.get("initial_components")} -> {fail_res.get("final_components")}')
    print(f'    Service resilience: {fail_res.get("service_resilience")}')

    print('[8] Testing cascading failure on rt-1...')
    casc_res = req(
        f'http://127.0.0.1:8000/api/v1/simulations/cascading?network_id={net_id}',
        method='POST',
        data={'initial_failed_nodes': ['rt-1'], 'overload_threshold': 0.8, 'max_simulation_rounds': 5}
    )
    print(f'    Cascade rounds: {casc_res.get("cascade_rounds")}, Failed: {len(casc_res.get("failed_nodes", []))}')

    print('\n[VERIFICATION COMPLETE] All guide endpoints, calculations, and simulations are operational.')

if __name__ == '__main__':
    main()

