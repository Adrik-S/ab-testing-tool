content = """from fastapi import FastAPI
from pydantic import BaseModel
from statsmodels.stats.proportion import proportions_ztest
import math

app = FastAPI()

class ABTestInput(BaseModel):
    control_visitors: int
    control_conversions: int
    variant_visitors: int
    variant_conversions: int

@app.post("/analyze")
def analyze_ab_test(data: ABTestInput):
    control_rate = data.control_conversions / data.control_visitors
    variant_rate = data.variant_conversions / data.variant_visitors
    uplift = (variant_rate - control_rate) / control_rate * 100
    count = [data.variant_conversions, data.control_conversions]
    nobs = [data.variant_visitors, data.control_visitors]
    z_stat, p_value = proportions_ztest(count, nobs)
    significant = p_value < 0.05
    margin_of_error = 1.96 * math.sqrt((variant_rate * (1 - variant_rate)) / data.variant_visitors)
    ci_lower = round((variant_rate - margin_of_error) * 100, 2)
    ci_upper = round((variant_rate + margin_of_error) * 100, 2)
    return {
        "control_rate": round(control_rate * 100, 2),
        "variant_rate": round(variant_rate * 100, 2),
        "uplift_percent": round(uplift, 2),
        "p_value": round(p_value, 4),
        "significant": significant,
        "confidence_interval": {"lower": ci_lower, "upper": ci_upper},
        "verdict": "Variant wins" if significant and uplift > 0 else "Control wins" if significant and uplift < 0 else "No significant difference yet"
    }

@app.get("/")
def root():
    return {"status": "AB Testing Tool is live"}
"""

with open("main.py", "w") as f:
    f.write(content)

print("main.py written successfully!")
