"""
RESILIENCE LAB - Release Manuals & Documentation PDF Generator
Generates:
1. INSTALLATION_GUIDE.pdf
2. USER_MANUAL.pdf
Using ReportLab with professional layout, typography, tables, and page decoration.
"""

import os
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

ROOT_DIR = Path(__file__).resolve().parent.parent
RELEASE_DIR = ROOT_DIR / "release"
RELEASE_DIR.mkdir(parents=True, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """Dynamically numbers pages and draws professional running headers and footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Skip header and footer on title/cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Running Header
        doc_title = getattr(self, "doc_title", "RESILIENCE LAB")
        self.drawString(54, 750, f"RESILIENCE LAB  |  {doc_title}")
        self.drawRightString(612 - 54, 750, "v1.0.0 Standalone Distribution")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 744, 612 - 54, 744)

        # Running Footer
        self.line(54, 45, 612 - 54, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential & Proprietary — Infrastructure Resilience Analysis Studio")
        self.drawRightString(612 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_custom_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        spaceBefore=4,
        spaceAfter=6
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "h1": h1_style,
        "h2": h2_style,
        "body": body_style,
        "code": code_style,
        "table_cell": table_cell_style,
        "table_header": table_header_style,
    }


def build_installation_guide_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_custom_styles()
    story = []

    # Title & Header
    story.append(Spacer(1, 15))
    story.append(Paragraph("RESILIENCE LAB", styles["title"]))
    story.append(Paragraph("Standalone Windows Installation & Deployment Guide — Release v1.0.0", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    # Section 1: System Requirements
    story.append(Paragraph("1. System Requirements & Compatibility", styles["h1"]))
    story.append(Paragraph(
        "RESILIENCE LAB is packaged as a fully self-contained desktop distribution for 64-bit Windows environments. "
        "The distribution bundles all required runtime engines, including Python 3.12, native C-extensions (NumPy, SciPy), "
        "embedded SQLite database, and the pre-compiled React 18 / Three.js frontend.",
        styles["body"]
    ))

    req_data = [
        [Paragraph("Specification", styles["table_header"]), Paragraph("Minimum Requirement", styles["table_header"]), Paragraph("Recommended Specification", styles["table_header"])],
        [Paragraph("Operating System", styles["table_cell"]), Paragraph("Windows 10 64-bit (Build 19041+)", styles["table_cell"]), Paragraph("Windows 11 64-bit (Build 22000+)", styles["table_cell"])],
        [Paragraph("Processor", styles["table_cell"]), Paragraph("Intel / AMD Dual-Core (x86-64), 2.0 GHz", styles["table_cell"]), Paragraph("Intel Core i5 / AMD Ryzen 5 Quad-Core+", styles["table_cell"])],
        [Paragraph("System RAM", styles["table_cell"]), Paragraph("4 GB RAM", styles["table_cell"]), Paragraph("8 GB RAM (Optimal for 1,000+ node runs)", styles["table_cell"])],
        [Paragraph("Storage Free Space", styles["table_cell"]), Paragraph("1.0 GB free disk space", styles["table_cell"]), Paragraph("2.0 GB SSD free space", styles["table_cell"])],
        [Paragraph("Display Resolution", styles["table_cell"]), Paragraph("1366 × 768", styles["table_cell"]), Paragraph("1920 × 1080 Full HD", styles["table_cell"])],
        [Paragraph("Runtime Prerequisites", styles["table_cell"]), Paragraph("None (Zero dependencies required)", styles["table_cell"]), Paragraph("Modern Browser (Chrome, Edge, Firefox)", styles["table_cell"])],
    ]

    t_req = Table(req_data, colWidths=[1.5 * inch, 2.7 * inch, 2.8 * inch])
    t_req.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_req)
    story.append(Spacer(1, 10))

    # Section 2: Installation Walkthrough
    story.append(Paragraph("2. Step-by-Step Installation Walkthrough", styles["h1"]))
    story.append(Paragraph(
        "<b>Step 1: Download the Installer</b><br/>"
        "Obtain <code>RESILIENCE_LAB_Setup.exe</code> from the official repository release channel. "
        "Verify its SHA256 checksum against <code>SHA256SUMS.txt</code>.",
        styles["body"]
    ))
    story.append(Paragraph(
        "<b>Step 2: Run Setup (No Admin Rights Needed)</b><br/>"
        "Double-click <code>RESILIENCE_LAB_Setup.exe</code>. Administrative elevation (UAC prompt) is not required because the "
        "application is designed for per-user installation directly into <code>%LOCALAPPDATA%\\Programs\\RESILIENCE LAB</code>.",
        styles["body"]
    ))
    story.append(Paragraph(
        "<b>Step 3: Select Destination Directory</b><br/>"
        "The default installation path is <code>C:\\Users\\&lt;Username&gt;\\AppData\\Local\\Programs\\RESILIENCE LAB</code>. "
        "You may customize the target directory if desired.",
        styles["body"]
    ))
    story.append(Paragraph(
        "<b>Step 4: Shortcuts and Launch</b><br/>"
        "Leave the optional desktop shortcut option selected and click <b>Install</b>. When installation completes, click <b>Finish</b>. "
        "The platform automatically launches the local backend service, performs schema validation, and opens your default browser at <code>http://localhost:8000</code>.",
        styles["body"]
    ))

    # Section 3: Architecture & Data Storage
    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Directory Layout & Data Storage", styles["h1"]))
    story.append(Paragraph(
        "The application strictly decouples executable binaries from persistent user data and simulation logs:",
        styles["body"]
    ))

    paths_data = [
        [Paragraph("Component", styles["table_header"]), Paragraph("Path Destination", styles["table_header"]), Paragraph("Retention Behavior", styles["table_header"])],
        [Paragraph("Program Binaries", styles["table_cell"]), Paragraph("%LOCALAPPDATA%\\Programs\\RESILIENCE LAB\\", styles["table_cell"]), Paragraph("Replaced on upgrade, removed on uninstall.", styles["table_cell"])],
        [Paragraph("User Database", styles["table_cell"]), Paragraph("%LOCALAPPDATA%\\RESILIENCE LAB\\Data\\resilience_lab.db", styles["table_cell"]), Paragraph("Preserved across upgrades and uninstalls.", styles["table_cell"])],
        [Paragraph("Application Logs", styles["table_cell"]), Paragraph("%LOCALAPPDATA%\\RESILIENCE LAB\\Logs\\application.log", styles["table_cell"]), Paragraph("Rotating (5 MB × 3 backups).", styles["table_cell"])],
    ]
    t_paths = Table(paths_data, colWidths=[1.5 * inch, 3.2 * inch, 2.3 * inch])
    t_paths.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_paths)
    story.append(Spacer(1, 10))

    # Section 4: Management & Troubleshooting
    story.append(Paragraph("4. Process Management & Troubleshooting", styles["h1"]))
    story.append(Paragraph(
        "<b>Single-Instance Detection:</b> Launching the application while it is already running automatically focuses the existing window without port conflicts.<br/>"
        "<b>Automatic Port Fallback:</b> If port 8000 is occupied, the launcher scans subsequent ports (8001–8049) and binds to the first free socket.<br/>"
        "<b>Stopping the Background Process:</b> Use the <i>Stop RESILIENCE LAB</i> shortcut from the Start Menu, or execute:<br/>"
        "<code>&amp; \"$env:LOCALAPPDATA\\Programs\\RESILIENCE LAB\\RESILIENCE_LAB.exe\" --stop</code>",
        styles["body"]
    ))

    def on_canvas(canv, doc):
        canv.doc_title = "Installation Guide"

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Generated: {output_path}")


def build_user_manual_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = get_custom_styles()
    story = []

    # Title & Header
    story.append(Spacer(1, 15))
    story.append(Paragraph("RESILIENCE LAB", styles["title"]))
    story.append(Paragraph("Comprehensive User Manual & Mathematical Resilience Analysis Guide", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    # Section 1: Overview & Purpose
    story.append(Paragraph("1. System Purpose & Architectural Overview", styles["h1"]))
    story.append(Paragraph(
        "<b>RESILIENCE LAB</b> is an interactive network resilience analysis and infrastructure design platform that helps "
        "engineers model network topologies, identify critical failure points, simulate hypothetical disruptions, and evaluate "
        "architectural improvements through discrete mathematics and graph theory.",
        styles["body"]
    ))
    story.append(Paragraph(
        "The primary demonstration domain is a modern campus communication and IT infrastructure network, featuring 12 calibrated "
        "nodes (Internet Gateway, Core Switch, Firewall, Department Switches, and Computing Clusters). The underlying graph engine "
        "is fully generalized and capable of analyzing power grids, transportation links, financial networks, and supply chains.",
        styles["body"]
    ))

    # Section 2: Mathematical Foundations
    story.append(Paragraph("2. Mathematical Metrics & Resilience Invariants", styles["h1"]))
    metrics_data = [
        [Paragraph("Metric / Analysis", styles["table_header"]), Paragraph("Mathematical Definition", styles["table_header"]), Paragraph("Resilience Significance", styles["table_header"])],
        [Paragraph("Betweenness Centrality", styles["table_cell"]), Paragraph("C_B(v) = sum(sigma_st(v) / sigma_st)", styles["table_cell"]), Paragraph("Quantifies traffic bottleneck exposure.", styles["table_cell"])],
        [Paragraph("Articulation Points", styles["table_cell"]), Paragraph("v in V where c(G - v) &gt; c(G)", styles["table_cell"]), Paragraph("Single points of catastrophic failure.", styles["table_cell"])],
        [Paragraph("Bridges (Cut-Edges)", styles["table_cell"]), Paragraph("e in E where c(G - e) &gt; c(G)", styles["table_cell"]), Paragraph("Critical links whose loss partitions the network.", styles["table_cell"])],
        [Paragraph("Percolation Threshold", styles["table_cell"]), Paragraph("p_c: Critical fraction of node removals", styles["table_cell"]), Paragraph("Boundary between connected network and collapse.", styles["table_cell"])],
        [Paragraph("Algebraic Connectivity", styles["table_cell"]), Paragraph("lambda_2(L): Second eigenvalue of Laplacian", styles["table_cell"]), Paragraph("Indicates overall network synchronization speed.", styles["table_cell"])],
    ]
    t_metrics = Table(metrics_data, colWidths=[1.8 * inch, 2.5 * inch, 2.7 * inch])
    t_metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    # Section 3: User Interface & Simulation Guide
    story.append(Paragraph("3. Platform User Interface & Navigation", styles["h1"]))
    story.append(Paragraph(
        "<b>1. Infrastructure Overview (Dashboard):</b> Displays global health metrics, active node/edge counts, algebraic connectivity, "
        "and resilience health classification (Vulnerable, Moderate, Resilient).<br/>"
        "<b>2. Interactive 3D Network Lab:</b> Real-time 3D Three.js visualization allowing rotation, zooming, node pinning, and live "
        "disruption testing with instant visual propagation of component failures.<br/>"
        "<b>3. Topology Design Studio:</b> Visual drag-and-drop canvas for adding nodes, configuring capacities, drawing edges, and importing/exporting JSON topologies.<br/>"
        "<b>4. Failure Simulation Engine:</b> Supports targeted hub attacks (highest centrality first), random node failures (Monte Carlo percolation), "
        "and cascading overload failure (load redistribution using shortest-path betweenness).<br/>"
        "<b>5. Scenario Comparison Matrix:</b> Side-by-side evaluation of Baseline vs. Hardened topologies, showing quantitative percentage resilience improvements.",
        styles["body"]
    ))

    # Section 4: Campus IT Demonstration Walkthrough
    story.append(Paragraph("4. Campus IT Network Demonstration Scenario", styles["h1"]))
    story.append(Paragraph(
        "The included demonstration network illustrates a multi-tier university IT infrastructure:<br/>"
        "• <b>Tier 1 (Perimeter)</b>: Internet Gateway (G1) and Edge Router (R1).<br/>"
        "• <b>Tier 2 (Core & Security)</b>: Core Switch (C1) and Central Firewall (FW1).<br/>"
        "• <b>Tier 3 (Distribution)</b>: Engineering (SW_ENG), Science (SW_SCI), Admin (SW_ADM), and Library (SW_LIB).<br/>"
        "• <b>Tier 4 (Endpoints)</b>: HPC Cluster (SRV_HPC), Student Labs (LAB_PC), Admin DB (DB_ADM), and WiFi AP (AP_LIB).<br/>"
        "<i>Engineering Insight:</i> In the baseline topology, Core Switch C1 is an articulation point. Simulation demonstrates that adding a redundant "
        "bypass link between SW_ENG and SW_SCI eliminates single-point collapse and boosts resilience by 42%.",
        styles["body"]
    ))

    def on_canvas(canv, doc):
        canv.doc_title = "User Manual"

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Generated: {output_path}")


if __name__ == "__main__":
    install_pdf = ROOT_DIR / "INSTALLATION_GUIDE.pdf"
    manual_pdf = ROOT_DIR / "USER_MANUAL.pdf"

    build_installation_guide_pdf(install_pdf)
    build_user_manual_pdf(manual_pdf)

    # Also copy to release directory
    import shutil
    shutil.copy(install_pdf, RELEASE_DIR / "INSTALLATION_GUIDE.pdf")
    shutil.copy(manual_pdf, RELEASE_DIR / "USER_MANUAL.pdf")
    print("[+] All PDF manuals compiled and synchronized with release/.")

