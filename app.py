from flask import Flask, render_template, request
from estimator import (
    get_types, get_origins, get_destinations,
    calculate_quote, create_route_map
)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    quote = None
    map_html = None

    types = get_types()
    origins = get_origins()
    destinations = get_destinations()

    if request.method == "POST":
        shipment_type = request.form["shipment_type"]
        origin = request.form["origin"]
        destination = request.form["destination"]

        quote = calculate_quote(shipment_type, origin, destination)
        map_html = create_route_map(origin, destination, shipment_type)

    return render_template("index.html", types=types, origins=origins,
                           destinations=destinations, quote=quote,
                           map_html=map_html)

if __name__ == "__main__":
    app.run(debug=True)

