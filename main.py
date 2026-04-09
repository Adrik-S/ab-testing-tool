from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from statsmodels.stats.proportion import proportions_ztest
from scipy import stats
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    z_stat = float(z_stat)
    p_value = float(p_value)
    significant = bool(p_value < 0.05)
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

class SampleSizeInput(BaseModel):
    baseline_rate: float
    minimum_detectable_effect: float
    confidence_level: float = 0.95
    power: float = 0.80

@app.post("/sample-size")
def calculate_sample_size(data: SampleSizeInput):
    alpha = 1 - data.confidence_level
    z_alpha = float(stats.norm.ppf(1 - alpha / 2))
    z_beta = float(stats.norm.ppf(data.power))
    p1 = data.baseline_rate
    p2 = p1 * (1 + data.minimum_detectable_effect)
    numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p2 - p1) ** 2
    sample_size = math.ceil(numerator / denominator)
    return {
        "baseline_rate": round(p1 * 100, 2),
        "target_rate": round(p2 * 100, 2),
        "sample_size_per_group": sample_size,
        "total_sample_size": sample_size * 2,
        "confidence_level": f"{int(data.confidence_level * 100)}%",
        "power": f"{int(data.power * 100)}%",
        "interpretation": f"You need {sample_size} visitors per group ({sample_size * 2} total) to detect a {round(data.minimum_detectable_effect * 100)}% relative improvement with {int(data.confidence_level * 100)}% confidence."
    }

class InterpretInput(BaseModel):
    experiment_name: str
    metric_name: str
    control_visitors: int
    control_conversions: int
    variant_visitors: int
    variant_conversions: int
    minimum_detectable_effect: float = 0.20

@app.post("/interpret")
def interpret_experiment(data: InterpretInput):
    control_rate = data.control_conversions / data.control_visitors
    variant_rate = data.variant_conversions / data.variant_visitors
    uplift = (variant_rate - control_rate) / control_rate * 100
    count = [data.variant_conversions, data.control_conversions]
    nobs = [data.variant_visitors, data.control_visitors]
    z_stat, p_value = proportions_ztest(count, nobs)
    p_value = float(p_value)
    significant = bool(p_value < 0.05)
    p1 = control_rate
    p2 = p1 * (1 + data.minimum_detectable_effect)
    z_alpha = float(stats.norm.ppf(0.975))
    z_beta = float(stats.norm.ppf(0.80))
    numerator = (z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
    denominator = (p2 - p1) ** 2
    required_sample = math.ceil(numerator / denominator)
    sample_sufficient = bool(data.control_visitors >= required_sample and data.variant_visitors >= required_sample)
    direction = "improved" if uplift > 0 else "decreased"
    if significant and uplift > 0 and sample_sufficient:
        recommendation = "Ship it"
        reasoning = f"The variant {direction} {data.metric_name} by {round(abs(uplift), 1)}% and the result is statistically significant with enough data to be confident. This is a clear win."
        risk = "Low - result is backed by sufficient data and strong significance."
    elif significant and uplift > 0 and not sample_sufficient:
        recommendation = "Proceed with caution"
        reasoning = f"The variant {direction} {data.metric_name} by {round(abs(uplift), 1)}% and reached significance, but you had fewer visitors than the recommended {required_sample} per group."
        risk = "Medium - significance reached early, which can be misleading."
    elif not significant and sample_sufficient:
        recommendation = "Kill it"
        reasoning = f"You had enough data ({data.control_visitors} visitors vs {required_sample} required) but the variant did not produce a significant improvement."
        risk = "Low - you gave the test a fair chance and it did not deliver."
    elif not significant and not sample_sufficient:
        recommendation = "Keep running"
        reasoning = f"The test has not reached the required {required_sample} visitors per group yet (currently at {data.control_visitors}). It is too early to make any decision."
        risk = "High - stopping early is the most common mistake in experimentation."
    else:
        recommendation = "Review manually"
        reasoning = f"The variant {direction} {data.metric_name} by {round(abs(uplift), 1)}%. The variant is hurting performance."
        risk = "High - do not ship. Investigate what caused the regression."
    return {
        "experiment_name": data.experiment_name,
        "metric_name": data.metric_name,
        "control_rate": round(control_rate * 100, 2),
        "variant_rate": round(variant_rate * 100, 2),
        "uplift_percent": round(uplift, 2),
        "p_value": round(p_value, 4),
        "significant": significant,
        "sample_sufficient": sample_sufficient,
        "required_sample_per_group": required_sample,
        "recommendation": recommendation,
        "reasoning": reasoning,
        "risk": risk
    }

@app.get("/")
def root():
    return {"status": "AB Testing Tool is live"}
