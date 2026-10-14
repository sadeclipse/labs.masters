from fastapi import APIRouter, HTTPException
from typing import List
from schemas.aviaModel import AviaMetricsCreate, AviaMetrics
from service.avia_service import avia_service

router = APIRouter(tags=["Avia Metrics"])

@router.get("/metrics", response_model=List[AviaMetrics], summary="Получить все метрики")
def get_all_metrics():
    return avia_service.get_all()


@router.get("/metrics/{record_id}", response_model=AviaMetrics, summary="Получить метрику по ID")
def get_metric(record_id: int):
    result = avia_service.get_by_id(record_id)
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result


@router.post("create_metric", response_model=AviaMetrics, status_code=201)
def create_metric(metric: AviaMetricsCreate): 
    return avia_service.create(metric)


@router.put("/metrics/{record_id}", response_model=AviaMetrics, summary="Обновить запись по ID")
def update_metric(record_id: int, updated_metric: AviaMetrics):
    if record_id != updated_metric.id:
        raise HTTPException(status_code=400, detail="ID в URL и в теле запроса не совпадают")
        
    result = avia_service.update(record_id, updated_metric)
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return result


@router.delete("/metrics/{record_id}", summary="Удалить запись по ID")
def delete_metric(record_id: int):
    success = avia_service.delete(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"message": f"Запись с ID {record_id} успешно удалена"}