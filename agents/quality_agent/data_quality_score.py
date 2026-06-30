import pandas as pd
from typing import Dict, List

class DataQualityScore:
    """
    Evaluates the completeness and quality of critical keys (NIC, BO_PC, CAD)
    in the SENTINELA dataset.
    """
    
    def __init__(self, critical_keys: List[str] = None):
        if critical_keys is None:
            self.critical_keys = ['NIC', 'BO_PC', 'CAD']
        else:
            self.critical_keys = critical_keys

    def calculate_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculates the percentage of non-null values for each critical key.
        """
        completeness_scores = {}
        total_rows = len(df)
        
        if total_rows == 0:
            return {key: 0.0 for key in self.critical_keys}
            
        for key in self.critical_keys:
            if key in df.columns:
                valid_count = df[key].notna().sum()
                completeness_scores[key] = float((valid_count / total_rows) * 100)
            else:
                completeness_scores[key] = 0.0
                
        return completeness_scores
        
    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Generates a comprehensive data quality report based on key completeness.
        """
        completeness = self.calculate_completeness(df)
        
        overall_score = float(sum(completeness.values()) / len(self.critical_keys)) if self.critical_keys else 100.0
        
        return {
            "overall_quality_score": overall_score,
            "key_completeness_percentages": completeness,
            "records_analyzed": int(len(df))
        }
