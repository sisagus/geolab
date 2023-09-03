import math

from geolab import ERROR_TOLERANCE, GeotechEng
from geolab.utils import log10, mul, sqrt

r"""SPT N-value corrected for field procedures according to ``Skempton (1986)``.

        .. note::

            This correction is to be applied irrespective of the type of soil.

        .. math::

            N_{60} = \dfrac{E_m \times C_B \times C_s \times C_R \times N_r}{0.6}

        :param recorded_spt_nvalue: recorded SPT N-value (blows/300mm)
        :type recorded_spt_nvalue: int
        :param hammer_efficiency: hammer efficiency, defaults to 0.575
        :type hammer_efficiency: float, optional
        :param borehole_diameter_correction: borehole diameter correction, defaults to 1.0
        :type borehole_diameter_correction: float, optional
        :param sampler_correction: sampler correction, defaults to 1.0
        :type sampler_correction: float, optional
        :param rod_length_correction: rod Length correction, defaults to 0.75
        :type rod_length_correction: float
        :return: spt N-value corrected for 60% hammer efficiency
        :rtype: float

        SPT N-value Overburden Pressure Correction.


        Gibbs and Holtz (1957)
        ----------------------

        It was only as late as in ``1957`` that ``Gibbs and Holtz`` suggested that corrections
        should be made for field ``SPT`` values for depth. As the correction factor came to be
        considered only after ``1957``, all empirical data published before ``1957`` like those
        by ``Terzaghi`` is for uncorrected values of ``SPT``.

        In granular soils, the overburden pressure affects the penetration resistance.
        If two soils having same relative density but different confining pressures are tested,
        the one with a higher confining pressure gives a higher penetration number. As the
        confining pressure in cohesionless soils increases with the depth, the penetration number
        for soils at shallow depths is underestimated and that at greater depths is overestimated.
        For uniformity, the N-values obtained from field tests under different effective overburden
        pressures are corrected to a standard effective overburden pressure.
        ``Gibbs and Holtz (1957)`` recommend the use of the following equation for dry or moist clean
        sand. (:cite:author:`2003:arora`, p. 428)

        .. math::

            N = \dfrac{350}{\sigma_o + 70} \times N_R if \sigma_o \le 280kN/m^2

        .. note::

            :math:`\frac{N_c}{N_R}` should lie between 0.45 and 2.0, if :math:`\frac{N_c}{N_R}` is
            greater than 2.0, :math:`N_c` should be divided by 2.0 to obtain the design value used in
            finding the bearing capacity of the soil. (:cite:author:`2003:arora`, p. 428)

        Bazaraa and Peck (1969)
        -----------------------

        This is a correction given by ``Bazaraa (1967)`` and also by ``Peck and Bazaraa (1969)``
        and it is one of the commonly used corrections.
        According to them:

        .. math::

            N = \dfrac{4N_R}{1 + 0.0418\sigma_o} if \sigma_o \lt 71.8kN/m^2

            N = \dfrac{4N_R}{3.25 + 0.0104\sigma_o} if \sigma_o \gt 71.8kN/m^2

            N = N_R if \sigma_o = 71.8kN/m^2

        Peck, Hansen and Thornburn (1974)
        ---------------------------------

        .. math::

            (N_1)_{60} = C_N \times N_{60} \le 2N_{60}

            C_N = overburden \, pressure \, coefficient \, factor

            C_N = 0.77\log(\frac{1905}{\sigma})

        Liao and Whitman (1986)
        -----------------------

        .. math::

            C_N = \sqrt{\frac{100}{\sigma}}

        Skempton
        --------

        .. math::

            C_N = \dfrac{2}{1 + 0.01044\sigma_o}

        :param spt_n60: spt N-value corrected for 60% hammer efficiency
        :type spt_n60: float
        :param eop: effective overburden pressure :math:`kN/m^2`
        :type eop: float
        :param eng: specifies the type of overburden pressure correction formula to use.
                    Available values are geolab.GIBBS, geolab.BAZARAA, geolab.PECK, geolab.LIAO,
                    and geolab.SKEMPTON
        :type eng: GeotechEng
        :return: corrected SPT N-value
        :rtype: float

        References
        ----------

        .. bibliography::

 SPT N-value Dilatancy Correction.

        **Dilatancy Correction** is a correction for silty fine sands and fine sands
        below the water table that develop pore pressure which is not easily
        dissipated. The pore pressure increases the resistance of the soil hence the
        penetration number (N). (:cite:author:`2003:arora`)

        Correction of silty fine sands recommended by ``Terzaghi and Peck (1967)`` if
        :math:`N_{60}` exceeds 15.

        .. math::

            N_c = 15 + \frac{1}{2}\left(N_{60} - 15\right) if N_{60} \gt 15

            N_c = N_{60} if N_{60} \le 15

        :param spt_n60: spt N-value corrected for 60% hammer efficiency
        :type spt_n60: float
        :return: corrected SPT N-value

        References
        ----------

        .. bibliography::   
"""


