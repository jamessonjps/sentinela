import pandas as pd
from typing import Dict, Any

class ProfileAnalyzer:
    """
    Analyzes DADOS_AUTOR data to create perpetrator profiles.
    """
    
    def analyze_demographics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates a profile based on demographics in DADOS_AUTOR.
        Expected columns might include age, gender, previous_records, etc.
        """
        profile = {}
        
        if 'AGE' in df.columns:
            profile['age_stats'] = {
                'mean': float(df['AGE'].mean()),
                'median': float(df['AGE'].median()),
                'mode': float(df['AGE'].mode()[0]) if not df['AGE'].mode().empty else None
            }
            
        if 'GENDER' in df.columns:
            profile['gender_distribution'] = df['GENDER'].value_counts(normalize=True).to_dict()
            
        if 'CRIME_TYPE' in df.columns:
            profile['common_crimes'] = df['CRIME_TYPE'].value_counts().head(5).to_dict()
            
        return profile
        
    def identify_repeat_offenders(self, df: pd.DataFrame, id_col: str = 'AUTHOR_ID') -> Dict[str, Any]:
        """
        Identifies repeat offenders based on ID frequency.
        """
        if id_col not in df.columns:
            return {"error": f"Column {id_col} not found in dataframe."}
            
        counts = df[id_col].value_counts()
        repeat_offenders = counts[counts > 1]
        
        return {
            "total_authors": int(df[id_col].nunique()),
            "repeat_offenders_count": int(len(repeat_offenders)),
            "percentage_repeat_offenders": float((len(repeat_offenders) / df[id_col].nunique()) * 100) if df[id_col].nunique() > 0 else 0.0
        }
