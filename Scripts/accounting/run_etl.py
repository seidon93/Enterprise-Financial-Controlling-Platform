"""
Enterprise ETL Runner
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from accounting.scenario_config import ScenarioConfig
from accounting.scenario_engine import ScenarioEngine


def main() -> None:

    config = ScenarioConfig()

    engine = ScenarioEngine(config)

    engine.run()


if __name__ == "__main__":
    main()