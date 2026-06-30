import pandas as pd
from typing import Dict, Any

class SLACalculator:
    """
    Calculates SLA (Service Level Agreement) metrics, specifically response times
    for procedures in the SENTINELA project.
    """
    
    def __init__(self, target_response_time_hours: float = 24.0):
        self.target_response_time_hours = target_response_time_hours

    def calculate_response_times(self, df: pd.DataFrame, start_time_col: str, end_time_col: str) -> pd.DataFrame:
        """
        Calculates the response time between start and end timestamps.
        """
        df = df.copy()
        df[start_time_col] = pd.to_datetime(df[start_time_col])
        df[end_time_col] = pd.to_datetime(df[end_time_col])
        
        df['response_time_hours'] = (df[end_time_col] - df[start_time_col]).dt.total_seconds() / 3600
        df['sla_met'] = df['response_time_hours'] <= self.target_response_time_hours
        
        return df
        
    def generate_sla_report(self, df: pd.DataFrame, group_by_col: str = None) -> Dict[str, Any]:
        """
        Generates an SLA compliance report.
        """
        if 'sla_met' not in df.columns:
            raise ValueError("Dataframe must contain 'sla_met' column. Run calculate_response_times first.")
            
        report = {
            "overall_compliance_rate": float(df['sla_met'].mean()),
            "average_response_time_hours": float(df['response_time_hours'].mean()),
            "total_records": int(len(df))
        }
        
        if group_by_col and group_by_col in df.columns:
            grouped = df.groupby(group_by_col).agg(
                compliance_rate=('sla_met', 'mean'),
                avg_response_time=('response_time_hours', 'mean'),
                count=('sla_met', 'count')
            ).to_dict('index')
            report['grouped_metrics'] = grouped
            
        return report
