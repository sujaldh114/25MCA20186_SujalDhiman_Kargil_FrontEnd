from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import heapq
import math
import os

app = Flask(__name__, static_folder=".")
CORS(app)

# ─── CAMPUS GRAPH DATA ────────────────────────────────────────────────────────
# x, y = normalised 0..1 position on the campus map
# Campus real dimensions: ~900m wide, ~700m tall

NODES = {
    # GATES
    "g_main":   {"label": "Main Gate",         "x": .06,  "y": .50,  "type": "gate"},
    "g_north":  {"label": "North Gate",         "x": .06,  "y": .18,  "type": "gate"},
    "g_south":  {"label": "South Gate",         "x": .06,  "y": .82,  "type": "gate"},
    "g_east":   {"label": "East Gate",          "x": .94,  "y": .50,  "type": "gate"},

    # NORTH — ACADEMIC BLOCKS
    "A1": {"label": "Block A1", "x": .28, "y": .12, "type": "academic"},
    "A2": {"label": "Block A2", "x": .37, "y": .12, "type": "academic"},
    "A3": {"label": "Block A3", "x": .46, "y": .12, "type": "academic"},
    "B1": {"label": "Block B1", "x": .28, "y": .22, "type": "academic"},
    "B2": {"label": "Block B2", "x": .37, "y": .22, "type": "academic"},
    "B3": {"label": "Block B3", "x": .46, "y": .22, "type": "academic"},
    "B4": {"label": "Block B4", "x": .55, "y": .22, "type": "academic"},
    "B5": {"label": "Block B5", "x": .64, "y": .22, "type": "academic"},
    "C1": {"label": "Block C1", "x": .28, "y": .33, "type": "academic"},
    "C2": {"label": "Block C2", "x": .37, "y": .33, "type": "academic"},
    "C3": {"label": "Block C3", "x": .46, "y": .33, "type": "academic"},
    "D1": {"label": "Block D1", "x": .55, "y": .33, "type": "academic"},
    "D2": {"label": "Block D2", "x": .64, "y": .33, "type": "academic"},
    "D3": {"label": "Block D3", "x": .73, "y": .33, "type": "academic"},
    "D4": {"label": "Block D4", "x": .55, "y": .12, "type": "academic"},
    "D5": {"label": "Block D5", "x": .64, "y": .12, "type": "academic"},
    "D6": {"label": "Block D6", "x": .73, "y": .12, "type": "academic"},

    # NORTH — FACILITIES
    "lib":   {"label": "Central Library",   "x": .46, "y": .45, "type": "facility"},
    "aud":   {"label": "Auditorium",        "x": .36, "y": .45, "type": "facility"},
    "adm":   {"label": "Admin Block",       "x": .26, "y": .45, "type": "facility"},
    "food1": {"label": "Food Court N",      "x": .17, "y": .34, "type": "facility"},
    "med":   {"label": "Medical Centre",    "x": .17, "y": .24, "type": "facility"},
    "atm":   {"label": "ATM / Bank",        "x": .16, "y": .45, "type": "facility"},
    "conv":  {"label": "Convocation Hall",  "x": .73, "y": .45, "type": "facility"},
    "sport": {"label": "Sports Complex",    "x": .83, "y": .33, "type": "ground"},
    "cric":  {"label": "Cricket Ground",    "x": .83, "y": .17, "type": "ground"},

    # BOYS HOSTELS
    "LC_A":  {"label": "LC-A Hostel",   "x": .16, "y": .59, "type": "boys"},
    "LC_B":  {"label": "LC-B Hostel",   "x": .16, "y": .66, "type": "boys"},
    "LC_C":  {"label": "LC-C Hostel",   "x": .24, "y": .59, "type": "boys"},
    "LC_D":  {"label": "LC-D Hostel",   "x": .24, "y": .66, "type": "boys"},
    "NC1":   {"label": "NC-1 Hostel",   "x": .32, "y": .59, "type": "boys"},
    "NC2":   {"label": "NC-2 Hostel",   "x": .32, "y": .66, "type": "boys"},
    "NC3":   {"label": "NC-3 Hostel",   "x": .40, "y": .59, "type": "boys"},
    "NC4":   {"label": "NC-4 Hostel",   "x": .40, "y": .66, "type": "boys"},
    "NC5":   {"label": "NC-5 Hostel",   "x": .48, "y": .59, "type": "boys"},
    "NC6":   {"label": "NC-6 Hostel",   "x": .48, "y": .66, "type": "boys"},
    "Zakir": {"label": "Zakir Hostel",  "x": .56, "y": .59, "type": "boys"},

    # GIRLS HOSTELS
    "SK1": {"label": "Sukhna-1",   "x": .63, "y": .59, "type": "girls"},
    "SK2": {"label": "Sukhna-2",   "x": .71, "y": .59, "type": "girls"},
    "SK3": {"label": "Sukhna-3",   "x": .79, "y": .59, "type": "girls"},
    "GH1": {"label": "Girls H-1",  "x": .63, "y": .66, "type": "girls"},
    "GH2": {"label": "Girls H-2",  "x": .71, "y": .66, "type": "girls"},

    # SOUTH CAMPUS
    "SE1":    {"label": "SC Block E1",  "x": .28, "y": .83, "type": "academic"},
    "SE2":    {"label": "SC Block E2",  "x": .37, "y": .83, "type": "academic"},
    "SF1":    {"label": "SC Block F1",  "x": .46, "y": .83, "type": "academic"},
    "SF2":    {"label": "SC Block F2",  "x": .55, "y": .83, "type": "academic"},
    "SG1":    {"label": "SC Block G1",  "x": .64, "y": .83, "type": "academic"},
    "SC_lib":  {"label": "SC Library",  "x": .37, "y": .93, "type": "facility"},
    "SC_food": {"label": "SC Food Ct.", "x": .26, "y": .93, "type": "facility"},
    "SC_BH1":  {"label": "SC Boys-1",  "x": .54, "y": .93, "type": "boys"},
    "SC_BH2":  {"label": "SC Boys-2",  "x": .61, "y": .93, "type": "boys"},
    "SC_GH1":  {"label": "SC Girls-1", "x": .68, "y": .93, "type": "girls"},
    "SC_GH2":  {"label": "SC Girls-2", "x": .75, "y": .93, "type": "girls"},
    "SC_gnd":  {"label": "SC Ground",  "x": .83, "y": .83, "type": "ground"},
}

