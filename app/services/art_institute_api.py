import httpx
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import settings


class CacheEntry:
    """Cache entry with value and expiration time"""
    def __init__(self, value: bool, ttl_seconds: int):
        self.value = value
        self.expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        return datetime.now() >= self.expires_at


_shared_cache: Dict[int, CacheEntry] = {}


class ArtInstituteAPIService:
    """Service for validating places in Art Institute of Chicago API with caching"""
    
    def __init__(self):
        self.base_url = settings.ART_INSTITUTE_API_BASE_URL
        self.timeout = 10.0
        self.cache_ttl = settings.API_CACHE_TTL_SECONDS
    
    @property
    def _cache(self) -> Dict[int, CacheEntry]:
        return _shared_cache
    
    def _get_from_cache(self, external_id: int) -> Optional[bool]:
        """
        Get value from cache if exists and not expired.
        Automatically cleans expired entries periodically.
        
        Args:
            external_id: ID of the artwork/place
            
        Returns:
            Cached value or None if not found/expired
        """
        if len(self._cache) > 1000 or len(self._cache) % 100 == 0:
            self.clear_expired_entries()
        
        if external_id not in self._cache:
            return None
        
        entry = self._cache[external_id]
        if entry.is_expired():
            del self._cache[external_id]
            return None
        
        return entry.value
    
    def _set_cache(self, external_id: int, value: bool):
        """
        Store value in cache with TTL.
        
        Args:
            external_id: ID of the artwork/place
            value: Value to cache
        """
        self._cache[external_id] = CacheEntry(value, self.cache_ttl)
    
    def clear_cache(self):
        self._cache.clear()
    
    def clear_expired_entries(self):
        expired_ids = [
            external_id for external_id, entry in self._cache.items()
            if entry.is_expired()
        ]
        for external_id in expired_ids:
            del self._cache[external_id]
    
    async def validate_place_exists(self, external_id: int) -> bool:
        """
        Validate that a place exists in the Art Institute API.
        Uses caching
        
        Args:
            external_id: ID of the artwork/place from the external API
            
        Returns:
            True if place exists, False otherwise
        """
        cached_value = self._get_from_cache(external_id)
        if cached_value is not None:
            return cached_value
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/artworks/{external_id}",
                    params={"fields": "id"}
                )
                exists = response.status_code == 200
                
                self._set_cache(external_id, exists)
                
                return exists
        except Exception:
            self._set_cache(external_id, False)
            return False
