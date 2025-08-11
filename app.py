from flask import Flask, render_template, request
from estimator import (
    get_shipment_types,
    get_origins_for_type,
    get_destinations_for_type,
    calculate_quote,
)
from map_utils import create_route_map_default, create_route_map_with_route

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    types = get_shipment_types()
    # selected type: first one by default
    selected_type = request.form.get("shipment_type") or (types[0] if types else "")

    # lists filtered by selected type
    origins = get_origins_for_type(selected_type)
    destinations = get_destinations_for_type(selected_type)

    quote = None
    # default map on first load
    fmap_html = create_route_map_default()._repr_html_()

    if request.method == "POST":
        origin = request.form.get("origin")
        destination = request.form.get("destination")
        quote = calculate_quote(selected_type, origin, destination)

        if quote and quote.get("origin_coords") and quote.get("dest_coords"):
            fmap_html = create_route_map_with_route(
                selected_type, quote["origin_coords"], quote["dest_coords"]
            )._repr_html_()

    return render_template(
        "index.html",
        shipment_types=types,
        selected_type=selected_type,
        origins=origins,
        destinations=destinations,
        quote=quote,
        map_html=fmap_html,
    )

if __name__ == "__main__":
    app.run(debug=True)