EDGES = [
    # Gates
    ("g_main","atm",65),("g_main","food1",130),("g_main","adm",165),
    ("g_north","med",90),("g_north","A1",160),
    ("g_south","LC_A",110),("g_south","SE1",200),
    ("g_east","conv",85),("g_east","SK3",155),("g_east","sport",130),
    # North road spine
    ("atm","adm",75),("adm","food1",85),("food1","med",95),
    ("adm","aud",85),("aud","lib",85),("lib","conv",90),
    # A row
    ("A1","A2",85),("A2","A3",85),("A3","D4",85),("D4","D5",85),("D5","D6",85),
    # B row
    ("B1","B2",85),("B2","B3",85),("B3","B4",85),("B4","B5",85),
    # C-D row
    ("C1","C2",85),("C2","C3",85),("C3","D1",85),("D1","D2",85),("D2","D3",85),
    # Vertical A-B
    ("A1","B1",95),("A2","B2",95),("A3","B3",95),("D4","B4",95),("D5","B5",95),
    # Vertical B-C
    ("B1","C1",95),("B2","C2",95),("B3","C3",95),("B4","D1",95),("B5","D2",95),("D6","D3",95),
    # Academic → facilities
    ("A1","med",120),("B1","food1",110),("C1","adm",110),
    ("C2","aud",110),("C3","lib",110),("D1","lib",110),
    ("D2","conv",120),("D3","conv",95),
    ("D5","sport",110),("D6","sport",95),("D5","cric",120),("D6","cric",100),
    ("sport","conv",105),
    # Hostel road
    ("LC_A","LC_B",52),("LC_A","LC_C",85),("LC_C","LC_D",52),("LC_B","LC_D",85),
    ("LC_C","NC1",85),("NC1","NC2",52),("NC1","NC3",85),("NC2","NC4",85),
    ("NC3","NC4",52),("NC3","NC5",85),("NC4","NC6",85),
    ("NC5","NC6",52),("NC5","Zakir",85),("NC6","Zakir",52),
    ("Zakir","SK1",85),("SK1","SK2",62),("SK2","SK3",62),
    ("SK1","GH1",62),("SK2","GH2",62),("GH1","GH2",62),
    # Hostels → academic
    ("LC_A","adm",140),("LC_B","g_south",110),
    ("NC1","C1",140),("NC3","C2",140),("NC5","C3",140),
    ("Zakir","D1",140),("SK1","D2",140),("GH2","D3",140),("SK3","g_east",150),
    # N ↔ S connectors
    ("g_south","SE1",130),("adm","SE1",220),("lib","SF1",220),("conv","SG1",230),
    # South campus
    ("SE1","SE2",85),("SE2","SF1",85),("SF1","SF2",85),("SF2","SG1",85),
    ("SE1","SC_food",95),("SE2","SC_lib",85),("SF1","SC_lib",75),
    ("SF2","SC_BH1",95),("SG1","SC_BH2",95),("SC_BH1","SC_BH2",62),
    ("SG1","SC_GH1",95),("SC_GH1","SC_GH2",62),("SC_GH2","SC_gnd",95),
    ("SG1","SC_gnd",110),("SC_BH1","SC_GH1",85),("SC_food","g_south",115),
    ("SC_food","SC_lib",100),
]

