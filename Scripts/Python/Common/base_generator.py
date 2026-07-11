"""
===============================================================================
Enterprise Financial Analytics Platform (EFAP)
-------------------------------------------------------------------------------
Object          : base_generator.py
Object Type     : Base ETL Generator
Layer           : Common
Version         : 1.0.0
Status          : Development

Description:
Abstract base class for all EFAP ETL generators.
===============================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from common.db_loader import replace_table


class BaseGenerator(ABC):
    """
    Base class for all ETL generators.
    """

    table_name: str = ""

    def __init__(self) -> None:
        self.df = pd.DataFrame()

    @abstractmethod
    def generate(self) -> pd.DataFrame:
        """
        Generate the DataFrame.
        """
        ...

    @abstractmethod
    def validate(self) -> None:
        """
        Validate the generated DataFrame.
        """
        ...

    def load(self) -> None:
        """
        Load the DataFrame into PostgreSQL.
        """

        replace_table(
            df=self.df,
            table_name=self.table_name,
        )

    def run(self) -> None:
        """
        Execute the ETL pipeline.
        """

        self.generate()

        self.validate()

        self.load()