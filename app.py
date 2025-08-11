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

    origins = get_origins_for_type(selected_type)
    selected_origin = request.form.get("origin") or (origins[0] if origins else "")

    destinations = get_destinations_for_type_origin(selected_type, selected_origin) if selected_origin else []
    # If user chooses unknown destination, dropdown may be empty/ignored
    selected_destination = request.form.get("destination") or ""

    use_custom = request.form.get("use_custom") == "on"
    custom_city = request.form.get("custom_city") if use_custom else None

    quote = None
    fmap_html = create_route_map_default()._repr_html_()

    if request.method == "POST" and selected_origin:
        # If custom destination requested, ignore dropdown destination
        destination_arg = None if use_custom else (selected_destination or None)
        quote = calculate_quote(selected_type, selected_origin, destination_arg, custom_city)

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
        use_custom=use_custom,
        custom_city=custom_city or "",
        quote=quote,
        map_html=fmap_html,
    )

if __name__ == "__main__":
    app.run(debug=True)