# Campus real dimensions (for admissible heuristic)
CAMPUS_W_M = 900.0   # metres represented by x: 0 → 1
CAMPUS_H_M = 700.0   # metres represented by y: 0 → 1

# Build adjacency list (bidirectional)
graph = {n: [] for n in NODES}
for a, b, d in EDGES:
    graph[a].append({"to": b, "dist": d})
    graph[b].append({"to": a, "dist": d})


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def euclidean(a: str, b: str) -> float:
    """
    Admissible Euclidean heuristic in metres.
    Uses real campus dimensions so h(n) <= true road distance always.
    """
    na, nb = NODES[a], NODES[b]
    dx = (na["x"] - nb["x"]) * CAMPUS_W_M
    dy = (na["y"] - nb["y"]) * CAMPUS_H_M
    return math.sqrt(dx * dx + dy * dy)


def reconstruct_path(prev: dict, src: str, dst: str) -> list:
    """
    Walk backwards from dst to src.
    Stop when we reach src (prev[src] is never set).
    Returns [] if path is disconnected.
    """
    path, cur, guard = [], dst, 0
    while cur is not None and guard < 500:
        path.append(cur)
        if cur == src:
            break
        cur = prev.get(cur)
        guard += 1
    if not path or path[-1] != src:
        return []
    path.reverse()
    return path


# ─── DIJKSTRA ────────────────────────────────────────────────────────────────

def run_dijkstra(src: str, dst: str):
    dist = {n: math.inf for n in NODES}
    prev = {}
    visited = set()
    visit_order = []
    steps = []

    dist[src] = 0
    pq = [(0.0, src)]   # (cost, node)

    while pq:
        cost, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        visit_order.append(u)
        steps.append(f"Visit {NODES[u]['label']} (d={round(cost)}m)")

        if u == dst:
            break

        for edge in graph[u]:
            v, w = edge["to"], edge["dist"]
            if v in visited:
                continue
            alt = dist[u] + w
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))
                steps.append(f"  Relax {NODES[v]['label']}: {round(alt)}m")

    if dist[dst] == math.inf:
        return None

    path = reconstruct_path(prev, src, dst)
    if not path:
        return None

    return {
        "algorithm": "dijkstra",
        "path": path,
        "path_labels": [NODES[n]["label"] for n in path],
        "distance": round(dist[dst]),
        "walk_minutes": round(dist[dst] / 80, 1),
        "nodes_visited": len(visit_order),
        "hops": len(path) - 1,
        "visit_order": visit_order,
        "steps": steps,
    }


# ─── A* ──────────────────────────────────────────────────────────────────────

def run_astar(src: str, dst: str):
    g_cost = {n: math.inf for n in NODES}
    prev = {}
    visited = set()
    visit_order = []
    steps = []

    g_cost[src] = 0
    # pq: (f_cost, g_cost, node) — g_cost as tie-breaker
    pq = [(euclidean(src, dst), 0.0, src)]

    while pq:
        f, g, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        visit_order.append(u)
        h = round(euclidean(u, dst))
        steps.append(f"Visit {NODES[u]['label']} (g={round(g)}m h={h}m f={round(f)}m)")

        if u == dst:
            break

        for edge in graph[u]:
            v, w = edge["to"], edge["dist"]
            if v in visited:
                continue
            tg = g_cost[u] + w
            if tg < g_cost[v]:
                g_cost[v] = tg
                f_new = tg + euclidean(v, dst)
                prev[v] = u
                heapq.heappush(pq, (f_new, tg, v))
                steps.append(f"  Update {NODES[v]['label']}: g={round(tg)}m f={round(f_new)}m")

    if g_cost[dst] == math.inf:
        return None

    path = reconstruct_path(prev, src, dst)
    if not path:
        return None

    return {
        "algorithm": "astar",
        "path": path,
        "path_labels": [NODES[n]["label"] for n in path],
        "distance": round(g_cost[dst]),
        "walk_minutes": round(g_cost[dst] / 80, 1),
        "nodes_visited": len(visit_order),
        "hops": len(path) - 1,
        "visit_order": visit_order,
        "steps": steps,
    }


