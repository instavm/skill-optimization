# Well-written data processor
# This is a good example with minimal issues

from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DataRecord:
    """Represents a single data record."""
    id: str
    timestamp: datetime
    value: float
    metadata: Dict[str, str]


class DataProcessor:
    """
    Processes and validates data records.

    This class handles data validation, transformation, and aggregation
    with proper error handling and logging.
    """

    def __init__(self, max_batch_size: int = 1000):
        """
        Initialize the data processor.

        Args:
            max_batch_size: Maximum number of records to process in one batch
        """
        if max_batch_size <= 0:
            raise ValueError("max_batch_size must be positive")

        self.max_batch_size = max_batch_size
        self._records: List[DataRecord] = []

    def validate_record(self, record: DataRecord) -> bool:
        """
        Validate a single data record.

        Args:
            record: The record to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if not record.id:
                logger.warning("Record missing ID")
                return False

            if record.value < 0:
                logger.warning(f"Invalid value for record {record.id}: {record.value}")
                return False

            if record.timestamp > datetime.now():
                logger.warning(f"Future timestamp for record {record.id}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating record: {e}")
            return False

    def process_batch(self, records: List[DataRecord]) -> Dict[str, float]:
        """
        Process a batch of records and return aggregated statistics.

        Args:
            records: List of records to process

        Returns:
            Dictionary containing aggregated statistics

        Raises:
            ValueError: If batch size exceeds maximum
        """
        if len(records) > self.max_batch_size:
            raise ValueError(
                f"Batch size {len(records)} exceeds maximum {self.max_batch_size}"
            )

        valid_records = [r for r in records if self.validate_record(r)]

        if not valid_records:
            logger.info("No valid records in batch")
            return {"count": 0, "sum": 0.0, "average": 0.0}

        total = sum(r.value for r in valid_records)
        count = len(valid_records)

        return {
            "count": count,
            "sum": total,
            "average": total / count,
            "min": min(r.value for r in valid_records),
            "max": max(r.value for r in valid_records)
        }

    def add_record(self, record: DataRecord) -> None:
        """Add a record to the internal buffer."""
        if self.validate_record(record):
            self._records.append(record)
        else:
            logger.warning(f"Skipping invalid record: {record.id}")

    def get_records(self) -> List[DataRecord]:
        """Get all buffered records."""
        return self._records.copy()

    def clear(self) -> None:
        """Clear all buffered records."""
        self._records.clear()
