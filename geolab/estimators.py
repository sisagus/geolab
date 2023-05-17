"""This module provides functions for estimating soil engineering parameters."""

from typing import Optional

import numpy as np

from geolab import DECIMAL_PLACES, deg2rad


def skempton_compression_index(liquid_limit: float) -> float:
    """The compression index of the soil estimated from `Skempton` (1994)
    relation.

    $$C_c = 0.007 \left(LL - 10)$$

    Examples:
        >>> skempton_compression_index(30)
        0.14
        >>> skempton_compression_index(50)
        0.28
        >>> skempton_compression_index(20)
        0.07

    Args:
        liquid_limit: Water content beyond which soils flows under their own weight. (%)

    Returns:
        compression index of soil. (unitless)
    """
    compression_index = 0.007 * (liquid_limit - 10)

    return np.round(compression_index, DECIMAL_PLACES)


def terzaghi_compression_index(liquid_limit: float) -> float:
    r"""The compression index of the soil estimated from `Terzagi` and
    `Peck` (1967) relation.

    $$C_c = 0.009 \left(LL - 10 \right)$$

    Examples:
        >>> terzaghi_compression_index(30)
        0.18
        >>> terzaghi_compression_index(50)
        0.36
        >>> terzaghi_compression_index(20)
        0.09

    Args:
        liquid_limit: Water content beyond which soils flows under their own weight. (%)

    Returns:
        compression index of soil. (unitless)
    """
    compression_index = 0.009 * (liquid_limit - 10)

    return np.round(compression_index, DECIMAL_PLACES)


def hough_compression_index(void_ratio: float) -> float:
    r"""The compression index of the soil estimated from `Hough` (1957)
    relation.

    $$C_c = 0.29 \left(e_o - 0.27 \right)$$

    Examples:
        >>> hough_compression_index(0.3)
        0.01
        >>> hough_compression_index(0.5)
        0.07
        >>> hough_compression_index(0.27)
        0.0

    Args:
        void_ratio: Volume of voids divided by volume of solids. (unitless)

    Returns:
        compression index of soil. (unitless)
    """
    compression_index = 0.29 * (void_ratio - 0.27)

    return np.round(compression_index, DECIMAL_PLACES)


def elastic_modulus(spt_n60: float) -> float:
    r"""Elastic modulus of soil estimated from `Joseph Bowles` correlation.

    $$E_s = 320\left(N_{60} + 15 \right)$$

    Examples:
        >>> elastic_modulus(20)
        11200
        >>> elastic_modulus(30)
        14400
        >>> elastic_modulus(10)
        8000

    Args:
        spt_n60: The SPT N-value corrected for 60% hammer efficiency.

    Returns:
        Elastic modulus of the soil ($kN/m^2$)
    """
    _elastic_modulus = 320 * (spt_n60 + 15)

    return np.round(_elastic_modulus, DECIMAL_PLACES)


@deg2rad("friction_angle")
def foundation_depth(
    allowable_bearing_capacity: float,
    unit_weight_of_soil: float,
    *,
    friction_angle: float,
) -> float:
    r"""Depth of foundation estimated using `Rankine's` formula.

    $$D_f=\dfrac{Q_{all}}{\gamma}\left(\dfrac{1 - \sin \phi}{1 + \sin \phi}\right)^2$$

    Args:
        allowable_bearing_capacity: Allowable bearing capacity.
        unit_weight_of_soil: Unit weight of soil. ($kN/m^3$)
        friction_angle: Internal angle of friction. (degrees)

    Returns:
        foundation depth.
    """
    first_expr = allowable_bearing_capacity / unit_weight_of_soil
    second_expr = (1 - np.sin(friction_angle)) / (1 + np.sin(friction_angle))
    _foundation_depth = first_expr * (second_expr**2)

    return np.round(_foundation_depth, DECIMAL_PLACES)


