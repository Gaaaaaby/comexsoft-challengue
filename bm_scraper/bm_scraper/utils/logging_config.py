import logging
import os


def setup_logging(log_level='INFO', log_file=None):
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    scraper_logger = logging.getLogger('bm_scraper')
    scraper_logger.setLevel(getattr(logging, log_level.upper()))
    
    return scraper_logger


def log_scraping_stats(logger, stats):
    logger.info("=== ESTADÍSTICAS DE SCRAPING ===")
    logger.info(f"Total de productos procesados: {stats.get('total_products', 0)}")
    logger.info(f"Páginas procesadas: {stats.get('pages_processed', 0)}")
    logger.info(f"Errores encontrados: {stats.get('errors', 0)}")
    logger.info(f"Tiempo total: {stats.get('total_time', 0):.2f} segundos")
    logger.info(f"Velocidad promedio: {stats.get('avg_speed', 0):.2f} productos/segundo")
    logger.info("================================")
