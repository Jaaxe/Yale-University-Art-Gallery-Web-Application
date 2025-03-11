"""
Application to run flask and endpoints
"""
import urllib.request
import urllib.error

from flask import Flask, render_template, request, make_response
from markupsafe import escape

from luxlist import query_database
from luxdetails import query_object_details

app = Flask(__name__)


@app.route('/')
def index():
    """
    Display the index page with caching
    """
    last_label = request.cookies.get('l', '')
    last_classifier = request.cookies.get('c', '')
    last_agent = request.cookies.get('a', '')
    last_date = request.cookies.get('d', '')

    results = None
    message = None

    # Check if there was a previous search (non-empty cookies)
    has_previous_search = any([last_label, last_classifier, last_agent, last_date])

    if has_previous_search:
        # Re-run the search using cached parameters
        all_empty = all(
            param == '' for param in [last_label, last_classifier, last_agent, last_date]
            )

        if all_empty:
            message = "No search terms provided. Please enter some search terms."
        else:
            # Query the database with cached parameters
            results = query_database(
                last_date,
                last_agent,
                last_classifier,
                last_label
            )

    return render_template(
        'index.html',
        last_label=last_label,
        last_classifier=last_classifier,
        last_agent=last_agent,
        last_date=last_date,
        results=results,
        message=message
    )


@app.route('/search')
def search():
    """
    Displays the page after searching the database
    """
    params = {
        'label': request.args.get('l', ''),
        'classifier': request.args.get('c', ''),
        'agent': request.args.get('a', ''),
        'date': request.args.get('d', '')
    }

    results = None
    message = None

    all_empty = all(value == '' for value in params.values())

    if all_empty:
        message="No search terms provided. Please enter some search terms."

    else:
        results = query_database(
            params['date'],
            params['agent'],
            params['classifier'],
            params['label']
        )
    response = make_response(render_template(
        'index.html',
        last_label=params['label'],
        last_classifier=params['classifier'],
        last_agent=params['agent'],
        last_date=params['date'],
        results=results,
        message=message
    ))

    # Set cookies to persist search parameters
    response.set_cookie('l', params['label'])
    response.set_cookie('c', params['classifier'])
    response.set_cookie('a', params['agent'])
    response.set_cookie('d', params['date'])

    return response

def object_image_exists(obj_id):
    """
    Checks if an image for this object is available at 
    https://media.collections.yale.edu/thumbnail/yuag/obj/<obj_id>.
    Returns True if we get a 200 OK response, else False.
    """
    url = f"https://media.collections.yale.edu/thumbnail/yuag/obj/{obj_id}"
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError):
        return False

@app.route("/obj/<path:obj_id>")
def show_object(obj_id):
    """
    Display the page when clicking on specific object
    calls detail query to query specific object_id
    """
    # Return error if obj id not int
    try:
        num_id = int(obj_id)
    except ValueError:
        return f"Error: no object with id {escape(obj_id)} exists", 404

    summary, label, produced_by, classifications, references = query_object_details(num_id)

    if not summary:
        return f"Error: no object with id {escape(obj_id)} exists", 404

    # Check for image
    has_img = object_image_exists(num_id)
    image_url = None
    if has_img:
        image_url = f"https://media.collections.yale.edu/thumbnail/yuag/obj/{num_id}"

    (accession_no, date_val, places_formatted, department_str) = summary
    return render_template(
        "details.html",
        obj_id=obj_id,
        accession_no=accession_no,
        date_val=date_val,
        places_formatted=places_formatted,
        department_str=department_str,
        label=label,
        produced_by=produced_by,
        classifications=classifications,
        references=references,
        image_url=image_url
    )

@app.route("/obj")
def obj_missing():
    """
    Display error message if not obj id
    """
    # Return error if obj missing
    return "Error: missing object id.", 404

@app.errorhandler(404)

def not_found(e):
    """
    Return "Error: exception" for any unknown route.
    """
    return f"Error: {e}", 404
