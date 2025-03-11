"""
Queries server for specific obj id details
"""
import sqlite3

def query_object_details(object_id):
    """
    queries the database based on object_id
    """
    conn = sqlite3.connect("lux.sqlite")
    cursor = conn.cursor()
    # Query Summary
    cursor.execute("""
        SELECT 
            o.accession_no,
            o.date, 
            GROUP_CONCAT(DISTINCT p.label) AS place, 
            GROUP_CONCAT(DISTINCT d.name) AS department
        FROM objects o
        LEFT JOIN objects_places op ON o.id = op.obj_id
        LEFT JOIN places p ON op.pl_id = p.id
        LEFT JOIN objects_departments od ON o.id = od.obj_id
        LEFT JOIN departments d ON od.dep_id = d.id
        WHERE o.id = ?;
    """, (object_id,))
    row = cursor.fetchone()

    if not row or row[0] is None:  # No matching object
        return None, "N/A", [], [], []

    if row:
        accession_no, date_val, places_raw, department_raw = row
        # Split places on commas -> then join with newline
        places_list = (places_raw or "").split(",")
        places_formatted = "\n".join(p.strip() for p in places_list if p.strip())
        department_list = (department_raw or "").split(",")
        department_formatted = ", ".join(d.strip() for d in department_list if d.strip())

        summary = (accession_no, date_val, places_formatted, department_formatted)
    else:
        summary = None

    # Query Label
    cursor.execute("SELECT label FROM objects WHERE id = ?", (object_id,))
    label_row = cursor.fetchone()
    label = label_row[0] if label_row else "N/A"

    # Query Produced By
    cursor.execute("""
        SELECT 
            p.part,
            a.name,
            a.begin_date, 
            a.end_date,
            GROUP_CONCAT(n.descriptor, ', ') AS nationalities
        FROM productions p
        JOIN agents a ON p.agt_id = a.id
        LEFT JOIN agents_nationalities an ON a.id = an.agt_id
        LEFT JOIN nationalities n ON an.nat_id = n.id
        WHERE p.obj_id = ?
        GROUP BY p.part, a.name
    """, (object_id,))
    produced_by_rows = cursor.fetchall()

    # Convert each row to (part, name, timespanYear, nationalities)
    processed = []
    for (part, name, begin_date, end_date, nationalities) in produced_by_rows:
        begin_year = (begin_date or "")[:4]  # Birth year
        end_year = (end_date or "")[:4]  # Death year (if available)
        if end_year:  # If the artist is deceased
            timespan = f"{begin_year}-{end_year}"
        else:  # If the artist is alive
            timespan = f"{begin_year}-"
        processed.append((part, name, timespan, nationalities or ""))

    # Now sort by agent name → part → nationality
    produced_by_sorted = sorted(
        processed,
        key=lambda row: (
            row[1].lower(),  # name
            row[0].lower(),  # part
            row[3].lower()   # nationality
        )
    )

    # Query Classifications
    cursor.execute("""
        SELECT c.name 
        FROM objects_classifiers oc
        JOIN classifiers c ON oc.cls_id = c.id
        WHERE oc.obj_id = ?
        ORDER BY LOWER(c.name) ASC;
    """, (object_id,))
    classifications = [row[0] for row in cursor.fetchall()]

    # Query References
    cursor.execute("""
        SELECT r.type, r.content
        FROM "references" r
        WHERE r.obj_id = ?
        ORDER BY r.type;
    """, (object_id,))
    references = cursor.fetchall()
    conn.close()

    return summary, label, produced_by_sorted, classifications, references
