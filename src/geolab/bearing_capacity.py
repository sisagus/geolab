import functools

import numpy as np

from geolab.exceptions import FoundationTypeError


def _phi_to_radians(func):
    @functools.wraps(func)
    def wrapper(phi):
        return func(np.deg2rad(phi))

    return wrapper


@_phi_to_radians
def Kp(phi: float) -> float:
    r"""Coeffiecient of passive earth pressure ($K_p$).

    $$\dfrac{1 + \sin \phi}{1 - \sin \phi}$$

    Args:
        phi: Internal angle of friction (degrees).

    Returns:
        Passive earth pressure coefficient.
    """
    return (1 + np.sin(phi)) / (1 - np.sin(phi))


def _Nq(phi: float) -> float:
    num = np.exp(((3 * np.pi) / 2 - phi) * np.tan(phi))  # The numerator of the formula
    den = 2 * (
        np.cos(np.deg2rad(45) + (phi / 2)) ** 2
    )  # The denominator of the formula

    return num / den


class T:
    """Terzaghi Bearing Capacity Factors $N_c$, $N_q$, $N_\gamma$"""

    @staticmethod
    @_phi_to_radians
    def Nq(phi: float) -> float:
        r"""Terzaghi Bearing Capacity factor $N_q$.

        $$\frac{e^{(\frac{3\pi}{2} - \phi)\tan \phi}}{2 \cos^2 \left(45^{\circ} + \frac{\phi}{2} \right)}$$

        Args:
            phi: Internal angle of friction (degrees).

        Returns:
            A `float` representing the bearing capacity factor ($N_q$).
        """
        return np.round(_Nq(phi), 2)

    @staticmethod
    @_phi_to_radians
    def Nc(phi: float) -> float:
        r"""Terzaghi Bearing Capacity factor $N_c$.

        $$\cot \phi \left(N_q - 1 \right)$$

        Args:
            phi: Internal angle of friction (degrees).

        Returns:
            A `float` representing the bearing capacity factor $N_c$.
        """
        if np.isclose(phi, 0.0):
            return 5.70

        return np.round((1 / np.tan(phi)) * (_Nq(phi) - 1), 2)

    @staticmethod
    @_phi_to_radians
    def Ngamma(phi: float) -> float:
        r"""Terzaghi Bearing Capacity factor $N_\gamma$.

        $$\frac{1}{2}\left(\frac{K_p}{\cos^2 \phi} - 1 \right)\tan \phi$$

        - $K_p$ : coefficient of passive earth pressure.

        Args:
            phi: Internal angle of friction (degrees).

        Returns:
            A `float` representing the bearing capacity factor $N_\gamma$.
        """
        return 0.5 * ((Kp(np.rad2deg(phi)) / (np.cos(phi) ** 2)) - 1) * np.tan(phi)


def terzaghi_qult_4_strip_footing(
    cohesion: float,
    phi: float,
    gamma: float,
    depth_of_foundation: float,
    width_of_foundation: float,
) -> float:
    r"""Ultimate bearing capacity according to `Terzaghi` for `strip footing`.

    Args:
        cohesion: cohesion of foundation soil ($kN/m^2$).
        phi: Internal angle of friction ($\phi$)
        gamma: Unit weight of soil ($kN/m^3$).
        depth_of_foundation: Foundation depth $D_f$ (m).
        width_of_foundation: Foundation width (**B**) (m)

    Returns:
        Ultimate bearing capacity ($q_{ult}$)
    """
    qult = (
        cohesion * T.Nc(phi)
        + gamma * depth_of_foundation * T.Nq(phi)
        + 0.5 * gamma * width_of_foundation * T.Ngamma(phi)
    )

    return np.round(qult, 2)


def terzaghi_qult(
    cohesion: float,
    phi: float,
    gamma: float,
    depth_of_foundation: float,
    width_of_foundation: float,
    type_of_foundation: str = "s",
) -> float:
    r"""Ultimate bearing capacity according to `Terzaghi` for `strip footing`.

    Args:
        cohesion: cohesion of foundation soil ($kN/m^2$).
        phi: Internal angle of friction ($\phi$)
        gamma: Unit weight of soil ($kN/m^3$).
        depth_of_foundation: Foundation depth $D_f$ (m).
        width_of_foundation: Foundation width (**B**) (m)
        type_of_foundation: Determines the type of foundation. `s` or `square` for square foundation
                            and `c` or `circular` for circular foundation. Defaults to `s`.
    Returns:
        Ultimate bearing capacity ($q_{ult}$)
    """
    if type_of_foundation not in {"s", "c", "square", "circular"}:
        raise FoundationTypeError(
            f"Foundation type must be s or c not {type_of_foundation}"
        )

    i = 0.4 if type_of_foundation in {"s", "square"} else 0.3

    qult = (
        1.2 * cohesion * T.Nc(phi)
        + gamma * depth_of_foundation * T.Nq(phi)
        + i * gamma * width_of_foundation * T.Ngamma(phi)
    )

    return np.round(qult, 2)
