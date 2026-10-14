from typing import List, Optional
from typing import List, Optional
from schemas.aviaModel import AviaMetrics, AviaMetricsCreate

class AviaMetricsService:
    def __init__(self):
        self._db: dict[int, dict] = {
            1: {"id": 1, "model": "Airbus A320", "airline": "Aeroflot", "altitude": 10500.0, "speed": 840.5, "latitude": 55.7558, "longitude": 37.6173, "lainerStatus": "In the flight"}
        }
        self._current_id = 1 
    
    def get_all(self) -> List[dict]:
        return list(self._db.values())

    def get_by_id(self, record_id: int) -> Optional[dict]:
        return self._db.get(record_id)

    def create(self, metric_data: AviaMetricsCreate) -> dict:
        self._current_id += 1 
        new_id = self._current_id
        
        new_record = metric_data.model_dump()
        new_record["id"] = new_id
        
        self._db[new_id] = new_record
        return new_record

    def update(self, record_id: int, metric: AviaMetrics) -> Optional[dict]:
        if record_id not in self._db:
            return None
        self._db[record_id] = metric.model_dump()
        return self._db[record_id]

    def delete(self, record_id: int) -> bool:
        if record_id not in self._db:
            return False
        del self._db[record_id]
        return True

avia_service = AviaMetricsService()
