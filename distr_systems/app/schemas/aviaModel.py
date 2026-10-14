from pydantic import BaseModel, Field
from typing import Literal

class AviaMetricsBase(BaseModel):
    model: Literal["Airbus A320", "Boeing 737", "other"] = Field(..., description="Модель авиалайнера")
    airline: str = Field(..., description="Авиакомпания")
    altitude: float = Field(..., description="Высота полета")
    speed: float = Field(..., description="Скорость полета")
    latitude: float = Field(..., description="Географическая широта")
    longitude: float = Field(..., description="Географическая долгота")
    lainerStatus: Literal["Awaiting", "In the flight", "Preparing"] = Field(..., description="Статус")

class AviaMetricsCreate(AviaMetricsBase):
    pass

class AviaMetrics(AviaMetricsBase):
    id: int = Field(..., description="Уникальный ID записи")
