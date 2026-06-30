import pandas as pd
from typing import Dict, Any

class KPIGenerator:
    """
    Generates Key Performance Indicators from VW_PROCEDIMENTOS_DAAS.
    Focuses on process response times and throughput.
    """
    
    def generate_process_kpis(self, df: pd.DataFrame, start_col: str = 'DATA_INICIO', end_col: str = 'DATA_FIM') -> Dict[str, Any]:
        """
        Generates KPIs for process response times.
        """
        df = df.copy()
        
        if start_col in df.columns and end_col in df.columns:
            df[start_col] = pd.to_datetime(df[start_col])
            df[end_col] = pd.to_datetime(df[end_col])
            
            df['duration_hours'] = (df[end_col] - df[start_col]).dt.total_seconds() / 3600
            
            kpis = {
                "average_process_time_hours": float(df['duration_hours'].mean()),
                "median_process_time_hours": float(df['duration_hours'].median()),
                "max_process_time_hours": float(df['duration_hours'].max()),
                "min_process_time_hours": float(df['duration_hours'].min()),
                "total_completed_processes": int(df[end_col].notna().sum())
            }
            return kpis
        else:
            return {"error": "Required datetime columns not found for KPI generation."}
            
    def generate_volume_kpis(self, df: pd.DataFrame, date_col: str = 'DATA_REGISTRO') -> Dict[str, Any]:
        """
        Generates KPIs related to the volume of procedures over time.
        """
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
            monthly_volume = df.groupby(df[date_col].dt.to_period('M')).size()
            
            return {
                "total_procedures": len(df),
                "monthly_volume_trend": {str(k): int(v) for k, v in monthly_volume.items()}
            }
        else:
            return {"error": "Date column not found for volume KPIs."}