class spt_corrections:
    def __init__(
        self,
        recorded_spt_nvalue: int,
        *,
        hammer_efficiency: float = 0.6,
        borehole_diameter_correction: float = 1.0,
        sampler_correction: float = 1.0,
        rod_length_correction: float = 0.75,
        eop: float = 0.0,
        eng: GeotechEng = GeotechEng.SKEMPTON,
    ):
        self.recorded_spt_nvalue = recorded_spt_nvalue
        self.hammer_efficiency = hammer_efficiency
        self.borehole_diameter_correction = borehole_diameter_correction
        self.sampler_correction = sampler_correction
        self.rod_length_correction = rod_length_correction
        self.eop = eop
        self.eng = eng

    def __call__(self, recorded_spt_nvalue: float = 0) -> float:
        if recorded_spt_nvalue:
            self.recorded_spt_nvalue = recorded_spt_nvalue
        return self.overburden_pressure_spt_correction()

    def _skempton_opc(self) -> float:
        return (2 / (1 + 0.01044 * self.eop)) * self.spt_n60

    def _bazaraa_opc(self) -> float:
        corr_spt: float  # corrected spt n-value

        std_pressure = 71.8

        if math.isclose(self.eop, std_pressure, rel_tol=ERROR_TOLERANCE):
            corr_spt = self.spt_n60

        elif self.eop < std_pressure:
            corr_spt = 4 * self.spt_n60 / (1 + 0.0418 * self.eop)

        else:
            corr_spt = 4 * self.spt_n60 / (3.25 + 0.0104 * self.eop)

        return corr_spt

    def _gibbs_holtz_opc(self) -> float:
        corr_spt: float

        std_pressure = 280

        if self.eop > std_pressure:
            msg = f"{self.eop} should be less than or equal to {std_pressure}"
            raise ValueError(msg)

        corr_spt = self.spt_n60 * (350 / (self.eop + 70))
        spt_ratio = corr_spt / self.spt_n60

        if 0.45 < spt_ratio < 2.0:
            return corr_spt

        return corr_spt / 2 if spt_ratio > 2.0 else corr_spt

    def _peck_opc(self) -> float:
        std_pressure = 24

        if self.eop < std_pressure:
            msg = (
                f"{self.eop} should be greater than or equal to {std_pressure}"
            )
            raise ValueError(msg)

        return 0.77 * log10(1905 / self.eop) * self.spt_n60

    def _liao_whitman_opc(self) -> float:
        return sqrt(100 / self.eop) * self.spt_n60

    @property
    def spt_n60(self) -> float:
        correction = mul(
            self.hammer_efficiency,
            self.borehole_diameter_correction,
            self.sampler_correction,
            self.rod_length_correction,
        )

        return (correction * self.recorded_spt_nvalue) / 0.6

    def dilatancy_spt_correction(self) -> float:
        """Returns the dilatancy spt correction."""
        return (
            self.spt_n60
            if self.spt_n60 <= 15
            else 15 + 0.5 * (self.spt_n60 - 15)
        )

    def overburden_pressure_spt_correction(self) -> float:
        """Returns the overburden pressure spt correction."""
        opc: float

        if self.eng is GeotechEng.GIBBS:
            opc = self._gibbs_holtz_opc()

        elif self.eng is GeotechEng.BAZARAA:
            opc = self._bazaraa_opc()

        elif self.eng is GeotechEng.PECK:
            opc = self._peck_opc()

        elif self.eng is GeotechEng.LIAO:
            opc = self._liao_whitman_opc()

        elif self.eng is GeotechEng.SKEMPTON:
            opc = self._skempton_opc()

        else:
            msg = f"{self.eng} is not a valid type for overburden pressure spt correction"
            raise TypeError(msg)

        return opc