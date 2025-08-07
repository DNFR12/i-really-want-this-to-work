from flask import Flask, render_template, request
from estimator import (
    get_shipment_types,
    get_unique_locations,
    calculate_quote,
)
from map_utils import create_map

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    shipment_types = get_shipment_types()
    origins, destinations = get_unique_locations()

    quote_result = None
    map_html = create_map()  # default map

    if request.method == 'POST':
        shipment_type = request.form['shipment_type']
        origin = request.form['origin']
        destination = request.form['destination']

        quote_result = calculate_quote(shipment_type, origin, destination)
        map_html = create_map(origin, destination, shipment_type)

    return render_template(
        'index.html',
        shipment_types=shipment_types,
        origins=origins,
        destinations=destinations,
        quote_result=quote_result,
        map_html=map_html
    )

if __name__ == '__main__':
    app.run(debug=True)
