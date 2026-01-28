from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./travel_planner.db"
    
    ART_INSTITUTE_API_BASE_URL: str = "https://api.artic.edu/api/v1"
    
    MAX_PLACES_PER_PROJECT: int = 10
    MIN_PLACES_PER_PROJECT: int = 1
    
    API_CACHE_TTL_SECONDS: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()