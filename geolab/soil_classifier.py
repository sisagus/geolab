r"""This module provides the implementations for ``USCS`` and ``AASHTO`` classification.

"""

import math
from typing import Optional

from geolab import ERROR_TOLERANCE, exceptions
from geolab.utils import round_

GRAVEL = "G"
SAND = "S"
CLAY = "C"
SILT = "M"
WELL_GRADED = "W"
POORLY_GRADED = "P"
ORGANIC = "O"
LOW_PLASTICITY = "L"
HIGH_PLASTICITY = "H"


def _check_size_distribution(fines: float, sand: float, gravel: float):
    total_aggregate = fines + sand + gravel
    if not math.isclose(total_aggregate, 100, rel_tol=ERROR_TOLERANCE):
        msg = f"fines + sand + gravels = 100% not {total_aggregate}"
        raise exceptions.PSDValueError(msg)


def _check_plasticity_idx(
    liquid_limit: float, plastic_limit: float, plasticity_index: float
):
    plasticity_idx = liquid_limit - plastic_limit
    if not math.isclose(
        plasticity_idx, plasticity_index, rel_tol=ERROR_TOLERANCE
    ):
        msg = f"PI should be equal to {plasticity_idx} not {plasticity_index}"
        raise exceptions.PIValueError(msg)


class AtterbergLimits:
    """Atterberg Limits."""

    def __init__(
        self,
        liquid_limit: float,
        plastic_limit: float,
        plasticity_index: float,
    ):
        _check_plasticity_idx(liquid_limit, plastic_limit, plasticity_index)

        self.liquid_limit = liquid_limit
        self.plastic_limit = plastic_limit
        self.plasticity_index = plasticity_index

    @property
    @round_(precision=2)
    def A_line(self) -> float:
        r"""Calculates the ``A-line``.

        .. math::

            0.73 \left(LL - 20 \right)

        """
        return 0.73 * (self.liquid_limit - 20)

    @property
    def fine_soil(self) -> str:
        """Returns the type of fine soil."""
        return CLAY if self.above_A_line() else SILT

    def above_A_line(self) -> bool:
        """Checks if the soil sample is above A-Line."""
        return self.plasticity_index > self.A_line

    def limit_plot_in_hatched_zone(self) -> bool:
        """Checks if soil sample plot in the hatched zone."""
        return math.isclose(self.plasticity_index, self.A_line)


class PSD:
    """Particle Size Distribution."""

    def __init__(
        self,
        fines: float,
        sand: float,
        gravel: float,
        d10: float = 0,
        d30: float = 0,
        d60: float = 0,
    ) -> None:
        _check_size_distribution(fines, sand, gravel)

        self.fines = fines
        self.sand = sand
        self.gravel = gravel
        self.d10 = d10
        self.d30 = d30
        self.d60 = d60

    def has_particle_sizes(self) -> bool:
        """Checks if soil sample has particle sizes."""
        return all((self.d10, self.d30, self.d60))

    def grade(self, coarse_soil: str) -> str:
        """Returns the grading of the soil sample."""
        soil_grade: str

        # Gravel
        if coarse_soil == GRAVEL:
            if (
                1 < self.curvature_coefficient < 3
                and self.uniformity_coefficient >= 4
            ):
                soil_grade = WELL_GRADED

            else:
                soil_grade = POORLY_GRADED

        # Sand
        else:
            if (
                1 < self.curvature_coefficient < 3
                and self.uniformity_coefficient >= 6
            ):
                soil_grade = WELL_GRADED

            else:
                soil_grade = POORLY_GRADED

        return soil_grade

    @property
    @round_(precision=2)
    def curvature_coefficient(self) -> float:
        r"""Returns the coefficient of curvature of the soil.

        .. math::

            C_c = \dfrac{d_{30}^2}{d_{60} \times d_{10}}
        """
        return (self.d30**2) / (self.d60 * self.d10)

    @property
    @round_(precision=2)
    def uniformity_coefficient(self) -> float:
        r"""Returns the coefficient of uniformity of the soil.

        .. math::

            C_u = \dfrac{d_{60}}{d_{10}}
        """
        return self.d60 / self.d10


