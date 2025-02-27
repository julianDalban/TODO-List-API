from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    PROJECT_NAME: str = 'Todo List API'
    
    DATABASE_URL: str = 'sql:///./app.db'
    
    class Config:
        env_file = '.env'

settings = Settings()