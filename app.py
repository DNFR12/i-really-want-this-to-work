from flask import Flask, render_template, request
from estimator import (
    get_shipment_types,
    get_known_destinations,
    estimate_freight
)
from map_utils import create_route_map

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    shipment_types = get_shipment_types()
    known_destinations = get_known_destinations()
    quote = None
    route_map = None

    if request.method == "POST":
        shipment_type = request.form.get("shipment_type")
        origin = request.form.get("origin")
        destination = request.form.get("destination")

        quote = estimate_freight(shipment_type, origin, destination)

        if "origin_coords" in quote and "dest_coords" in quote:
            route_map = create_route_map(
                shipment_type,
                quote["origin_coords"],
                quote["dest_coords"]
            )

    return render_template(
        "index.html",
        shipment_types=shipment_types,
        known_destinations=known_destinations,
        quote=quote,
        route_map=route_map._repr_html_() if route_map else None
    )

if __name__ == "__main__":
    app.run(debug=True)
