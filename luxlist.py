"""
Queries the database sqlite for info
"""
import sqlite3


def query_database(date, agt, cls, label):
    """
    queries the database based on the inputs date, agt, cls, label
    """
    conn = sqlite3.connect("lux.sqlite")
    cursor = conn.cursor()
    #base query
    query = """
    SELECT 
        o.id, 
        o.label, 
        o.date, 
        (
            SELECT GROUP_CONCAT(DISTINCT agent_part)
            FROM (
                SELECT a.name || ' (' || p.part || ')' AS agent_part
                FROM productions p
                JOIN agents a ON p.agt_id = a.id
                WHERE p.obj_id = o.id
                ORDER BY a.name ASC, p.part ASC
            )
        ) AS sorted_agents,
        (   
            SELECT GROUP_CONCAT(cls_name, "||")
            FROM (
                SELECT DISTINCT cls_name 
                FROM(
                    SELECT c.name AS cls_name
                    FROM objects_classifiers oc
                    JOIN classifiers c ON oc.cls_id = c.id
                    WHERE oc.obj_id = o.id
                    ORDER BY LOWER(c.name) ASC
                ) 
            )
        ) AS ordered_classifiers

    FROM objects o
        LEFT JOIN productions p ON p.obj_id == o.id
        LEFT JOIN agents a ON a.id == p.agt_id
        LEFT JOIN objects_classifiers oc ON o.id == oc.obj_id
        LEFT JOIN classifiers c ON c.id == oc.cls_id
        WHERE 1=1
    """
    params = []

    #conditionals to add onto base query
    if date:
        query += " AND o.date LIKE ?"
        params.append(f"%{date}%")
    if agt:
        query += " AND a.name LIKE ?"
        params.append(f"%{agt}%")
    if cls:
        query += " AND c.name LIKE ?"
        params.append(f"%{cls}%")
    if label:
        query += " AND o.label LIKE ?"
        params.append(f"%{label}%")

    query += """
    GROUP BY o.id
    ORDER BY o.label ASC, o.date ASC
    LIMIT 1000
    """

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results
