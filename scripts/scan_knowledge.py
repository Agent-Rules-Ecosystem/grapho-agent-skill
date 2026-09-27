#!/usr/bin/env python3
"""
scan_knowledge.py — Deterministic Knowledge & Lore Graph Indexer (Grapho Agent Skill)
Parses Markdown files with YAML Frontmatter, validates schema integrity,
builds an SQLite database with FTS5 full-text search, and enables surgical,
low-token JSON queries.
"""

import os
import sys
import re
import json
import sqlite3
import argparse
from pathlib import Path

# Optional YAML parser with fallback to simple parser if PyYAML is not installed
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def parse_simple_yaml(yaml_text):
    """Fallback simple YAML parser for frontmatters without PyYAML."""
    data = {}
    lines = yaml_text.strip().split('\n')
    current_key = None
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith('#'):
            continue
        
        # Key-value pair at root
        if ':' in line and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('-'):
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip()
            current_key = key
            
            if not val:
                data[key] = {}
            elif val.startswith('[') and val.endswith(']'):
                # Inline list
                items = [item.strip().strip('"\'') for item in val[1:-1].split(',') if item.strip()]
                data[key] = items
            elif val.lower() in ('true', 'yes'):
                data[key] = True
            elif val.lower() in ('false', 'no'):
                data[key] = False
            elif (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                data[key] = val[1:-1]
            else:
                data[key] = val
        elif line_clean.startswith('- ') and current_key:
            item_val = line_clean[2:].strip().strip('"\'')
            if not isinstance(data.get(current_key), list):
                data[current_key] = []
            data[current_key].append(item_val)
            
    return data

def extract_frontmatter_and_body(content):
    """Extract YAML frontmatter and markdown body from file content."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        raw_yaml = match.group(1)
        body = match.group(2)
        try:
            if HAS_YAML:
                parsed_yaml = yaml.safe_load(raw_yaml) or {}
            else:
                parsed_yaml = parse_simple_yaml(raw_yaml)
        except Exception:
            parsed_yaml = parse_simple_yaml(raw_yaml)
        return parsed_yaml, body, raw_yaml
    return {}, content, ""

def extract_title(body, file_path):
    """Extract first H1 title from body or use file stem."""
    match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return Path(file_path).stem

def init_db(db_path):
    """Initialize SQLite database with schema and FTS5 tables."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        path TEXT UNIQUE,
        title TEXT,
        type TEXT,
        status TEXT,
        epistemology TEXT,
        is_canon INTEGER DEFAULT 1,
        created TEXT,
        updated TEXT,
        tags TEXT,
        raw_yaml TEXT,
        body TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS relations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT,
        target_id TEXT,
        relation_type TEXT,
        notes TEXT,
        FOREIGN KEY(source_id) REFERENCES nodes(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS constants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        param_key TEXT,
        param_value TEXT,
        unit TEXT,
        domain TEXT,
        source_path TEXT
    )
    """)
    
    # FTS5 Full-Text Search Table
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
        id,
        title,
        type,
        tags,
        body,
        content='nodes',
        content_rowid='rowid'
    )
    """)
    
    conn.commit()
    return conn