# ─── ROUTES ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/graph-data", methods=["GET"])
def graph_data():
    """Return the full campus graph."""
    return jsonify({
        "nodes": NODES,
        "edges": [{"from": a, "to": b, "distance": d} for a, b, d in EDGES],
        "node_count": len(NODES),
        "edge_count": len(EDGES),
        "campus_width_m": CAMPUS_W_M,
        "campus_height_m": CAMPUS_H_M,
    })


@app.route("/nodes", methods=["GET"])
def get_nodes():
    """Return node list grouped by type."""
    return jsonify([
        {"id": k, "label": v["label"], "type": v["type"],
         "x": v["x"], "y": v["y"], "connections": len(graph[k])}
        for k, v in NODES.items()
    ])


@app.route("/shortest-path", methods=["GET"])
def shortest_path():
    """
    Query params:
        src     : source node id  (required)
        dst     : destination node id  (required)
        algo    : 'dijkstra' | 'astar'  (default: dijkstra)
        compare : '1' to also run the other algorithm
    """
    src  = request.args.get("src", "").strip()
    dst  = request.args.get("dst", "").strip()
    algo = request.args.get("algo", "dijkstra").strip().lower()
    compare = request.args.get("compare", "0") == "1"

    if not src or not dst:
        return jsonify({"error": "src and dst are required"}), 400
    if src not in NODES:
        return jsonify({"error": f"Unknown source: {src}"}), 400
    if dst not in NODES:
        return jsonify({"error": f"Unknown destination: {dst}"}), 400
    if src == dst:
        return jsonify({"error": "src and dst must differ"}), 400

    primary = run_astar(src, dst) if algo == "astar" else run_dijkstra(src, dst)

    response = {"primary": primary}

    if compare:
        other = run_dijkstra(src, dst) if algo == "astar" else run_astar(src, dst)
        response["comparison"] = other

        if primary and other:
            response["analysis"] = {
                "same_distance": primary["distance"] == other["distance"],
                "dijkstra_visited": (primary if primary["algorithm"] == "dijkstra" else other)["nodes_visited"],
                "astar_visited":    (primary if primary["algorithm"] == "astar"    else other)["nodes_visited"],
                "nodes_saved_by_astar": (
                    (primary if primary["algorithm"] == "dijkstra" else other)["nodes_visited"] -
                    (primary if primary["algorithm"] == "astar"    else other)["nodes_visited"]
                ),
            }

    return jsonify(response)


@app.route("/complexity", methods=["GET"])
def complexity():
    return jsonify({
        "dijkstra": {
            "time":  "O((V + E) log V)",
            "space": "O(V)",
            "heuristic": None,
            "description": "Explores all reachable nodes in order of increasing distance. Optimal. No geometric information needed.",
        },
        "astar": {
            "time":  "O(E) best case, O((V + E) log V) worst case",
            "space": "O(V)",
            "heuristic": "Euclidean distance in metres (admissible)",
            "description": "Uses straight-line distance to goal as a guide. Visits fewer nodes in practice. Optimal when heuristic is admissible.",
        },
    })


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🗺️  Campus PathFinder — Chandigarh University, Mohali")
    print("=" * 56)
    print(f"  Nodes : {len(NODES)}")
    print(f"  Edges : {len(EDGES)}")
    print(f"  Server: http://localhost:5000")
    print("=" * 56)
    print("\nEndpoints:")
    print("  GET /                    → Web interface (index.html)")
    print("  GET /graph-data          → Full campus graph JSON")
    print("  GET /nodes               → Node list with types")
    print("  GET /complexity          → Algorithm complexity info")
    print("  GET /shortest-path?src=A1&dst=SC_gnd&algo=dijkstra")
    print("  GET /shortest-path?src=A1&dst=SC_gnd&algo=astar&compare=1\n")
    app.run(debug=True, host="0.0.0.0", port=5000)