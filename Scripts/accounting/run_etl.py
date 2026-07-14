"""
Enterprise ETL Runner
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging

from accounting.scenario_config import ScenarioConfig
from accounting.scenario_engine import ScenarioEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)


def main() -> None:

    config = ScenarioConfig()

    engine = ScenarioEngine(config)

    engine.run_accounting()


if __name__ == "__main__":
    main()