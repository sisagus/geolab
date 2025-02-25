"""This module provides functions for estimating soil engineering parameters."""

from typing import Any, Optional

from geolab import GeotechEng
from geolab.exceptions import EngineerTypeError
from geolab.utils import arctan, round_, sin


def check_eng(obj, **kwargs):
    if "eng" in kwargs:
        obj.eng = kwargs.get("eng")


def error_eng_msg(eng: GeotechEng):
    return f"{eng} is not a valid type for engineer"


class soil_unit_weight:
    """Calculates the moist, saturated and submerged unit weight of soil
       sample.

    :param spt_n60: spt N-value corrected for 60% hammer efficiency
    :type spt_n60: float
    """

    def __init__(self, spt_n60: float) -> None:
        self.spt_n60 = spt_n60

    def __call__(self) -> float:
        return self.moist

    @property
    @round_
    def moist(self) -> float:
        return 16.0 + 0.1 * self.spt_n60

    @property
    @round_
    def saturated(self) -> float:
        return 16.8 + 0.15 * self.spt_n60

    @property
    @round_
    def submerged(self) -> float:
        return 8.8 + 0.01 * self.spt_n60


class compression_index:
    r"""The compression index of the soil estimated from ``liquid limit`` or ``void_ratio``.

    The available correlations used are defined below; They are in the order ``Skempton (1994)``,
    ``Terzaghi and Peck (1967)`` and ``Hough (1957)``.

    .. math::

        C_c = 0.007 \left(LL - 10 \right)

        C_c = 0.009 \left(LL - 10 \right)

        C_c = 0.29 \left(e_o - 0.27 \right)

    :Example:

    :param liquid_limit: water content beyond which soils flows under their own weight (%)
    :type liquid_limit: float
    :param void_ratio: volume of voids divided by volume of solids (unitless)
    :type void_ratio: float
    :param eng: specifies the type of compression index formula to use. Available
                values are geolab.SKEMPTON, geolab.TERZAGHI and geolab.HOUGH
    :type eng: GeotechEng
    """

    def __init__(
        self,
        liquid_limit: float = 0.0,
        void_ratio: float = 0.0,
        eng: GeotechEng = GeotechEng.SKEMPTON,
    ) -> None:
        self.liquid_limit = liquid_limit
        self.void_ratio = void_ratio
        self.eng = eng

    def __call__(self, **kwargs) -> float:
        return self.estimate(**kwargs)  # type: ignore

    def _terzaghi_peck_compression_idx(self) -> float:
        return 0.009 * (self.liquid_limit - 10)

    def _skempton_compression_idx(self) -> float:
        return 0.007 * (self.liquid_limit - 10)

    def _hough_compression_idx(self) -> float:
        return 0.29 * (self.void_ratio - 0.27)

    @round_
    def estimate(self, **kwargs) -> float:
        """Returns the compression index of the soil sample (unitless)"""
        check_eng(self, **kwargs)

        comp_idx: float  # compression index

        if self.eng is GeotechEng.SKEMPTON:
            comp_idx = self._skempton_compression_idx()

        elif self.eng is GeotechEng.TERZAGHI:
            comp_idx = self._terzaghi_peck_compression_idx()

        elif self.eng is GeotechEng.HOUGH:
            comp_idx = self._hough_compression_idx()

        else:
            msg = error_eng_msg(self.eng)
            raise EngineerTypeError(msg)

        return comp_idx


class friction_angle:
    r"""Estimation of the internal angle of friction using spt_n60.

    For cohesionless soils the coefficient of internal friction :math:`\phi` was
    determined from the minimum value from ``Peck, Hanson and Thornburn (1974)``
    and ``Kullhawy and Mayne (1990)`` respectively. The correlations are shown below.

    .. math::

        \phi = 27.1 + 0.3 \times N_{60} - 0.00054 \times (N_{60})^2

        \phi = \tan^{-1}\left[\dfrac{N_{60}}{12.2 + 20.3(\frac{\sigma_o}{P_a})} \right]^0.34

    :Example:

    :param spt_n60: spt N-value corrected for 60% hammer efficiency
    :type spt_n60: float
    :param eop: effective overburden pressure :math:`kN/m^2`, defaults to None
    :type eop: float, optional
    :param atm_pressure: atmospheric pressure :math:`kN/m^2`, defaults to None
    :type atm_pressure: float, optional
    """

    def __init__(
        self,
        spt_n60,
        eop: float = 0,
        atm_pressure: float = 0,
        eng: GeotechEng = GeotechEng.PECK,
    ):
        self.spt_n60 = spt_n60
        self.eop = eop
        self.atm_pressure = atm_pressure
        self.eng = eng

    def __call__(self, **kwargs) -> float:
        return self.estimate(**kwargs)  # type: ignore

    def _peck_et_al_friction_angle(self) -> float:
        return 27.1 + (0.3 * self.spt_n60) - (0.00054 * (self.spt_n60**2))

    def _kullhawy_mayne_friction_angle(self) -> float:
        expr = self.spt_n60 / (12.2 + 20.3 * (self.eop / self.atm_pressure))
        return arctan(expr**0.34)

    @round_
    def estimate(self, **kwargs) -> float:
        """Internal angle of friction in degrees"""
        check_eng(self, **kwargs)

        _friction_angle: float

        if self.eng is GeotechEng.PECK:
            _friction_angle = self._peck_et_al_friction_angle()

        elif self.eng is GeotechEng.KULLHAWY:
            _friction_angle = self._kullhawy_mayne_friction_angle()

        else:
            msg = error_eng_msg(self.eng)
            raise EngineerTypeError(msg)

        return _friction_angle


