from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from notification_gen_app.api.v1.dependencies import get_periodic_task_service
from notification_gen_app.config.settings import settings
from notification_gen_app.config.scheduler_settings import scheduler
from notification_gen_app.schemas.messages import InstantMessageRequest, PeriodicTaskIdRequest, \
    PeriodicTaskParamsRequest
from notification_gen_app.services.periodic_messages import PeriodicMessageService, PeriodicTaskService
from uuid import UUID

router = APIRouter()

@router.post("/periodic_messages/pause_task/", status_code=status.HTTP_201_CREATED)
async def pause_periodic_task(
        periodic_task_params: PeriodicTaskIdRequest,
        periodic_message_service: PeriodicTaskService = Depends(get_periodic_task_service)
):
    try:
        result = await periodic_message_service.pause_task(task_id=periodic_task_params.task_id)
        return JSONResponse({'result': result})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/periodic_messages/resume_task/", status_code=status.HTTP_201_CREATED)
async def resume_periodic_task(
        periodic_task_params: PeriodicTaskIdRequest,
        periodic_message_service: PeriodicTaskService = Depends(get_periodic_task_service)
):
    try:
        result = await periodic_message_service.resume_task(task_id=periodic_task_params.task_id)
        return JSONResponse({'result': result})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/periodic_messages/delete_task/", status_code=status.HTTP_202_ACCEPTED)
async def delete_periodic_task(
        periodic_task_params: PeriodicTaskIdRequest,
        periodic_message_service: PeriodicTaskService = Depends(get_periodic_task_service)
):
    try:
        result = await periodic_message_service.delete_task(task_id=periodic_task_params.task_id)
        return JSONResponse({'result': result})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/periodic_messages/tasks/", status_code=status.HTTP_200_OK)
async def get_tasks(
        periodic_message_service: PeriodicTaskService = Depends(get_periodic_task_service)
):
    try:
        result = await periodic_message_service.get_tasks()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/periodic_messages/{content_id}/", status_code=status.HTTP_201_CREATED)
async def create_periodic_message(
        content_id: UUID,
        message: InstantMessageRequest,
        periodic_task_params: PeriodicTaskParamsRequest,
        ):

    try:
        # Get periodic_message_service, because scheduler doesn't supply dependencies
        periodic_message_service = PeriodicMessageService(broker_url=settings.rabbitmq_connection_url)

        # Add task to scheduler
        result = scheduler.add_job(
            periodic_message_service.send_single_message,
            kwargs={"content_id": content_id, "message": message, "message_transfer": 'email',
                    "queue_name": settings.scheduled_message_queue}, trigger='interval',
            seconds=periodic_task_params.interval_in_seconds, name=periodic_task_params.name)
        return JSONResponse({'result': str(result)})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