def friction_angle(
    spt_n60,
    effective_overburden_pressure: Optional[float] = None,
    atmospheric_pressure: Optional[float] = None,
) -> float:
    r"""Estimation of the internal angle of friction using spt_n60.

    For cohesionless soils the coefficient of internal friction ($\phi$) was
    determined from the minimum value from `Peck, Hanson and Thornburn (1974)`
    and `Kullhawy and Mayne (1990)` respectively. The correlations are shown below.

    $$\phi = 27.1 + 0.3 \times N_{60} - 0.00054 \times (N_{60})^2$$

    $$\phi = \tan^{-1}\left[\dfrac{N_{60}}{12.2 + 20.3(\frac{\sigma_o}{P_a})} \right]^0.34$$

    Examples:
        >>> friction_angle(20)
        32.88
        >>> friction_angle(30)
        35.61
        >>> friction_angle(30, 18, 40)
        0.98
        >>> friction_angle(20, 18, 20)
        0.83
        >>> friction_angle(40, 10, 30)
        1.04

    Args:
        spt_n60: The SPT N-value corrected for 60% hammer efficiency. (blows/300 mm)
        effective_overburden_pressure: Effective overburden pressure. ($kN/m^2$)
        atmospheric_pressure: Atmospheric pressure in the same unit as
                              `effective_overburden_pressure`.

    Returns:
        The internal angle of friction in degrees.
    """
    if (effective_overburden_pressure is not None) and (
        atmospheric_pressure is not None
    ):
        den = 12.2 + 20.3 * (effective_overburden_pressure / atmospheric_pressure)
        phi = np.arctan(spt_n60 / den) ** 0.34
        return np.round(phi, 2)

    phi = 27.1 + (0.3 * spt_n60) - (0.00054 * (spt_n60**2))

    # rounded to 2 d.p for consistency with eng. practices
    return np.round(phi, DECIMAL_PLACES)


def stroud_undrained_shear_strength(spt_n60: float, k: float = 3.5) -> float:
    r"""Undrained shear strength estimated from the correlation developed by `Stroud`
    in 1974.

    $$C_u = K \times N_{60}$$

    Examples:
        >>> stroud_undrained_shear_strength(20)
        70.0
        >>> stroud_undrained_shear_strength(30, 4)
        120
        >>> stroud_undrained_shear_strength(40, 2.5)
        Traceback (most recent call last):
        ...
        ValueError: k should be 3.5 <= k <= 6.5 not 2.5
        >>> stroud_undrained_shear_strength(40, 7.5)
        Traceback (most recent call last):
        ...
        ValueError: k should be 3.5 <= k <= 6.5 not 7.5

    Args:
        spt_n60: The SPT N-value corrected for 60% hammer efficiency. (blows/300 mm)
        k: Stroud Parameter. ($kN/m^2$)

    Returns:
        undrained shear strength of the soil. ($kN/m^2$)
    """
    if not (3.5 <= k <= 6.5):
        raise ValueError(f"k should be 3.5 <= k <= 6.5 not {k}")

    shear_strength = k * spt_n60

    return np.round(shear_strength, DECIMAL_PLACES)


def skempton_undrained_shear_strength(
    effective_overburden_pressure: float, plasticity_index: float
):
    r"""Undrained shear strength estimated from the correlation developed by `Skempton`
    in 1957.

    The ratio $\frac{C_u}{\sigma_o}$ is a constant for a given clay.
    `Skempton` suggested that a similar constant ratio exists between the undrained shear
    strength of normally consolidated natural deposits and the effective overburden pressure.
    It has been established that the ratio ($\frac{C_u}{\sigma_o}$) is constant provided the
    plasticity index (PI) of the soil remains constant.

    The relationship is expressed as:

    $$\dfrac{C_u}{\sigma_o} = 0.11 + 0.0037 \times PI$$

    The value of the ratio ($\frac{C_u}{\sigma_o}$) determined in a consolidated-undrained test on
    undisturbed samples is generally greater than actual value because of anisotropic consolidation
    in the field. The actual value is best determined by `in-situ shear vane test`. (Arora, p. 330)

    Args:
        effective_overburden_pressure: Effective overburden pressure. ($kN/m^2$)
        plasticity_index: Range of water content over which soil remains in plastic condition
                          `PI = LL - PL`. (%)
    Returns:
        undrained shear strength of the soil. ($kN/m^2$)

    References:
        Arora, K 2003, _Soil Mechanics and Foundation Engineering_, 6 Edition,
        Standard Publishers Distributors, Delhi.
    """
    shear_strength = effective_overburden_pressure * (0.11 + 0.0037 * plasticity_index)

    return np.round(shear_strength, DECIMAL_PLACES)
