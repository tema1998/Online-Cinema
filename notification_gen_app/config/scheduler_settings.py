from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from notification_gen_app.config.settings import settings

jobstores = {
    'default': RedisJobStore(db=1, jobs_key='dispatched_trips_jobs', run_times_key='dispatched_trips_running',
                             host=settings.redis_host, port=settings.redis_port)
}

scheduler = AsyncIOScheduler(timezone='Europe/Moscow', jobstores=jobstores)

