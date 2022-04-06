from __future__ import annotations
import pandas as pd  # pylint: disable=import-outside-toplevel
import seaborn as sns  # pylint: disable=import-outside-toplevel

from conflowgen.posthoc_analyses.inbound_and_outbound_vehicle_capacity_analysis import \
    InboundAndOutboundVehicleCapacityAnalysis
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph

sns.set_palette(sns.color_palette())


class InboundAndOutboundVehicleCapacityAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.InboundAndOutboundVehicleCapacityAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    Analyze the vehicle capacity by vehicle type for the inbound and outbound journeys and check for the maximum
    capacity of each vehicle type.
    If e.g. for the vehicle type 'feeder' the maximum outbound capacity is used up, most likely there are more vehicles
    that deliver containers destined for feeder vessels than there are feeder vessels planned during the period of data
    generation (between `start_date` and `end_date`).
    """

    def __init__(self):
        super().__init__()
        self.analysis = InboundAndOutboundVehicleCapacityAnalysis(
            transportation_buffer=self.transportation_buffer
        )

    def get_report_as_text(self) -> str:
        inbound_capacities, outbound_actual_capacities, outbound_maximum_capacities = self._get_capacities()

        # create string representation
        report = "\n"
        report += "vehicle type    "
        report += "inbound capacity "
        report += "outbound actual capacity "
        report += "outbound max capacity"
        report += "\n"
        for vehicle_type in self.order_of_vehicle_types_in_report:
            vehicle_type_as_text = str(vehicle_type).replace("_", " ")
            report += f"{vehicle_type_as_text:<15} "
            report += f"{inbound_capacities[vehicle_type]:>16.1f} "
            report += f"{outbound_actual_capacities[vehicle_type]:>24.1f} "
            report += f"{outbound_maximum_capacities[vehicle_type]:>21.1f}"
            report += "\n"
        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self) -> object:
        """
        The report as a graph is represented as a bar chart using pandas.

        Returns:
             The matplotlib axis of the bar chart.
        """

        inbound_capacities, outbound_actual_capacities, outbound_maximum_capacities = self._get_capacities()
        if (len(inbound_capacities) + len(outbound_actual_capacities) + len(outbound_maximum_capacities)) == 0:
            return no_data_graph()
        else:
            df = pd.DataFrame({
                "inbound capacities": inbound_capacities,
                "outbound actual capacities": outbound_actual_capacities,
                "outbound maximum capacities": outbound_maximum_capacities
            })
            df.index = [str(i).replace("_", " ") for i in df.index]
            ax = df.plot.barh()
            ax.set_xlabel("Capacity (in TEU)")
            ax.set_title("Inbound and outbound vehicle capacity analysis")
            return ax

    def _get_capacities(self):
        assert self.transportation_buffer is not None
        self.analysis.update(
            transportation_buffer=self.transportation_buffer
        )
        # gather data
        inbound_capacities = self.analysis.get_inbound_capacity_of_vehicles()
        outbound_actual_capacities, outbound_maximum_capacities = self.analysis.get_outbound_capacity_of_vehicles()
        return inbound_capacities, outbound_actual_capacities, outbound_maximum_capacities
