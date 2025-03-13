from api_collector import CarbonDataCollector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    collector = CarbonDataCollector()
    
    # Collect cloud provider data
    logger.info("Collecting cloud provider data...")
    cloud_data = collector.collect_cloud_data()
    logger.info(f"Collected {len(cloud_data)} records from cloud providers")
    
    # Collect training benchmarks
    logger.info("Collecting training benchmark data...")
    benchmark_data = collector.collect_training_benchmarks()
    logger.info(f"Collected {len(benchmark_data)} benchmark records")
    
    return cloud_data, benchmark_data

if __name__ == "__main__":
    main() 