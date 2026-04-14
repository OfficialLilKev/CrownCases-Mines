"""
CrownCases Mines — Flask Backend
Provably fair, hypergeometric multipliers, strict game-state enforcement.
"""

import hashlib
import os
import secrets
from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

GRID_SIZE   = 25
HOUSE_EDGE  = 0.97   # 3% house edge factor


# ──────────────────────────────────────────────────────────────
# Math
# ──────────────────────────────────────────────────────────────

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def multiplier_table(mines: int) -> list[float]:
    """
    Returns a list of length (totalGems + 1) where index k is the
    multiplier AFTER k successful (gem) picks.

    Uses the hypergeometric model:
        mult[k] = HOUSE_EDGE / P(all k picks are gems)
        P(k)    = product_{i=0}^{k-1}  (totalGems - i) / (totalTiles - i)

    mult[0] is always 1.00 — the starting state before any pick.
    """
    total_gems = GRID_SIZE - mines
    table = [1.0]
    prob = 1.0
    for k in range(1, total_gems + 1):
        prob *= (total_gems - (k - 1)) / (GRID_SIZE - (k - 1))
        table.append(round(HOUSE_EDGE / prob, 2))
    return table


def derive_mines(server_seed: str, client_seed: str, nonce: int, count: int):
    """
    Fisher-Yates pool selection driven by SHA-256 hash bytes.
    Returns (positions: list[int], result_hash: str)
    """
    combined    = f"{server_seed}:{client_seed}:{nonce}"
    result_hash = sha256(combined)

    hex_str = result_hash
    # Extend entropy if needed
    def get_bytes(h):
        return [int(h[i:i+2], 16) for i in range(0, len(h), 2)]

    byte_pool = get_bytes(hex_str)
    pool      = list(range(GRID_SIZE))
    positions = []
    bi        = 0

    while len(positions) < count:
        if bi >= len(byte_pool):
            ext = sha256(result_hash + ":" + str(bi))
            byte_pool += get_bytes(ext)
        pick = byte_pool[bi] % len(pool)
        positions.append(pool.pop(pick))
        bi += 1

    return positions, result_hash


def validate_mine_count(v):
    return max(1, min(24, int(v)))


def validate_bet(v):
    return max(0.01, float(v))


# ──────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/seeds", methods=["GET"])
def get_seeds():
    """Return current server seed hash and nonce (never the raw seed)."""
    if "server_seed" not in session:
        session["server_seed"] = secrets.token_hex(32)
        session["nonce"] = 0
    return jsonify({
        "server_seed_hash": sha256(session["server_seed"]),
        "nonce": session.get("nonce", 0),
    })


@app.route("/api/seeds/rotate", methods=["POST"])
def rotate_seed():
    """Rotate server seed. Only allowed when no active game."""
    if session.get("game", {}).get("active"):
        return jsonify({"error": "Cannot rotate seed during an active round."}), 400

    old_seed = session.get("server_seed", "")
    session["server_seed"] = secrets.token_hex(32)
    session["nonce"]       = 0

    return jsonify({
        "revealed_server_seed": old_seed,
        "old_hash":             sha256(old_seed) if old_seed else "",
        "new_server_seed_hash": sha256(session["server_seed"]),
        "nonce": 0,
    })


@app.route("/api/start", methods=["POST"])
def start_game():
    """
    Start a new round. Rejected if a round is already active.
    Locks bet amount and mine count for the duration.
    """
    # Reject if a round is already active
    if session.get("game", {}).get("active"):
        return jsonify({"error": "A round is already in progress. Finish it first."}), 400

    data        = request.get_json(silent=True) or {}
    bet         = validate_bet(data.get("bet", 10))
    mines       = validate_mine_count(data.get("mines", 3))
    client_seed = str(data.get("client_seed", secrets.token_hex(8)))

    if "server_seed" not in session:
        session["server_seed"] = secrets.token_hex(32)
        session["nonce"]       = 0

    server_seed = session["server_seed"]
    nonce       = session.get("nonce", 0)

    positions, result_hash = derive_mines(server_seed, client_seed, nonce, mines)
    grid = ["bomb" if i in positions else "gem" for i in range(GRID_SIZE)]
    table = multiplier_table(mines)

    session["game"] = {
        "active":      True,
        "grid":        grid,
        "bet":         bet,
        "mines":       mines,
        "client_seed": client_seed,
        "nonce":       nonce,
        "result_hash": result_hash,
        "positions":   positions,
        "revealed":    [],
        "gems_found":  0,
        "mult_table":  table,
        "multiplier":  table[0],
        "over":        False,
    }
    session["nonce"] = nonce + 1

    return jsonify({
        "status":             "started",
        "server_seed_hash":   sha256(server_seed),   # commitment — raw seed stays hidden
        "client_seed":        client_seed,
        "nonce":              nonce,
        "multiplier":         table[0],
        "potential_winnings": round(bet * table[0], 2),
        # result_hash NOT returned here — revealed after round ends
    })


