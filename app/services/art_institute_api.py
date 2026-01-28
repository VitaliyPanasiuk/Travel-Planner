import httpx
from app.config import settings


class ArtInstituteAPIService:
    """Service for validating places in Art Institute of Chicago API"""
    
    def __init__(self):
        self.base_url = settings.ART_INSTITUTE_API_BASE_URL
        self.timeout = 10.0
    
    async def validate_place_exists(self, external_id: str) -> bool:
        """
        Validate that a place exists in the Art Institute API.
        
        Args:
            external_id: ID of the artwork/place from the external API
            
        Returns:
            True if place exists, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/artworks/{external_id}",
                    params={"fields": "id"}
                )
                return response.status_code == 200
        except Exception:
            return False
