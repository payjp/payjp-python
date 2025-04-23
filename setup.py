import sys

from setuptools import setup

install_requires = []

if sys.version_info < (3, 8):
    raise DeprecationWarning(
        "Python versions below 3.8 are no longer supported by PAY.JP. Please use Python 3.8 or higher."
    )

install_requires.append("requests >= 2.7.0")

setup(
    name="payjp",
    version="1.6.1",
    description="PAY.JP python bindings",
    author="PAY.JP",
    author_email="support@pay.jp",
    packages=["payjp", "payjp.test"],
    url="https://github.com/payjp/payjp-python",
    install_requires=install_requires,
    python_requires=">=3.0",
)