class AASHTO:
    """American Association of State Highway and Transportation Officials (``AASHTO``)
    classification system.

    The AASHTO Classification system categorizes soils for highways based on
    Particle Size Distribution and plasticity characteristics. It classifies
    both coarse-grained and fine-grained soils into eight main groups (A1 to A7)
    with subgroups, along with a separate category (A8) for organic soils.

    :param liquid_limit: Water content beyond which soils flows under their own weight (%)
    :type liquid_limit: float
    :param plasticity_index: Range of water content over which soil remains in plastic condition (%)
    :param fines: Percentage of fines in soil sample (%)
    :type fines: float
    """

    def __init__(
        self,
        liquid_limit: float,
        plasticity_index: float,
        fines: float,
    ) -> None:
        self.liquid_limit = liquid_limit
        self.plasticity_index = plasticity_index
        self.fines = fines

    @round_(precision=0)
    def group_index(self) -> float:
        """Returns the ``Group Index GI`` of the soil sample.

        The ``(GI)`` is used to further evaluate soils with a group (subgroups).

        .. math::

            GI = (F_{200} - 35)[0.2 + 0.005(LL - 40)] + 0.01(F_{200} - 15)(PI - 10)
        """
        x_1 = 0 if (x := self.fines - 35) < 0 else min(x, 40)
        x_2 = 0 if (x := self.liquid_limit - 40) < 0 else min(x, 20)
        x_3 = 0 if (x := self.fines - 15) < 0 else min(x, 40)
        x_4 = 0 if (x := self.plasticity_index - 10) < 0 else min(x, 20)
        grp_idx = x_1 * (0.2 + 0.005 * x_2) + 0.01 * x_3 * x_4

        return 0.0 if grp_idx <= 0 else grp_idx

    def classify(self) -> str:
        """Returns the AASHTO classification of the soil sample."""
        clf: str  # soil classification
        grp_idx = self.group_index()
        grp_idx = f"{grp_idx:.0f}"  # convert grp_idx to a whole number

        if self.fines <= 35:
            if self.liquid_limit <= 40:
                if self.plasticity_index <= 10:
                    clf = f"A-2-4({grp_idx})"
                else:
                    clf = f"A-2-6({grp_idx})"

            else:
                if self.plasticity_index <= 10:
                    clf = f"A-2-5({grp_idx})"
                else:
                    clf = f"A-2-7({grp_idx})"

        # Silts A4-A7
        else:
            if self.liquid_limit <= 40:
                if self.plasticity_index <= 10:
                    clf = f"A-4({grp_idx})"
                else:
                    clf = f"A-6({grp_idx})"

            else:
                if self.plasticity_index <= 10:
                    clf = f"A-5({grp_idx})"
                else:
                    if self.plasticity_index <= (self.liquid_limit - 30):
                        clf = f"A-7-5({grp_idx})"
                    else:
                        clf = f"A-7-6({grp_idx})"

        return clf


