"""Terzaghi Bearing Capacity Analysis."""

from types import SimpleNamespace

from geolab import GeotechEng
from geolab.bearing_capacity import (
    FootingShape,
    FoundationSize,
    BearingCapacityFactors,
)
from geolab.utils import PI, cos, deg2rad, exp, mul, round_, tan


def _nc(phi: float) -> float:
    num = exp(((3 * PI) / 2 - deg2rad(phi)) * tan(phi))
    den = 2 * (cos(45 + (phi / 2)) ** 2)

    return num / den


def _nq(phi: float) -> float:
    return (1 / tan(phi)) * (_nq(phi) - 1)


def _ngamma(phi: float, eng: GeotechEng = GeotechEng.MEYERHOF):
    if eng is GeotechEng.MEYERHOF:
        return (_nq(phi) - 1) * tan(1.4 * phi)
    if eng is GeotechEng.HANSEN:
        return 1.8 * (_nq(phi) - 1) * tan(phi)
    msg = f"Available types are {GeotechEng.MEYERHOF} or {GeotechEng.HANSEN}"
    raise TypeError(msg)


def _qult_4_strip_footing(
    cohesion: float,
    soil_unit_weight: float,
    foundation_size: FoundationSize,
    bcf: BearingCapacityFactors,
) -> float:
    return (
        mul(cohesion, bcf.nc)
        + mul(soil_unit_weight, foundation_size.depth, bcf.nq)
        + mul(
            0.5,
            soil_unit_weight,
            foundation_size.footing_size.width,
            bcf.ngamma,
        )
    )


def _qult_4_square_footing(
    cohesion: float,
    soil_unit_weight: float,
    foundation_size: FoundationSize,
    bcf: BearingCapacityFactors,
):
    return (
        mul(1.2, cohesion, bcf.nc)
        + mul(soil_unit_weight, foundation_size.depth, bcf.nq)
        + mul(
            0.4,
            soil_unit_weight,
            foundation_size.footing_size.width,
            bcf.ngamma,
        )
    )


def _qult_4_circular_footing(
    cohesion: float,
    soil_unit_weight: float,
    foundation_size: FoundationSize,
    bcf: BearingCapacityFactors,
):
    return (
        mul(1.2, cohesion, bcf.nc)
        + mul(soil_unit_weight, foundation_size.depth, bcf.nq)
        + mul(
            0.3,
            soil_unit_weight,
            foundation_size.footing_size.width,
            bcf.ngamma,
        )
    )


class TerzaghiBearingCapacity:
    """Terzaghi Bearing Capacity.

    :param cohesion: cohesion of foundation soil :math:`(kN/m^2)`
    :type cohesion: float
    :param friction_angle: internal angle of friction (degrees)
    :type friction_angle: float
    :param soil_unit_weight: unit weight of soil :math:`(kN/m^3)`
    :type soil_unit_weight: float
    :param foundation_depth: depth of foundation :math:`d_f` (m)
    :type foundation_depth: float
    :param foundation_width: width of foundation (**B**) (m)
    :type foundation_width: float
    :param eng: specifies the type of ngamma formula to use. Available
                values are geolab.MEYERHOF and geolab.HANSEN
    :type eng: GeotechEng
    """

    def __init__(
        self,
        cohesion: float,
        friction_angle: float,
        soil_unit_weight: float,
        foundation_size: FoundationSize,
        footing_shape: FootingShape = FootingShape.SQUARE_FOOTING,
        eng: GeotechEng = GeotechEng.MEYERHOF,
    ) -> None:
        self.cohesion = cohesion
        self.soil_unit_weight = soil_unit_weight
        self.foundation_size = foundation_size
        self.friction_angle = friction_angle
        self.footing_shape = footing_shape
        self.eng = eng

    @property
    @round_
    def nc(self) -> float:
        r"""Terzaghi Bearing Capacity factor :math:`N_c`.

        .. math::

            N_c = \cot \phi \left(N_q - 1 \right)

        :return: The bearing capacity factor :math:`N_c`
        :rtype: float
        """
        return _nc(self.friction_angle)

    @property
    @round_
    def nq(self) -> float:
        r"""Terzaghi Bearing Capacity factor :math:`N_q`.

        .. math::

            N_q=\dfrac{e^{(\frac{3\pi}{2}-\phi)\tan\phi}}{2\cos^2\left(45^{\circ}+\frac{\phi}{2}\right)}

        :return: The bearing capacity factor :math:`N_q`
        :rtype: float
        """
        return _nq(self.friction_angle)

    @property
    @round_
    def ngamma(self) -> float:
        r"""Terzaghi Bearing Capacity factor :math:`N_\gamma`.

        .. note::

            Exact values of :math:`N_\gamma` are not directly obtainable; values have
            been proposed by ``Brinch Hansen (1968)`` which are widely used in Europe,
            and also by ``Meyerhof (1963)``, which have been adopted in North America.

        The formulas shown below are ``Brinch Hansen`` and ``Meyerhof`` respectively.

        .. math::

            N_\gamma = 1.8 \left(N_q - 1 \right) \tan \phi

            N_\gamma = \left(N_q -1 \right)\tan(1.4\phi)

        :return: The bearing capacity factor :math:`N_\gamma`
        :rtype: float
        """
        return _ngamma(self.friction_angle, self.eng)

    @round_
    def ultimate_bearing_capacity(self) -> float:
        r"""Ultimate bearing capacity according to ``Terzaghi`` for ``strip footing``, ``square footing``
        and ``circular footing``.

        STRIP FOOTING
        -------------

        .. math::

            q_u = cN_c + \gamma D_f N_q + 0.5 \gamma B N_\gamma

        SQUARE FOOTING
        --------------

        .. math::

            q_u = 1.2cN_c + \gamma D_f N_q + 0.4 \gamma B N_\gamma

        CIRCULAR FOOTING
        ----------------

        .. math::

            q_u = 1.2cN_c + \gamma D_f N_q + 0.3 \gamma B N_{\gamma}

        :return: ultimate bearing capacity of the soil :math:`(q_{ult})`
        :rtype: float
        """
        bcf = SimpleNamespace(nc=self.nc, nq=self.nq, ngamma=self.ngamma)

        if self.footing_shape is FootingShape.STRIP_FOOTING:
            return _qult_4_strip_footing(
                self.cohesion,
                self.soil_unit_weight,
                self.foundation_size,
                bcf,
            )

        if self.footing_shape is FootingShape.SQUARE_FOOTING:
            return _qult_4_square_footing(
                self.cohesion,
                self.soil_unit_weight,
                self.foundation_size,
                bcf,
            )

        if self.footing_shape is FootingShape.CIRCULAR_FOOTING:
            return _qult_4_circular_footing(
                self.cohesion,
                self.soil_unit_weight,
                self.foundation_size,
                bcf,
            )

        msg = ""
        raise TypeError(msg)
