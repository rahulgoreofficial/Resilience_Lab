"""
Seed Database Script for RESILIENCE LAB.
Populates standard benchmark topologies:
1. Enterprise Tier-3 Datacenter Network
2. Campus Redundant Ring Backbone
3. Bridge-Vulnerable Hybrid Network
"""

import os
import sys
from pathlib import Path

# Set up paths and environment
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "sqlite:///infrastructure_resilience.db")

from app.database.session import engine, SessionLocal
from app.database.init_db import init_db
from app.services.network_service import NetworkService
from app.schemas.network import NetworkCreate
from app.schemas.node import NodeCreate
from app.schemas.edge import EdgeCreate
from app.repositories.network_repository import NetworkRepository


def seed():
    print("[*] Initializing database schema...")
    init_db(engine)

    db = SessionLocal()
    try:
        existing, total = NetworkRepository.list_all(db)
        if total > 0:
            print(f"[+] Database already contains {total} network(s). Skipping seed.")
            return

        print("[*] Seeding sample enterprise networks...")

        # 1. Tier-3 Enterprise Datacenter
        dc_nodes = [
            NodeCreate(node_id="gw_core_1", node_type="gateway", capacity=1000.0, importance=1.0, current_load=150.0),
            NodeCreate(node_id="gw_core_2", node_type="gateway", capacity=1000.0, importance=1.0, current_load=120.0),
            NodeCreate(node_id="fw_edge_1", node_type="firewall", capacity=800.0, importance=0.9, current_load=90.0),
            NodeCreate(node_id="fw_edge_2", node_type="firewall", capacity=800.0, importance=0.9, current_load=85.0),
            NodeCreate(node_id="r_dist_1", node_type="router", capacity=600.0, importance=0.8, current_load=110.0),
            NodeCreate(node_id="r_dist_2", node_type="router", capacity=600.0, importance=0.8, current_load=105.0),
            NodeCreate(node_id="sw_access_1", node_type="switch", capacity=400.0, importance=0.6, current_load=60.0),
            NodeCreate(node_id="sw_access_2", node_type="switch", capacity=400.0, importance=0.6, current_load=70.0),
            NodeCreate(node_id="srv_app_1", node_type="server", capacity=250.0, importance=0.7, current_load=40.0),
            NodeCreate(node_id="srv_app_2", node_type="server", capacity=250.0, importance=0.7, current_load=45.0),
            NodeCreate(node_id="srv_db_primary", node_type="database", capacity=500.0, importance=0.95, current_load=120.0),
            NodeCreate(node_id="srv_db_replica", node_type="database", capacity=500.0, importance=0.85, current_load=60.0),
        ]
        dc_edges = [
            EdgeCreate(edge_id="e_gw1_gw2", source="gw_core_1", target="gw_core_2", weight=1.0, bandwidth=10000.0),
            EdgeCreate(edge_id="e_gw1_fw1", source="gw_core_1", target="fw_edge_1", weight=1.5, bandwidth=5000.0),
            EdgeCreate(edge_id="e_gw2_fw2", source="gw_core_2", target="fw_edge_2", weight=1.5, bandwidth=5000.0),
            EdgeCreate(edge_id="e_gw1_fw2", source="gw_core_1", target="fw_edge_2", weight=2.0, bandwidth=5000.0),
            EdgeCreate(edge_id="e_gw2_fw1", source="gw_core_2", target="fw_edge_1", weight=2.0, bandwidth=5000.0),
            EdgeCreate(edge_id="e_fw1_rdist1", source="fw_edge_1", target="r_dist_1", weight=1.0, bandwidth=4000.0),
            EdgeCreate(edge_id="e_fw2_rdist2", source="fw_edge_2", target="r_dist_2", weight=1.0, bandwidth=4000.0),
            EdgeCreate(edge_id="e_rdist1_rdist2", source="r_dist_1", target="r_dist_2", weight=1.0, bandwidth=4000.0),
            EdgeCreate(edge_id="e_rdist1_sw1", source="r_dist_1", target="sw_access_1", weight=1.2, bandwidth=2000.0),
            EdgeCreate(edge_id="e_rdist2_sw2", source="r_dist_2", target="sw_access_2", weight=1.2, bandwidth=2000.0),
            EdgeCreate(edge_id="e_rdist1_sw2", source="r_dist_1", target="sw_access_2", weight=1.8, bandwidth=2000.0),
            EdgeCreate(edge_id="e_rdist2_sw1", source="r_dist_2", target="sw_access_1", weight=1.8, bandwidth=2000.0),
            EdgeCreate(edge_id="e_sw1_app1", source="sw_access_1", target="srv_app_1", weight=1.0, bandwidth=1000.0),
            EdgeCreate(edge_id="e_sw2_app2", source="sw_access_2", target="srv_app_2", weight=1.0, bandwidth=1000.0),
            EdgeCreate(edge_id="e_sw1_app2", source="sw_access_1", target="srv_app_2", weight=1.5, bandwidth=1000.0),
            EdgeCreate(edge_id="e_sw2_app1", source="sw_access_2", target="srv_app_1", weight=1.5, bandwidth=1000.0),
            EdgeCreate(edge_id="e_app1_dbprim", source="srv_app_1", target="srv_db_primary", weight=1.0, bandwidth=2000.0),
            EdgeCreate(edge_id="e_app2_dbprim", source="srv_app_2", target="srv_db_primary", weight=1.0, bandwidth=2000.0),
            EdgeCreate(edge_id="e_db_sync", source="srv_db_primary", target="srv_db_replica", weight=0.8, bandwidth=4000.0),
            EdgeCreate(edge_id="e_app1_dbrepl", source="srv_app_1", target="srv_db_replica", weight=1.5, bandwidth=1000.0),
        ]
        net1 = NetworkService.create_network(
            db,
            NetworkCreate(
                name="Enterprise Tier-3 Datacenter",
                description="High-availability datacenter topology with dual gateways, firewalls, distribution routers, and database clustering.",
                network_type="enterprise",
                nodes=dc_nodes,
                edges=dc_edges
            )
        )
        print(f"[+] Created '{net1.name}' (ID: {net1.id}, {len(dc_nodes)} nodes, {len(dc_edges)} edges)")

        # 2. Campus Redundant Ring Backbone
        ring_nodes = [
            NodeCreate(node_id=f"campus_hub_{i}", node_type="router", capacity=500.0, importance=0.8, current_load=50.0)
            for i in range(1, 7)
        ]
        ring_edges = [
            EdgeCreate(edge_id=f"e_ring_{i}_{i+1}", source=f"campus_hub_{i}", target=f"campus_hub_{i+1}", weight=2.0, bandwidth=2000.0)
            for i in range(1, 6)
        ]
        ring_edges.append(EdgeCreate(edge_id="e_ring_6_1", source="campus_hub_6", target="campus_hub_1", weight=2.0, bandwidth=2000.0))
        # Add diagonal chords for redundancy
        ring_edges.append(EdgeCreate(edge_id="e_chord_1_4", source="campus_hub_1", target="campus_hub_4", weight=3.0, bandwidth=4000.0))
        ring_edges.append(EdgeCreate(edge_id="e_chord_2_5", source="campus_hub_2", target="campus_hub_5", weight=3.0, bandwidth=4000.0))

        net2 = NetworkService.create_network(
            db,
            NetworkCreate(
                name="Campus Dual-Chord Ring Backbone",
                description="Fault-tolerant metro ring with internal cross-chords connecting 6 regional campus distribution nodes.",
                network_type="campus",
                nodes=ring_nodes,
                edges=ring_edges
            )
        )
        print(f"[+] Created '{net2.name}' (ID: {net2.id}, {len(ring_nodes)} nodes, {len(ring_edges)} edges)")

        # 3. Bridge-Vulnerable Hybrid Topology
        vuln_nodes = [
            NodeCreate(node_id="zoneA_core", node_type="router", capacity=400.0, importance=0.9),
            NodeCreate(node_id="zoneA_sw1", node_type="switch", capacity=200.0, importance=0.5),
            NodeCreate(node_id="zoneA_sw2", node_type="switch", capacity=200.0, importance=0.5),
            NodeCreate(node_id="bridge_router", node_type="router", capacity=300.0, importance=1.0),
            NodeCreate(node_id="zoneB_core", node_type="router", capacity=400.0, importance=0.9),
            NodeCreate(node_id="zoneB_srv1", node_type="server", capacity=250.0, importance=0.7),
            NodeCreate(node_id="zoneB_db", node_type="database", capacity=500.0, importance=0.95),
        ]
        vuln_edges = [
            EdgeCreate(edge_id="e_zA_1", source="zoneA_core", target="zoneA_sw1", weight=1.0),
            EdgeCreate(edge_id="e_zA_2", source="zoneA_core", target="zoneA_sw2", weight=1.0),
            EdgeCreate(edge_id="e_zA_loop", source="zoneA_sw1", target="zoneA_sw2", weight=1.5),
            EdgeCreate(edge_id="e_critical_bridge_1", source="zoneA_core", target="bridge_router", weight=2.5),
            EdgeCreate(edge_id="e_critical_bridge_2", source="bridge_router", target="zoneB_core", weight=2.5),
            EdgeCreate(edge_id="e_zB_1", source="zoneB_core", target="zoneB_srv1", weight=1.0),
            EdgeCreate(edge_id="e_zB_2", source="zoneB_core", target="zoneB_db", weight=1.0),
        ]
        net3 = NetworkService.create_network(
            db,
            NetworkCreate(
                name="Bridge-Vulnerable Hybrid Star-Mesh",
                description="Topology featuring single-point-of-failure articulation points and critical inter-zone communication bridges.",
                network_type="hybrid",
                nodes=vuln_nodes,
                edges=vuln_edges
            )
        )
        print(f"[+] Created '{net3.name}' (ID: {net3.id}, {len(vuln_nodes)} nodes, {len(vuln_edges)} edges)")

        print("[OK] Database seeding completed successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
