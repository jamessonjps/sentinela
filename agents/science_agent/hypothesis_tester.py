import pandas as pd
from scipy import stats
from typing import Dict, Any

class HypothesisTester:
    """
    Tests statistical hypotheses related to the SENTINELA project data.
    """
    
    def compare_response_times(self, df: pd.DataFrame, category_col: str, time_col: str) -> Dict[str, Any]:
        """
        Performs an ANOVA or T-test to compare response times across different categories.
        """
        df = df.dropna(subset=[category_col, time_col])
        categories = df[category_col].unique()
        
        if len(categories) < 2:
            return {"error": "Not enough categories to compare."}
            
        groups = [df[df[category_col] == cat][time_col] for cat in categories]
        
        if len(categories) == 2:
            stat, p_value = stats.ttest_ind(groups[0], groups[1])
            test_name = "Independent T-test"
        else:
            stat, p_value = stats.f_oneway(*groups)
            test_name = "One-way ANOVA"
            
        return {
            "test_name": test_name,
            "statistic": float(stat),
            "p_value": float(p_value),
            "significant_difference": p_value < 0.05
        }
