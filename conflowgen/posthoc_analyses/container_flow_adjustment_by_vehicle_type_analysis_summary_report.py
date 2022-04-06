from __future__ import annotations

import pandas as pd

from conflowgen.posthoc_analyses.container_flow_adjustment_by_vehicle_type_analysis_summary import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummary
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by
    :class:`.ContainerFlowAdjustmentByVehicleTypeAnalysisSummary` and creates a comprehensible representation for the
    user, either as text or as a graph.
    """

    report_description = """
    Analyse whether a container needed to change its vehicle type for the outbound journey and if that was the case,
    how many times which vehicle type was chosen in order to not exceed the maximum dwell time.
    """

    def __init__(self):
        super().__init__()
        self.analysis_summary = ContainerFlowAdjustmentByVehicleTypeAnalysisSummary()

    def get_report_as_text(
            self
    ) -> str:
        adjusted_to = self.analysis_summary.get_summary()
        total_capacity = sum(adjusted_to)

        if total_capacity > 0:
            report = "\n"
            report += "                             Capacity in TEU\n"
            report += f"vehicle type unchanged:      {adjusted_to.unchanged:<10.1f} " \
                      f"({adjusted_to.unchanged * 100 / total_capacity:.2f}%)\n"
            report += f"changed to deep sea vessel:  {adjusted_to.deep_sea_vessel:<10.1f} " \
                      f"({adjusted_to.deep_sea_vessel * 100 / total_capacity:.2f}%)\n"
            report += f"changed to feeder:           {adjusted_to.feeder:<10.1f} " \
                      f"({adjusted_to.feeder * 100 / total_capacity:.2f}%)\n"
            report += f"changed to barge:            {adjusted_to.barge:<10.1f} " \
                      f"({adjusted_to.barge * 100 / total_capacity:.2f}%)\n"
            report += f"changed to train:            {adjusted_to.train:<10.1f} " \
                      f"({adjusted_to.train * 100 / total_capacity:.2f}%)\n"
            report += f"changed to truck:            {adjusted_to.truck:<10.1f} " \
                      f"({adjusted_to.truck * 100 / total_capacity:.2f}%)\n"
            report += "(rounding errors might exist)\n"
        else:
            report = """
                             Capacity in TEU
vehicle type unchanged:      0.0        (-%)
changed to deep sea vessel:  0.0        (-%)
changed to feeder:           0.0        (-%)
changed to barge:            0.0        (-%)
changed to train:            0.0        (-%)
changed to truck:            0.0        (-%)
(rounding errors might exist)
"""
        return report

    def get_report_as_graph(self) -> object:
        """
        The report as a graph is represented as a pie chart.

        Returns:
             The matplotlib axis of the pie chart.
        """

        adjusted_to = self.analysis_summary.get_summary()
        if sum(adjusted_to) == 0:
            return no_data_graph()

        data_series = pd.Series({
            "unchanged": adjusted_to.unchanged,
            "deep sea vessel": adjusted_to.deep_sea_vessel,
            "feeder": adjusted_to.feeder,
            "barge": adjusted_to.barge,
            "train": adjusted_to.train,
            "truck": adjusted_to.truck
        }, name="Transshipment share")
        ax = data_series.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title="Adjusted vehicle type"
        )
        return ax
