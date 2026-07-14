# KSE-100 SIP Calculator

A highly accurate, visually asthetic Systematic Investment Plan (SIP) calculator designed specifically for the Pakistan Stock Exchange (KSE-100). 

Unlike standard SIP calculators, this tool factors in real-world costs native to the PSX ecosystem, including brokerage fees, CDC handling charges, Sindh Sales Tax (SST), Capital Gains Tax (CGT) based on Filer status, and the eroding effect of inflation.

---

## 🚀 Features

- **Premium UI/UX:** A dark, sleek "fintech dashboard" aesthetic built with native CSS (no heavy frameworks). Features micro-animations and responsive layouts.
- **Real-World Net Returns:** Accurately subtracts all Pakistani regulatory and brokerage fees.
- **Filer / Non-Filer Support:** Dynamic Capital Gains Tax calculation via an interactive UI toggle.
- **Inflation Adjustment:** Calculates both nominal (Gross) returns and purchasing power (Real) returns.
- **Production-Ready Backend:** Built on Flask with built-in API rate limiting (`Flask-Limiter`) and strict numeric upper-bounds to protect against DoS attacks and Math Overflows.

---

## 🧮 The Mathematics & Logic

The calculation engine evaluates the portfolio month-by-month.

### 1. Gross Investment Growth
Instead of a simple generic SIP formula, the portfolio grows iteratively.
For each month:
1. The **Monthly Investment** is added to the balance.
2. The portfolio grows by the **Monthly Return Rate** `(Annual Return / 12)`.
   
*(If a Starting Amount is provided, it is added in Month 1 and compounds over the entire duration).*

### 2. Transaction Costs (Deducted at Purchase)
Every time a monthly deposit is made, buying shares incurs fees. These fees are deducted from the investment *before* it compounds:
- **Brokerage Fee:** `Investment × Brokerage Rate (e.g., 0.15%)`
- **Sindh Sales Tax (SST):** `Brokerage Fee × SST Rate (e.g., 13%)`
- **CDC Handling Fee:** `Investment × CDC Rate (e.g., 0.02%)`

### 3. Annual Flat Fees & Step-Up SIP
At the end of every 12th month:
- The NCCPL/CDC account maintenance fee (e.g., Rs 700) is subtracted from the portfolio balance.
- If an **Annual Step-Up (%)** is provided, the monthly investment amount is increased by this percentage for the following year to simulate salary growth and increasing contributions.

### 4. Capital Gains Tax (CGT)
Calculated only on the **Net Profit**.
- `Profit = Gross Value - (Total Contributed + Total Purchase Fees + Total Annual Fees)`
- `CGT = Profit × Filer Rate (15%)` OR `Profit × Non-Filer Rate (30%)`

### 5. Inflation & Real Value
To show the actual purchasing power of the final amount:
- **Real Value** = `Net Value after CGT / ((1 + Annual Inflation Rate) ^ Years)`

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-Limiter
- **Frontend:** HTML5, Vanilla JavaScript, Vanilla CSS (Custom Design System)
- **Deployment:** Vercel (Serverless functions via WSGI)

---

## 💻 Local Setup & Development

To run the calculator on your local machine:

1. **Clone the repository** (or download the files).
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Flask server:**
   ```bash
   python app.py
   ```
4. **Open in Browser:** Navigate to `http://127.0.0.1:5000`

---

## 🛡️ Security Measures

Because this calculator exposes an API endpoint (`/api/calculate`), the following serverless protections are in place:
1. **Loop Exhaustion Protection:** Duration is capped at 100 years.
2. **Overflow Protection:** Investment amounts are capped at 100 Billion Rs and percentage rates at 5000% to prevent Python `OverflowError` thread crashes.
3. **Rate Limiting:** The API is strictly limited to 30 requests per minute per IP to deter bot spam.

---

## 📝 Example Working (Step-by-Step Scenario)

Let's assume a simple scenario to see how the math works in action.
- **Monthly Investment:** Rs. 10,000
- **Annual Return:** 14% *(which means ~1.16% per month)*
- **Duration:** 10 Years *(120 months)*

**Step 1: Month 1 Purchase Fees**
When you deposit Rs. 10,000, the broker buys shares. The system deducts the transaction fees:
- *Brokerage (0.15%):* Rs. 15.00
- *SST on Brokerage (13%):* Rs. 1.95
- *CDC Fee (0.02%):* Rs. 2.00
- **Total Fees Deducted:** Rs. 18.95
- **Actual Invested Capital:** Rs. 9,981.05

**Step 2: Month 1 Growth**
Your actual capital now grows by the monthly return rate (~1.16%).
- `Rs. 9,981.05 × 1.0116 = Rs. 10,096.83`
At the end of Month 1, your portfolio balance is **Rs. 10,096.83**. 

*(This cycle repeats for all 120 months, adding a new Rs. 10,000 deposit and compounding the total balance every time).*

**Step 3: Annual Flat Fee**
At the end of every 12th month (Month 12, 24, 36...), the system automatically deducts the NCCPL/CDC account maintenance fee (e.g., **Rs. 700**) from your balance.

**Step 4: Capital Gains Tax (CGT)**
Assume after 10 years, your total portfolio has grown to **Rs. 2,500,000** (gross value).
Since you deposited Rs. 10,000 every month for 120 months, your total contribution is **Rs. 1,200,000**.
- **Net Profit:** `2,500,000 - 1,200,000 = Rs. 1,300,000` *(simplified by ignoring minor deducted fees for clarity)*
- **Filer CGT (15%):** `1,300,000 × 0.15 = Rs. 195,000`
- **Final Take-Home Amount:** `2,500,000 - 195,000 = Rs. 2,305,000`
