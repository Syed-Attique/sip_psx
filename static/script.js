const fmt = (n) => {
  if (n === null || n === undefined || Number.isNaN(n)) return "\u2014";
  return "Rs " + Math.round(n).toLocaleString("en-PK");
};

function readInputs() {
  const ids = [
    "starting_amount", "monthly_investment", "years",
    "annual_return_pct", "inflation_pct",
    "brokerage_pct", "sst_pct_of_brokerage", "cdc_pct",
    "annual_flat_fee", "cgt_filer_pct", "cgt_nonfiler_pct",
  ];
  const payload = {};
  for (const id of ids) {
    payload[id] = parseFloat(document.getElementById(id).value);
  }
  return payload;
}

async function runCalculation(event) {
  event.preventDefault();
  const errorEl = document.getElementById("error-msg");
  errorEl.textContent = "";

  const payload = readInputs();

  let res;
  try {
    res = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    errorEl.textContent = "Could not reach the calculator server.";
    return;
  }

  const data = await res.json();

  if (!res.ok) {
    errorEl.textContent = data.error || "Something went wrong.";
    return;
  }

  document.getElementById("empty-state").classList.add("hidden");
  document.getElementById("results-content").classList.remove("hidden");

  document.getElementById("slip-date").textContent = new Date().toLocaleDateString("en-GB", {
    day: "2-digit", month: "short", year: "numeric",
  });

  document.getElementById("out-contributed").textContent = fmt(data.total_contributed);
  document.getElementById("out-purchase-fees").textContent = "(" + fmt(data.total_purchase_fees) + ")";
  document.getElementById("out-annual-fees").textContent = "(" + fmt(data.annual_fees_paid) + ")";
  document.getElementById("out-cost-basis").textContent = fmt(data.cost_basis);
  document.getElementById("out-gross").textContent = fmt(data.gross_value);
  document.getElementById("out-gain").textContent = fmt(data.gain);

  document.getElementById("cgt-filer-rate").textContent = payload.cgt_filer_pct;
  document.getElementById("out-cgt-filer").textContent = "(" + fmt(data.cgt_filer) + ")";
  document.getElementById("out-net-filer").textContent = fmt(data.net_value_filer);
  document.getElementById("out-real-filer").textContent = fmt(data.real_value_filer);

  document.getElementById("cgt-nonfiler-rate").textContent = payload.cgt_nonfiler_pct;
  document.getElementById("out-cgt-nonfiler").textContent = "(" + fmt(data.cgt_nonfiler) + ")";
  document.getElementById("out-net-nonfiler").textContent = fmt(data.net_value_nonfiler);
  document.getElementById("out-real-nonfiler").textContent = fmt(data.real_value_nonfiler);
}

document.getElementById("calc-form").addEventListener("submit", runCalculation);