from flask import Flask, request, jsonify, render_template
from calculator import calculate_sip

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health_check():
    return {"status": "SIP calculator API is running"}


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True, silent=True)

    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        result = calculate_sip(
            starting_amount=data["starting_amount"],
            monthly_investment=data["monthly_investment"],
            years=data["years"],
            annual_return_pct=data["annual_return_pct"],
            inflation_pct=data["inflation_pct"],
            brokerage_pct=data.get("brokerage_pct", 0.15),
            sst_pct_of_brokerage=data.get("sst_pct_of_brokerage", 13.0),
            cdc_pct=data.get("cdc_pct", 0.02),
            annual_flat_fee=data.get("annual_flat_fee", 700.0),
            cgt_filer_pct=data.get("cgt_filer_pct", 15.0),
            cgt_nonfiler_pct=data.get("cgt_nonfiler_pct", 30.0),
        )
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)