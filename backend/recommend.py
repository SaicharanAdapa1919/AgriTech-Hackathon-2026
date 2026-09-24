import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def recommend_schemes(state: str, crop: str, land: float, category: str):
    """
    AI-style weighted recommendation engine
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schemes_path = os.path.join(base_dir, "schemes.csv")
        
        # Check if file exists
        if not os.path.exists(schemes_path):
            logger.error(f"Schemes file not found: {schemes_path}")
            raise FileNotFoundError(f"Schemes data file not found at {schemes_path}")
        
        data = pd.read_csv(schemes_path)
        
        # Validate required columns
        required_columns = ["scheme_name", "state", "crop_type", "min_land", "max_land", "farmer_category", "benefit_type", "benefit_amount", "focus_area", "description", "eligibility", "application_mode", "official_url"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            logger.error(f"Missing columns in schemes.csv: {missing_columns}")
            raise ValueError(f"Missing required columns: {missing_columns}")


        data["min_land"] = data["min_land"].astype(float)
        data["max_land"] = data["max_land"].astype(float)
        
        # Fill NaN values to prevent JSON serialization errors
        data = data.fillna("NA")

        recommendations = []

        logger.info(f"Processing recommendation for: state={state}, crop={crop}, land={land}, category={category}")

        for _, row in data.iterrows():
            # Only include schemes that match the selected state (or "All" states)
            if row["state"] not in [state, "All"]:
                continue
            
            score = 0

            # Weighted intelligence - only for matching state
            score += 3  # State match (already confirmed above)
            if row["crop_type"] in [crop, "All"]:
                score += 3
            if row["min_land"] <= land <= row["max_land"]:
                score += 2
            if row["farmer_category"] in [category, "All"]:
                score += 2

            if score >= 6:  # Eligibility threshold

                recommendations.append({
                    "scheme_name": row["scheme_name"],
                    "focus_area": row["focus_area"],
                    "benefit_type": row["benefit_type"],
                    "benefit_amount": row["benefit_amount"],
                    "description": row["description"],
                    "eligibility": row["eligibility"],
                    "application_mode": row["application_mode"],
                    "official_url": row["official_url"],
                    "score": score
                })


        # Rank schemes by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Found {len(recommendations)} recommendations")
        return recommendations
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error in recommend_schemes: {e}")
        raise RuntimeError(f"Failed to generate recommendations: {str(e)}")
