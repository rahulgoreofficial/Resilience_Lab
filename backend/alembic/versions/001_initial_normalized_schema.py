"""Initial normalized schema for networks, nodes, edges, snapshots, simulations, and events.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-02 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Networks Table
    op.create_table(
        "networks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("network_type", sa.String(64), nullable=False, server_default="COMMUNICATION_NETWORK"),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_networks_name", "networks", ["name"])

    # 2. Nodes Table
    op.create_table(
        "nodes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("network_id", sa.String(36), sa.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_id", sa.String(64), nullable=False),
        sa.Column("node_type", sa.String(32), nullable=False),
        sa.Column("importance", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("capacity", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("current_load", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("failure_probability", sa.Float(), nullable=False, server_default="0.01"),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("network_id", "node_id", name="uq_network_node_id"),
        sa.CheckConstraint("importance >= 0.0", name="chk_node_importance_non_negative"),
        sa.CheckConstraint("capacity > 0.0", name="chk_node_capacity_positive"),
        sa.CheckConstraint("current_load >= 0.0", name="chk_node_load_non_negative"),
        sa.CheckConstraint("failure_probability >= 0.0 AND failure_probability <= 1.0", name="chk_node_fail_prob_range")
    )
    op.create_index("ix_nodes_network_id", "nodes", ["network_id"])

    # 3. Edges Table
    op.create_table(
        "edges",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("network_id", sa.String(36), sa.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("edge_id", sa.String(64), nullable=False),
        sa.Column("source_node_id", sa.String(64), nullable=False),
        sa.Column("target_node_id", sa.String(64), nullable=False),
        sa.Column("canonical_u", sa.String(64), nullable=False),
        sa.Column("canonical_v", sa.String(64), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("latency", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("capacity", sa.Float(), nullable=False, server_default="10.0"),
        sa.Column("reliability", sa.Float(), nullable=False, server_default="0.99"),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("network_id", "edge_id", name="uq_network_edge_id"),
        sa.UniqueConstraint("network_id", "canonical_u", "canonical_v", name="uq_network_undirected_edge"),
        sa.CheckConstraint("canonical_u != canonical_v", name="chk_edge_no_self_loops"),
        sa.CheckConstraint("weight >= 0.0", name="chk_edge_weight_non_negative"),
        sa.CheckConstraint("latency >= 0.0", name="chk_edge_latency_non_negative"),
        sa.CheckConstraint("capacity > 0.0", name="chk_edge_capacity_positive"),
        sa.CheckConstraint("reliability >= 0.0 AND reliability <= 1.0", name="chk_edge_reliability_range")
    )
    op.create_index("ix_edges_network_id", "edges", ["network_id"])

    # 4. Network Snapshots Table
    op.create_table(
        "network_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("network_id", sa.String(36), sa.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("network_version", sa.Integer(), nullable=False),
        sa.Column("graph_snapshot", sa.JSON(), nullable=False),
        sa.Column("snapshot_hash", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index("ix_network_snapshots_network_id", "network_snapshots", ["network_id"])
    op.create_index("ix_network_snapshots_snapshot_hash", "network_snapshots", ["snapshot_hash"])

    # 5. Simulations Table
    op.create_table(
        "simulations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("network_id", sa.String(36), sa.ForeignKey("networks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_id", sa.String(36), sa.ForeignKey("network_snapshots.id", ondelete="SET NULL"), nullable=True),
        sa.Column("simulation_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="queued"),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("random_seed", sa.Integer(), nullable=True),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index("ix_simulations_network_id", "simulations", ["network_id"])
    op.create_index("ix_simulations_snapshot_id", "simulations", ["snapshot_id"])
    op.create_index("ix_simulations_simulation_type", "simulations", ["simulation_type"])
    op.create_index("ix_simulations_status", "simulations", ["status"])
    op.create_index("ix_simulations_created_at", "simulations", ["created_at"])

    # 6. Simulation Events Table
    op.create_table(
        "simulation_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("simulation_id", sa.String(36), sa.ForeignKey("simulations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("event_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("simulation_id", "sequence_number", name="uq_simulation_event_sequence")
    )
    op.create_index("ix_simulation_events_simulation_id", "simulation_events", ["simulation_id"])


def downgrade() -> None:
    op.drop_table("simulation_events")
    op.drop_table("simulations")
    op.drop_table("network_snapshots")
    op.drop_table("edges")
    op.drop_table("nodes")
    op.drop_table("networks")

