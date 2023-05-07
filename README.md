# `geolab`: geotechnical engineering software for students and professionals

[![pypi](https://img.shields.io/badge/PyPi-Pato546-blue?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/user/Pato546/)
![license](https://img.shields.io/pypi/l/geolab?style=flat-square)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat-square&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![code style](https://img.shields.io/badge/code%20formatter-docformatter-fedcba.svg?style=flat-square)](https://github.com/PyCQA/docformatter)
[![style guide](https://img.shields.io/badge/%20style-google-3666d6.svg?style=flat-square)](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings)
![repo size](https://img.shields.io/github/repo-size/patrickboateng/geolab?style=flat-square&labelColor=ef8336)
![downloads](https://img.shields.io/pypi/dm/geolab?style=flat-square)

`geolab` is a computer program that implements technical and professional software for geotechnical engineering.
Some of the features of `geolab` are as follows:

- Soil Classification (`USCS` & `AASHTO`)
- Bearing Capacity Analysis (`Lab` & `Field`)
- Estimating Soil Engineering Properties (`void ratio`$\left(e_o\right)$, `modulus of elasticity`$\left(E_s\right)$, `internal angle of friction`$\left(\phi\right)$ etc)
- Settlement Analysis
- Finite Element Modelling (`FEM`) of soils under loads

## Installation

> **&#9432;** This install does not work yet.

```sh
pip install geolab
```

## Usage example

```py
>>> from geolab.soil_classifier import aashto, uscs

>>>  # element in data should be arranged as follows
>>>  # liquid limit, plastic limit, plasticity index, fines, sand, gravel
>>> data = [34.1, 21.1, 13, 47.88, 37.84, 14.28]
>>> uscs(liquid_limit=34.1, plastic_limit=21.1, plasticity_index=13, fines=47.88, sand=37.84, gravels=14.28)
'SC'
>>> aashto(liquid_limit=34.1, plastic_limit=21.1, plasticity_index=13, fines=47.88)
'A-6(3)'

```

<!-- ## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
``` -->

## Release History

- 0.1.0
  - **rapid** development.

## Contributing

1. [Fork it](https://github.com/patrickboateng/geolab/fork)
2. Create your feature branch (`git checkout -b feature`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature`)
5. Create a new Pull Request

## Todo

- [x] Soil Classifier
- [ ] Bearing Capacity Analysis
- [ ] Estimating Soil Engineering Parameters
- [ ] Settlement Analysis
- [ ] Modelling the behavior of Soils under loads using `FEM`
