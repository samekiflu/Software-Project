from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Optional, Any
import time
import logging
from url_classifier import URLType


class BaseMetric(ABC):
    """Base class for all metrics"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def required_url_types(self) -> List[URLType]:
        """Returns list of URL types required to calculate this metric"""
        pass

    @abstractmethod
    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        """
        Calculate the metric score

        Args:
            resources: Dictionary mapping URLType to list of resource handlers

        Returns:
            Tuple of (score, latency_ms)
        """
        pass


class LicenseMetric(BaseMetric):
    """Metric for license compatibility with LGPLv2.1"""

    def required_url_types(self) -> List[URLType]:
        # License needs to be checked across all resources
        return [URLType.MODEL, URLType.DATASET, URLType.CODE]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        # Check license compatibility across all available resources
        scores = []

        for url_type in self.required_url_types():
            if url_type in resources and resources[url_type]:
                for resource in resources[url_type]:
                    license_score = self._evaluate_resource_license(resource)
                    scores.append(license_score)

        # Take the minimum score (most restrictive license)
        final_score = min(scores) if scores else 0.5

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return final_score, latency_ms

    def _evaluate_resource_license(self, resource: Any) -> float:
        # This would call the resource's license evaluation method
        try:
            return resource.get_license_score()
        except Exception as e:
            self.logger.error(f"Error evaluating license: {e}")
            return 0.5


class SizeScoreMetric(BaseMetric):
    """Metric for model size compatibility with different hardware"""

    def required_url_types(self) -> List[URLType]:
        # Size is primarily a model concern
        return [URLType.MODEL]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        if not resources.get(URLType.MODEL):
            return 0.0, int((time.time() - start_time) * 1000)

        model = resources[URLType.MODEL][0]  # Assume one model
        size_dict = self._calculate_hardware_compatibility(model)

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return size_dict, latency_ms

    def _calculate_hardware_compatibility(self, model: Any) -> Dict[str, float]:
        try:
            model_size_mb = model.get_size_mb()

            # Hardware compatibility thresholds (example)
            return {
                "raspberry_pi": 1.0 if model_size_mb < 100 else 0.5 if model_size_mb < 500 else 0.0,
                "jetson_nano": 1.0 if model_size_mb < 1000 else 0.7 if model_size_mb < 2000 else 0.3,
                "desktop_pc": 1.0 if model_size_mb < 5000 else 0.8 if model_size_mb < 10000 else 0.5,
                "aws_server": 1.0 if model_size_mb < 20000 else 0.9
            }
        except Exception as e:
            self.logger.error(f"Error calculating size compatibility: {e}")
            return {"raspberry_pi": 0.0, "jetson_nano": 0.0, "desktop_pc": 0.5, "aws_server": 0.5}


class RampUpTimeMetric(BaseMetric):
    """Metric for ease of getting started with the model"""

    def required_url_types(self) -> List[URLType]:
        # Ramp-up depends on documentation quality across all resources
        return [URLType.MODEL, URLType.DATASET, URLType.CODE]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        documentation_scores = []

        for url_type in self.required_url_types():
            if url_type in resources and resources[url_type]:
                for resource in resources[url_type]:
                    doc_score = self._evaluate_documentation_quality(resource)
                    documentation_scores.append(doc_score)

        # Average documentation quality across all resources
        final_score = sum(documentation_scores) / len(documentation_scores) if documentation_scores else 0.0

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return final_score, latency_ms

    def _evaluate_documentation_quality(self, resource: Any) -> float:
        try:
            return resource.get_documentation_score()
        except Exception as e:
            self.logger.error(f"Error evaluating documentation: {e}")
            return 0.0


class BusFactorMetric(BaseMetric):
    """Metric for knowledge concentration risk"""

    def required_url_types(self) -> List[URLType]:
        # Bus factor should consider all related resources
        return [URLType.MODEL, URLType.DATASET, URLType.CODE]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        contributor_counts = []

        for url_type in self.required_url_types():
            if url_type in resources and resources[url_type]:
                for resource in resources[url_type]:
                    contributor_count = self._get_contributor_count(resource)
                    contributor_counts.append(contributor_count)

        # Calculate bus factor based on contributor diversity
        avg_contributors = sum(contributor_counts) / len(contributor_counts) if contributor_counts else 0

        # Convert to 0-1 score (more contributors = higher score)
        if avg_contributors >= 10:
            final_score = 1.0
        elif avg_contributors >= 5:
            final_score = 0.8
        elif avg_contributors >= 2:
            final_score = 0.5
        else:
            final_score = 0.2

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return final_score, latency_ms

    def _get_contributor_count(self, resource: Any) -> int:
        try:
            return resource.get_contributor_count()
        except Exception as e:
            self.logger.error(f"Error getting contributor count: {e}")
            return 1


class PerformanceClaimsMetric(BaseMetric):
    """Metric for evidence of performance claims"""

    def required_url_types(self) -> List[URLType]:
        # Performance claims need model + dataset + evaluation code
        return [URLType.MODEL, URLType.DATASET, URLType.CODE]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        has_benchmarks = False
        has_evaluation_code = False
        has_dataset_info = False

        # Check for benchmarks in model
        if URLType.MODEL in resources and resources[URLType.MODEL]:
            has_benchmarks = resources[URLType.MODEL][0].has_performance_benchmarks()

        # Check for evaluation code
        if URLType.CODE in resources and resources[URLType.CODE]:
            has_evaluation_code = resources[URLType.CODE][0].has_evaluation_code()

        # Check for dataset information
        if URLType.DATASET in resources and resources[URLType.DATASET]:
            has_dataset_info = resources[URLType.DATASET][0].has_evaluation_dataset()

        # Score based on available evidence
        score = 0.0
        if has_benchmarks:
            score += 0.5
        if has_evaluation_code:
            score += 0.3
        if has_dataset_info:
            score += 0.2

        final_score = min(score, 1.0)

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return final_score, latency_ms


class DatasetAndCodeScoreMetric(BaseMetric):
    """Metric for availability of training dataset and code"""

    def required_url_types(self) -> List[URLType]:
        return [URLType.DATASET, URLType.CODE]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        dataset_available = URLType.DATASET in resources and resources[URLType.DATASET]
        code_available = URLType.CODE in resources and resources[URLType.CODE]

        score = 0.0
        if dataset_available:
            score += 0.6
        if code_available:
            score += 0.4

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return score, latency_ms


class DatasetQualityMetric(BaseMetric):
    """Metric for dataset quality assessment"""

    def required_url_types(self) -> List[URLType]:
        return [URLType.DATASET]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        if not resources.get(URLType.DATASET):
            return 0.0, int((time.time() - start_time) * 1000)

        dataset = resources[URLType.DATASET][0]
        quality_score = self._evaluate_dataset_quality(dataset)

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return quality_score, latency_ms

    def _evaluate_dataset_quality(self, dataset: Any) -> float:
        try:
            return dataset.get_quality_score()
        except Exception as e:
            self.logger.error(f"Error evaluating dataset quality: {e}")
            return 0.0


class CodeQualityMetric(BaseMetric):
    """Metric for code quality assessment"""

    def required_url_types(self) -> List[URLType]:
        return [URLType.CODE]

    def calculate(self, resources: Dict[URLType, List[Any]]) -> Tuple[float, int]:
        start_time = time.time()

        if not resources.get(URLType.CODE):
            return 0.0, int((time.time() - start_time) * 1000)

        code_repo = resources[URLType.CODE][0]
        quality_score = self._evaluate_code_quality(code_repo)

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        return quality_score, latency_ms

    def _evaluate_code_quality(self, code_repo: Any) -> float:
        try:
            return code_repo.get_code_quality_score()
        except Exception as e:
            self.logger.error(f"Error evaluating code quality: {e}")
            return 0.0


# Metric registry for easy access
METRIC_CLASSES = {
    'license': LicenseMetric,
    'size_score': SizeScoreMetric,
    'ramp_up_time': RampUpTimeMetric,
    'bus_factor': BusFactorMetric,
    'performance_claims': PerformanceClaimsMetric,
    'dataset_and_code_score': DatasetAndCodeScoreMetric,
    'dataset_quality': DatasetQualityMetric,
    'code_quality': CodeQualityMetric
}