def scan_repository(root_dir, scan_dirs=None, db_path="overview/grapho/knowledge.db"):
    """Scan markdown files and build the SQLite index."""
    conn = init_db(db_path)
    cursor = conn.cursor()
    
    # Clear previous indexed records
    cursor.execute("DELETE FROM nodes")
    cursor.execute("DELETE FROM relations")
    cursor.execute("DELETE FROM constants")
    cursor.execute("DELETE FROM nodes_fts")
    
    default_dirs = ["overview", "docs", "knowledge", "00_Nucleo", "01_Lore", "02_Sistema", "03_Entidades", "04_Web3"]
    target_dirs = scan_dirs if scan_dirs else default_dirs
    
    scanned_files = 0
    indexed_nodes = 0
    duplicate_ids = []
    
    for d in target_dirs:
        dir_path = os.path.join(root_dir, d)
        if not os.path.exists(dir_path):
            continue
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if not file.endswith(".md"):
                    continue
                
                scanned_files += 1
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, root_dir)
                
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    print(f"⚠️ Error reading {rel_path}: {e}", file=sys.stderr)
                    continue
                
                frontmatter, body, raw_yaml = extract_frontmatter_and_body(content)
                title = extract_title(body, full_path)
                
                # Derive node ID (fallback to slugified relative path if not in frontmatter)
                node_id = frontmatter.get("id")
                if not node_id:
                    node_id = rel_path.replace("/", "-").replace("\\", "-").replace(".md", "")
                
                node_type = str(frontmatter.get("tipo") or frontmatter.get("type") or "documento")
                node_status = str(frontmatter.get("estado") or frontmatter.get("status") or "active")
                
                # Epistemology
                epist = frontmatter.get("epistemologia")
                if isinstance(epist, dict):
                    epist_level = epist.get("level", "canon")
                    is_canon = 1 if epist.get("is_canon", True) else 0
                elif isinstance(epist, str):
                    epist_level = epist
                    is_canon = 1 if epist.lower() == "canon" else 0
                else:
                    epist_level = "canon"
                    is_canon = 1
                
                created = str(frontmatter.get("creado") or frontmatter.get("created") or "")
                updated = str(frontmatter.get("actualizado") or frontmatter.get("updated") or "")
                
                tags = frontmatter.get("tags", [])
                tags_str = json.dumps(tags) if isinstance(tags, list) else str(tags)
                
                try:
                    cursor.execute("""
                    INSERT INTO nodes (id, path, title, type, status, epistemology, is_canon, created, updated, tags, raw_yaml, body)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (node_id, rel_path, title, node_type, node_status, epist_level, is_canon, created, updated, tags_str, raw_yaml, body))
                    indexed_nodes += 1
                except sqlite3.IntegrityError:
                    duplicate_ids.append((node_id, rel_path))
                    # Insert with unique fallback path
                    alt_id = f"{node_id}__dup_{indexed_nodes}"
                    cursor.execute("""
                    INSERT OR REPLACE INTO nodes (id, path, title, type, status, epistemology, is_canon, created, updated, tags, raw_yaml, body)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (alt_id, rel_path, title, node_type, node_status, epist_level, is_canon, created, updated, tags_str, raw_yaml, body))
                
                # Index relations
                relations = frontmatter.get("relations") or frontmatter.get("relaciones") or []
                if isinstance(relations, list):
                    for rel in relations:
                        if isinstance(rel, dict):
                            target = rel.get("target") or rel.get("destino")
                            rel_type = rel.get("type") or rel.get("tipo") or "relacionado"
                            notes = rel.get("notes") or rel.get("notas") or ""
                            if target:
                                cursor.execute("""
                                INSERT INTO relations (source_id, target_id, relation_type, notes)
                                VALUES (?, ?, ?, ?)
                                """, (node_id, target, rel_type, notes))
                        elif isinstance(rel, str) and "→" in rel:
                            # Parse inline string relation: → depende_de → [[ID]]: desc
                            parts = [p.strip() for p in rel.split("→") if p.strip()]
                            if len(parts) >= 2:
                                rel_type = parts[0]
                                target_raw = parts[1].replace("[[", "").replace("]]", "").split(":")[0].strip()
                                cursor.execute("""
                                INSERT INTO relations (source_id, target_id, relation_type, notes)
                                VALUES (?, ?, ?, ?)
                                """, (node_id, target_raw, rel_type, ""))

    # Populate FTS5 index
    cursor.execute("""
    INSERT INTO nodes_fts (rowid, id, title, type, tags, body)
    SELECT rowid, id, title, type, tags, body FROM nodes
    """)
    
    conn.commit()
    
    # Audit broken relations
    cursor.execute("""
    SELECT r.source_id, r.target_id, r.relation_type, n.path
    FROM relations r
    LEFT JOIN nodes n ON r.source_id = n.id
    WHERE r.target_id NOT IN (SELECT id FROM nodes)
    """)
    broken_relations = cursor.fetchall()
    
    stats = {
        "scanned_files": scanned_files,
        "indexed_nodes": indexed_nodes,
        "duplicate_ids": duplicate_ids,
        "broken_relations_count": len(broken_relations),
        "broken_relations": [{"source": b[0], "target": b[1], "type": b[2], "file": b[3]} for b in broken_relations[:10]],
        "db_path": db_path
    }
    
    conn.close()
    return stats

def run_query(query, db_path="overview/grapho/knowledge.db"):
    """Execute raw SQL query and return JSON results."""
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}. Run --scan first."}
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"count": len(rows), "results": rows}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

def run_search(search_term, db_path="overview/grapho/knowledge.db"):
    """Search nodes using FTS5."""
    if not os.path.exists(db_path):
        return {"error": f"Database not found at {db_path}. Run --scan first."}
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT n.id, n.title, n.type, n.status, n.path, snippet(nodes_fts, 4, '<b>', '</b>', '...', 15) as excerpt
        FROM nodes_fts f
        JOIN nodes n ON f.rowid = n.rowid
        WHERE nodes_fts MATCH ?
        ORDER BY rank
        LIMIT 10
        """, (search_term,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"count": len(rows), "results": rows}
    except Exception as e:
        conn.close()
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Deterministic Knowledge Graph Scanner")
    parser.add_argument("--scan", nargs="*", help="Scan directories and build SQLite index")
    parser.add_argument("--root", default=".", help="Workspace root directory")
    parser.add_argument("--db", default="overview/grapho/knowledge.db", help="SQLite database path")
    parser.add_argument("--query", "-q", help="Run SQL query and return JSON")
    parser.add_argument("--find", "-f", help="Full-text search query via FTS5")
    parser.add_argument("--audit", action="store_true", help="Run health audit on knowledge base")
    
    args = parser.parse_args()
    
    if args.scan is not None:
        dirs = args.scan if len(args.scan) > 0 else None
        res = scan_repository(args.root, dirs, args.db)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.query:
        res = run_query(args.query, args.db)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.find:
        res = run_search(args.find, args.db)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.audit:
        scan_res = scan_repository(args.root, None, args.db)
        print(json.dumps({
            "status": "healthy" if scan_res["broken_relations_count"] == 0 and len(scan_res["duplicate_ids"]) == 0 else "degraded",
            "audit_summary": scan_res
        }, indent=2, ensure_ascii=False))
    else:
        # Default action: scan root
        res = scan_repository(args.root, None, args.db)
        print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
