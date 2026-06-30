class GeoValidator:
    """
    Validates geographical coordinates and regions.
    """
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """
        Validates if latitude and longitude are within standard global bounds.
        """
        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return False
            
        if lat < -90 or lat > 90:
            return False
        if lon < -180 or lon > 180:
            return False
        return True
