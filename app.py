from flask import Flask, render_template, request
from estimator import (
    get_shipment_types,
    get_origins_for_type,
    get_destinations_for_type_origin,
    calculate_quote,
)
from map_utils import create_route_map_default, create_route_map_with_route

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    shipment_types = get_shipment_types()
    selected_type = request.form.get("shipment_type") or (shipment_types[0] if shipment_types else "")

    # filter origins by selected type
    origins = get_origins_for_type(selected_type)
    selected_origin = request.form.get("origin") or (origins[0] if origins else "")

    # filter destinations by selected type + selected origin
    destinations = get_destinations_for_type_origin(selected_type, selected_origin) if selected_origin else []
    selected_destination = request.form.get("destination") or (destinations[0] if destinations else "")

    quote = None
    fmap_html = create_route_map_default()._repr_html_()

    if request.method == "POST" and selected_origin and selected_destination:
        quote = calculate_quote(selected_type, selected_origin, selected_destination)
        if quote and not quote.get("error") and quote.get("origin_coords") and quote.get("dest_coords"):
            fmap_html = create_route_map_with_route(
                selected_type, quote["origin_coords"], quote["dest_coords"]
            )._repr_html_()

    return render_template(
        "index.html",
        shipment_types=shipment_types,
        selected_type=selected_type,
        origins=origins,
        selected_origin=selected_origin,
        destinations=destinations,
        selected_destination=selected_destination,
        quote=quote,
        map_html=fmap_html,
    )

if __name__ == "__main__":
    app.run(debug=True)
