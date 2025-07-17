from fastapi import FastAPI, Depends
from datetime import datetime
from typing import List, Generator
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os

# === Load environment variables ===
load_dotenv()


# === Settings ===
class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")

    class Config:
        env_file = ".env"


settings = Settings()

# === SQLAlchemy setup ===
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a SQLAlchemy session.
    Closes the session automatically after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Pydantic schemas ===
class Measure(BaseModel):
    node_id: int
    node_name: str
    region_name: str
    grid_name: str
    timestamp: datetime
    value: float
    collected_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# === FastAPI app ===
app = FastAPI()


@app.get("/api/latest_measures", response_model=List[Measure])
async def get_latest_measures(
    start: datetime, end: datetime, db: Session = Depends(get_db)
) -> List[Measure]:
    """
    Return latest collected measurements per node in a time range.
    """
    query = text(
        """
        WITH latest_measures AS (
            SELECT 
                m.grid_node_id,
                m.timestamp,
                MAX(m.collected_at) as latest_collected_at
            FROM measures m
            WHERE m.timestamp BETWEEN :start AND :end
            GROUP BY m.grid_node_id, m.timestamp
        )
        SELECT 
            n.id AS node_id,
            n.name AS node_name,
            r.name AS region_name,
            g.name AS grid_name,
            m.timestamp,
            m.value,
            m.collected_at
        FROM measures m
        JOIN latest_measures lm ON 
            m.grid_node_id = lm.grid_node_id AND 
            m.timestamp = lm.timestamp AND 
            m.collected_at = lm.latest_collected_at
        JOIN grid_nodes n ON m.grid_node_id = n.id
        JOIN grid_regions r ON n.region_id = r.id
        JOIN grids g ON r.grid_id = g.id
        ORDER BY n.id, m.timestamp
        """
    )

    result = db.execute(query, {"start": start, "end": end})
    return [
        Measure(
            node_id=row.node_id,
            node_name=row.node_name,
            region_name=row.region_name,
            grid_name=row.grid_name,
            timestamp=row.timestamp,
            value=row.value,
            collected_at=row.collected_at,
        )
        for row in result
    ]


@app.get("/api/measures_by_collection", response_model=List[Measure])
async def get_measures_by_collection(
    start: datetime,
    end: datetime,
    collected: datetime,
    db: Session = Depends(get_db),
) -> List[Measure]:
    """
    Return measurements available up to a certain collection time.
    Only latest per node-timestamp combination.
    """
    query = text(
        """
        SELECT 
            n.id AS node_id,
            n.name AS node_name,
            r.name AS region_name,
            g.name AS grid_name,
            m.timestamp,
            m.value,
            m.collected_at
        FROM measures m
        JOIN grid_nodes n ON m.grid_node_id = n.id
        JOIN grid_regions r ON n.region_id = r.id
        JOIN grids g ON r.grid_id = g.id
        WHERE m.timestamp BETWEEN :start AND :end
          AND m.collected_at <= :collected
          AND NOT EXISTS (
              SELECT 1 
              FROM measures m2 
              WHERE m2.grid_node_id = m.grid_node_id 
                AND m2.timestamp = m.timestamp 
                AND m2.collected_at <= :collected
                AND m2.collected_at > m.collected_at
          )
        ORDER BY n.id, m.timestamp
        """
    )

    result = db.execute(query, {"start": start, "end": end, "collected": collected})
    return [
        Measure(
            node_id=row.node_id,
            node_name=row.node_name,
            region_name=row.region_name,
            grid_name=row.grid_name,
            timestamp=row.timestamp,
            value=row.value,
            collected_at=row.collected_at,
        )
        for row in result
    ]
