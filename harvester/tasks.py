import logging

from celery import shared_task

from .services import CrawlerService, ProcessingService

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def collect_wikicfp_task(self, pages: int = 3, per_page: int = 40) -> dict[str, int]:
    service = CrawlerService()
    result = service.collect(pages=pages, per_page=per_page)
    logger.info("WikiCFP collect task finished: %s", result)
    return result


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def process_conferences_task(self, limit: int = 300) -> dict[str, int]:
    service = ProcessingService()
    processed = service.process_pending(limit=limit)
    result = {"processed": processed}
    logger.info("Conference processing task finished: %s", result)
    return result


@shared_task(bind=True)
def collect_and_process_task(self, pages: int = 3, per_page: int = 40, process_limit: int = 300) -> dict[str, int]:
    collect_result = collect_wikicfp_task(pages=pages, per_page=per_page)
    process_result = process_conferences_task(limit=process_limit)
    return {
        **collect_result,
        **process_result,
    }