class USCS:
    """Unified Soil Classification System (``USCS``).

    The Unified Soil Classification System, initially developed by Casagrande in 1948
    and later modified in 1952, is widely utilized in engineering projects involving soils.
    It is the most popular system for soil classification and is similar to Casagrande's
    Classification System. The system relies on Particle Size Distribution and Atterberg Limits
    for classification. Soils are categorized into three main groups: coarse-grained, fine-grained,
    and highly organic soils. Additionally, the system has been adopted by the American Society for
    Testing and Materials (``ASTM``).

    :param liquid_limit: Water content beyond which soils flows under their own weight (%)
    :type liquid_limit: float
    :param plastic_limit: Water content at which plastic deformation can be initiated (%)
    :type plastic_limit: float
    :param plasticity_index: Range of water content over which soil remains in plastic condition (%)
    :type plasticity_index: float
    :param fines: Percentage of fines in soil sample (%)
    :type fines: float
    :param sand: Percentage of sand in soil sample (%)
    :type sand: float
    :param gravel: Percentage of gravel in soil sample (%)
    :type gravel: float
    :param d10: Diameter at which 30% of the soil by weight is finer
    :type d10: float
    :param d30: Diameter at which 30% of the soil by weight is finer
    :type d30: float
    :param d60: Diameter at which 60% of the soil by weight is finer
    :type d60: float
    :raises exceptions.PIValueError: Raised when ``PI`` is not equal to ``LL - PL``
    :raises exceptions.PSDValueError: Raised when soil aggregates does not approximately sum to 100%
    """

    def __init__(
        self,
        liquid_limit: float,
        plastic_limit: float,
        plasticity_index: float,
        fines: float,
        sand: float,
        gravel: float,
        *,
        d10: float = 0,
        d30: float = 0,
        d60: float = 0,
        organic: Optional[bool] = False,
    ) -> None:
        self.atterberg_limits = AtterbergLimits(
            liquid_limit,
            plastic_limit,
            plasticity_index,
        )
        self.psd = PSD(fines, sand, gravel, d10, d30, d60)
        self.organic = organic

    def _dual_soil_classifier(self, coarse_soil: str) -> str:
        _soil_grd = self.psd.grade(coarse_soil)
        fine_soil = self.atterberg_limits.fine_soil
        return f"{coarse_soil}{_soil_grd}-{coarse_soil}{fine_soil}"

    def _classify_coarse_soil(self, coarse_soil: str) -> str:
        clf: str  # soil classification

        if self.psd.fines > 12:
            if self.atterberg_limits.limit_plot_in_hatched_zone():
                clf = f"{coarse_soil}{SILT}-{coarse_soil}{CLAY}"

            elif self.atterberg_limits.above_A_line():
                clf = f"{coarse_soil}{CLAY}"

            else:
                clf = f"{coarse_soil}{SILT}"

        elif 5 <= self.psd.fines <= 12:
            # Requires dual symbol based on graduation and plasticity chart
            if self.psd.has_particle_sizes():
                clf = self._dual_soil_classifier(coarse_soil)

            else:
                clf = (
                    f"{coarse_soil}{WELL_GRADED}-{coarse_soil}{SILT},"
                    f"{coarse_soil}{POORLY_GRADED}-{coarse_soil}{SILT},"
                    f"{coarse_soil}{WELL_GRADED}-{coarse_soil}{CLAY},"
                    f"{coarse_soil}{POORLY_GRADED}-{coarse_soil}{CLAY}"
                )

        # Less than 5% pass No. 200 sieve
        # Obtain Cc and Cu from grain size graph
        else:
            if self.psd.has_particle_sizes():
                _soil_grd = self.psd.grade(coarse_soil)
                clf = f"{coarse_soil}{_soil_grd}"

            else:
                clf = f"{coarse_soil}{WELL_GRADED} or {coarse_soil}{POORLY_GRADED}"

        return clf

    def _classify_fine_soil(self) -> str:
        clf: str  # soil classification

        if self.atterberg_limits.liquid_limit < 50:
            # Low LL
            if (self.atterberg_limits.above_A_line()) and (
                self.atterberg_limits.plasticity_index > 7
            ):
                clf = f"{CLAY}{LOW_PLASTICITY}"

            elif (not self.atterberg_limits.above_A_line()) or (
                self.atterberg_limits.plasticity_index < 4
            ):
                if self.organic:
                    clf = f"{ORGANIC}{LOW_PLASTICITY}"

                else:
                    clf = f"{SILT}{LOW_PLASTICITY}"

            # Limits plot in hatched area on plasticity chart
            else:
                clf = f"{SILT}{LOW_PLASTICITY}-{CLAY}{LOW_PLASTICITY}"

        # High LL
        else:
            # Above A-Line
            if self.atterberg_limits.above_A_line():
                clf = f"{CLAY}{HIGH_PLASTICITY}"

            # Below A-Line
            else:
                if self.organic:
                    clf = f"{ORGANIC}{HIGH_PLASTICITY}"
                else:
                    clf = f"{SILT}{HIGH_PLASTICITY}"

        return clf

    def classify(self) -> str:
        """Returns the ``USCS`` classification of the soil."""
        if self.psd.fines < 50:
            # Coarse grained, Run Sieve Analysis
            if self.psd.gravel > self.psd.sand:
                # Gravel
                return self._classify_coarse_soil(coarse_soil=GRAVEL)

            # Sand
            return self._classify_coarse_soil(coarse_soil=SAND)

        # Fine grained, Run Atterberg
        return self._classify_fine_soil()