@app.route("/api/reveal", methods=["POST"])
def reveal_tile():
    """Reveal a tile. Returns gem or bomb."""
    game = session.get("game")
    if not game or not game.get("active") or game.get("over"):
        return jsonify({"error": "No active round."}), 400

    data  = request.get_json(silent=True) or {}
    index = int(data.get("index", -1))

    if index < 0 or index >= GRID_SIZE:
        return jsonify({"error": "Invalid tile."}), 400
    if index in game["revealed"]:
        return jsonify({"error": "Already revealed."}), 400

    grid      = game["grid"]
    bet       = game["bet"]
    mines     = game["mines"]
    table     = game["mult_table"]
    revealed  = game["revealed"]

    revealed.append(index)

    if grid[index] == "bomb":
        game["over"]   = True
        game["active"] = False
        session["game"] = game

        # Reveal server seed so player can verify
        return jsonify({
            "result":        "bomb",
            "bomb_positions": game["positions"],
            "result_hash":   game["result_hash"],
            "server_seed":   session.get("server_seed", ""),  # revealed on loss
            "client_seed":   game["client_seed"],
            "nonce":         game["nonce"],
            "payout":        0,
            "message":       f"Blown up! Lost ${bet:.2f}",
        })

    # Gem hit
    gems_found = len([i for i in revealed if grid[i] == "gem"])
    multiplier = table[gems_found] if gems_found < len(table) else table[-1]
    game["gems_found"] = gems_found
    game["multiplier"] = multiplier
    game["revealed"]   = revealed

    total_gems = GRID_SIZE - mines
    cleared    = gems_found >= total_gems
    potential  = round(bet * multiplier, 2)

    if cleared:
        game["over"]   = True
        game["active"] = False

    session["game"] = game

    resp = {
        "result":             "gem",
        "multiplier":         multiplier,
        "potential_winnings": potential,
        "cleared":            cleared,
        "message":            f"All clear! Won ${potential}" if cleared else None,
    }
    if cleared:
        resp["server_seed"]    = session.get("server_seed", "")
        resp["result_hash"]    = game["result_hash"]
        resp["bomb_positions"] = game["positions"]

    return jsonify(resp)


@app.route("/api/cashout", methods=["POST"])
def cashout():
    """Cash out. Only valid during an active round with at least one gem revealed."""
    game = session.get("game")
    if not game or not game.get("active") or game.get("over"):
        return jsonify({"error": "No active round."}), 400
    if game.get("gems_found", 0) == 0:
        return jsonify({"error": "Reveal at least one gem before cashing out."}), 400

    bet        = game["bet"]
    multiplier = game["multiplier"]
    winnings   = round(bet * multiplier, 2)
    game["over"]   = True
    game["active"] = False
    session["game"] = game

    return jsonify({
        "status":          "cashed_out",
        "multiplier":      multiplier,
        "winnings":        winnings,
        "server_seed":     session.get("server_seed", ""),
        "client_seed":     game["client_seed"],
        "nonce":           game["nonce"],
        "result_hash":     game["result_hash"],
        "bomb_positions":  game["positions"],
        "message":         f"Cashed out ${winnings}!",
    })


@app.route("/api/verify", methods=["POST"])
def verify():
    """
    Independent verification endpoint.
    Provide server_seed, client_seed, nonce, mine_count (and optionally
    claimed result_hash and positions) — server recalculates and confirms.
    """
    data            = request.get_json(silent=True) or {}
    server_seed     = str(data.get("server_seed", ""))
    client_seed     = str(data.get("client_seed", ""))
    nonce           = int(data.get("nonce", 0))
    mine_count      = validate_mine_count(data.get("mine_count", 3))
    claimed_hash    = str(data.get("result_hash", ""))
    claimed_pos     = data.get("positions", [])

    if not server_seed or not client_seed:
        return jsonify({"error": "Missing server_seed or client_seed."}), 400

    positions, result_hash = derive_mines(server_seed, client_seed, nonce, mine_count)

    hash_match = result_hash == claimed_hash if claimed_hash else None
    pos_match  = (sorted(positions) == sorted(int(p) for p in claimed_pos)) if claimed_pos else None

    return jsonify({
        "valid":                 (hash_match is not False) and (pos_match is not False),
        "hash_match":            hash_match,
        "positions_match":       pos_match,
        "recalculated_hash":     result_hash,
        "recalculated_positions": positions,
        "server_seed_hash":      sha256(server_seed),
    })


@app.route("/api/multiplier_table", methods=["GET"])
def get_multiplier_table():
    """Return the full multiplier table for a given mine count (for frontend preview)."""
    mines = validate_mine_count(request.args.get("mines", 3))
    return jsonify({
        "mines": mines,
        "table": multiplier_table(mines),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