class undrained_shear_strength:
    r"""Undrained shear strength.

    The available correlations used are defined below;

    .. math::

        Stroud (1974) \, \rightarrow C_u = K \times N_{60}

        Skempton (1957) \, \rightarrow \dfrac{C_u}{\sigma_o} = 0.11 + 0.0037 \times PI

    The ratio :math:`\frac{C_u}{\sigma_o}` is a constant for a given clay. ``Skempton``
    suggested that a similar constant ratio exists between the undrained shear strength
    of normally consolidated natural deposits and the effective overburden pressure.
    It has been established that the ratio :math:`\frac{C_u}{\sigma_o}` is constant provided the
    plasticity index (PI) of the soil remains constant.

    The value of the ratio :math:`\frac{C_u}{\sigma_o}` determined in a consolidated-undrained test on
    undisturbed samples is generally greater than actual value because of anisotropic consolidation
    in the field. The actual value is best determined by `in-situ shear vane test`.
    (:cite:author:`2003:arora`, p. 330)

    :param spt_n60: SPT N-value corrected for 60% hammer efficiency, defaults to None
    :type spt_n60: Optional[float], optional
    :param eop: effective overburden pressure :math:`kN/m^2`, defaults to None
    :type eop: Optional[float], optional
    :param plasticity_index: range of water content over which soil remains in plastic condition, defaults to None
    :type plasticity_index: Optional[float], optional
    :param k: stroud parameter, defaults to 3.5
    :type k: float, optional
    :param eng: specifies the type of undrained shear strength formula to use. Available values are
                geolab.STROUD and geolab.SKEMPTON, defaults to GeotechEng.STROUD
    :type eng: GeotechEng, optional

    :References:

        .. bibliography::
    """

    def __init__(
        self,
        spt_n60=0,
        eop=0,
        plasticity_index=0,
        k=3.5,
        eng: GeotechEng = GeotechEng.STROUD,
    ) -> None:
        self.spt_n60 = spt_n60
        self.eop = eop
        self.plasticity_index = plasticity_index
        self.k = k
        self.eng = eng

    def __call__(self, **kwargs) -> float:
        return self.estimate(**kwargs)

    def _stroud_undrained_shear_strength(self):
        if not (3.5 <= self.k <= 6.5):
            msg = f"k should be 3.5 <= k <= 6.5 not {self.k}"
            raise ValueError(msg)

        return self.k * self.spt_n60

    def _skempton_undrained_shear_strength(self):
        return self.eop * (0.11 + 0.0037 * self.plasticity_index)

    def estimate(self, **kwargs) -> float:
        check_eng(self, **kwargs)

        und_shr: float  # undrained shear strength

        if self.eng is GeotechEng.STROUD:
            und_shr = self._stroud_undrained_shear_strength()

        elif self.eng is GeotechEng.SKEMPTON:
            und_shr = self._skempton_undrained_shear_strength()

        else:
            msg = error_eng_msg(self.eng)
            raise EngineerTypeError(msg)

        return und_shr


class misc:
    @staticmethod
    def soil_elastic_modulus(spt_n60: float) -> float:
        r"""Elastic modulus of soil estimated from ``Joseph Bowles`` correlation.

        .. math::

            E_s = 320\left(N_{60} + 15 \right)

        :Example:
            >>> soil_elastic_modulus(20)
            11200
            >>> soil_elastic_modulus(30)
            14400
            >>> soil_elastic_modulus(10)
            8000

        :param spt_n60: spt N-value corrected for 60% hammer efficiency
        :type spt_n60: float
        :return: Elastic modulus of the soil :math:`kN/m^2`
        :rtype: float
        """
        return 320 * (spt_n60 + 15)

    @staticmethod
    def foundation_depth(
        allow_bearing_capacity: float,
        unit_weight_of_soil: float,
        friction_angle: float,
    ) -> float:
        r"""Depth of foundation estimated using ``Rankine's`` formula.

        .. math::

            D_f=\dfrac{Q_{all}}{\gamma}\left(\dfrac{1 - \sin \phi}{1 + \sin \phi}\right)^2

        :param allow_bearing_capacity: allowable bearing capacity
        :type allow_bearing_capaciy: float
        :param unit_weight_of_soil: unit weight of soil :math:`kN/m^3`
        :type unit_weight_of_soil: float
        :param friction_angle: internal angle of friction (degrees)
        :type friction_angle: float
        :return: depth of foundation
        :rtype: float
        """
        x1 = allow_bearing_capacity / unit_weight_of_soil
        x2 = (1 - sin(friction_angle)) / (1 + sin(friction_angle))

        return x1 * (x2**2)
