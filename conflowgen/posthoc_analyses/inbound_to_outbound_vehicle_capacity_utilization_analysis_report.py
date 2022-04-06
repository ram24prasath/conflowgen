from __future__ import annotations

from typing import Tuple, Any, Dict, Iterable, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker
import pandas as pd

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.posthoc_analyses.inbound_to_outbound_vehicle_capacity_utilization_analysis import \
    InboundToOutboundVehicleCapacityUtilizationAnalysis, CompleteVehicleIdentifier
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class InboundToOutboundVehicleCapacityUtilizationAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.InboundToOutboundCapacityUtilizationAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    Analyze the used vehicle capacity for each vehicle for the inbound and outbound journeys.
    Generally, it expected to reach an equilibrium - each vehicle should approximately pick up as many containers
    at the container terminal as it has delivered.
    Great disparities between the transported capacities on the inbound and outbound journey are considered noteworthy
    but depending on the input data it might be acceptable.
    """

    maximum_length_for_readable_name = 50  # doc: Each vehicle has a name that might be a bit lengthy for text output

    plot_title = "Capacity utilization analysis"

    def __init__(self):
        super().__init__()
        self.analysis = InboundToOutboundVehicleCapacityUtilizationAnalysis(
            transportation_buffer=self.transportation_buffer
        )

    @classmethod
    def _create_readable_name(cls, vehicle_identifier: Tuple[Any]) -> str:
        name = "-".join(str(part) for part in vehicle_identifier)
        if len(name) > cls.maximum_length_for_readable_name:
            name = name[:46] + "..."

        return name

    def get_report_as_text(self, **kwargs) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Keyword Args:
            vehicle_type: Either ``"all"``, a single vehicle of type :class:`.ModeOfTransport` or a whole collection of
                vehicle types, e.g. passed as a :class:`list` or :class:`set`.
                For the exact interpretation of the parameter, check
                :class:`.InboundToOutboundVehicleCapacityUtilizationAnalysis`.

        Returns:
             The report in text format (possibly spanning over several lines).
        """
        vehicle_type, capacities = self._get_capacities_depending_on_vehicle_type(kwargs)
        report = "\n"
        report += "vehicle type = " + vehicle_type + "\n"
        report += "vehicle identifier                                 "
        report += "inbound capacity (in TEU) "
        report += "outbound capacity (in TEU)"
        report += "\n"
        for vehicle_identifier, (used_inbound_capacity, used_outbound_capacity) in capacities.items():
            vehicle_name = self._create_readable_name(vehicle_identifier)
            report += f"{vehicle_name:<50} "  # align this with cls.maximum_length_for_readable_name!
            report += f"{used_inbound_capacity:>25.1f} "
            report += f"{used_outbound_capacity:>26.1f}"
            report += "\n"
        if len(capacities) == 0:
            report += "--no vehicles exist--\n"
        else:
            report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self, **kwargs) -> object:
        """
        The report as a graph is represented as a scatter plot using pandas.

        Keyword Args:
            plot_type: Either "absolute", "relative", or "both". Defaults to "both".
            vehicle_type: Either ``"all"``, a single vehicle of type :class:`.ModeOfTransport` or a whole collection of
                vehicle types, e.g. passed as a :class:`list` or :class:`set`.
                For the exact interpretation of the parameter, check
                :class:`.InboundToOutboundVehicleCapacityUtilizationAnalysis`.

        Returns:
             The matplotlib figure
        """
        plot_type = kwargs.get("plot_type", "both")

        vehicle_type, capacities = self._get_capacities_depending_on_vehicle_type(kwargs)
        if len(capacities) == 0:
            return no_data_graph()

        df = self._convert_analysis_to_df(capacities)

        if plot_type == "absolute":
            fig, ax = plt.subplots(1, 1)
            self._plot_absolute_values(df, vehicle_type, ax=ax)
        elif plot_type == "relative":
            fig, ax = plt.subplots(1, 1)
            self._plot_relative_values(df, vehicle_type, ax=ax)
        elif plot_type == "both":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
            self._plot_absolute_values(df, vehicle_type, ax=ax1)
            self._plot_relative_values(df, vehicle_type, ax=ax2)
            plt.subplots_adjust(wspace=0.4)
        else:
            raise Exception(f"Plot type '{plot_type}' is not supported.")

        plt.legend(
            loc='lower left',
            bbox_to_anchor=(1, 0),
            fancybox=True,
        )
        return fig

    @staticmethod
    def _get_vehicle_type_representation(vehicle_type: Any) -> str:
        if vehicle_type is None:
            return "all"
        if isinstance(vehicle_type, ModeOfTransport):
            return str(vehicle_type)
        if isinstance(vehicle_type, Iterable):
            return " & ".join([str(element) for element in vehicle_type])
        return str(vehicle_type)

    def _plot_absolute_values(
            self, df: pd.DataFrame, vehicle_type: str, ax: Optional[matplotlib.pyplot.axis] = None
    ) -> matplotlib.pyplot.axis:
        ax = df.plot.scatter(x="inbound capacity (fixed)", y="used outbound capacity", ax=ax)
        slope = 1 + self.transportation_buffer
        ax.axline((0, 0), slope=slope, color='black', label='Maximum outbound capacity')
        ax.axline((0, 0), slope=1, color='gray', label='Equilibrium')
        ax.set_title(self.plot_title + " (absolute),\n vehicle type = " + vehicle_type)
        ax.set_aspect('equal', adjustable='box')
        ax.grid(color='lightgray', linestyle=':', linewidth=.5)
        maximum = df[["inbound capacity (fixed)", "used outbound capacity"]].max(axis=1).max(axis=0)
        axis_limitation = maximum * 1.1  # add some white space to the top and left
        ax.set_xlim([0, axis_limitation])
        ax.set_ylim([0, axis_limitation])
        return ax

    def _plot_relative_values(
            self, df: pd.DataFrame, vehicle_type: str, ax: Optional[matplotlib.pyplot.axis] = None
    ) -> matplotlib.pyplot.axis:
        ax = df.plot.scatter(x="inbound capacity (fixed)", y="ratio", ax=ax)
        ax.axline((0, (1 + self.transportation_buffer)), slope=0, color='black', label='Maximum outbound capacity')
        ax.axline((0, 1), slope=0, color='gray', label='Equilibrium')
        ax.set_title(self.plot_title + " (relative),\n vehicle type = " + vehicle_type)
        ax.grid(color='lightgray', linestyle=':', linewidth=.5)
        return ax

    def _convert_analysis_to_df(self, capacities: Dict[CompleteVehicleIdentifier, Tuple[float, float]]) -> pd.DataFrame:
        rows = []
        for vehicle_identifier, (inbound_capacity, used_outbound_capacity) in capacities.items():
            vehicle_name = self._create_readable_name(vehicle_identifier)
            rows.append({
                "vehicle name": vehicle_name,
                "inbound capacity (fixed)": inbound_capacity,
                "used outbound capacity": used_outbound_capacity
            })
        df = pd.DataFrame(rows)
        df["ratio"] = df["used outbound capacity"] / df["inbound capacity (fixed)"]
        return df

    def _get_capacities_depending_on_vehicle_type(
            self, kwargs
    ) -> Tuple[str, Dict[CompleteVehicleIdentifier, Tuple[float, float]]]:
        if "vehicle_type" in kwargs:
            vehicle_type = kwargs["vehicle_type"]
            capacities = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle(
                vehicle_type=vehicle_type
            )
        else:
            vehicle_type = None
            capacities = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle()
        return self._get_vehicle_type_representation(vehicle_type), capacities
