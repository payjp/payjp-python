from setuptools import setup

install_requires = []


install_requires.append("requests >= 2.7.0")

setup(
    name="payjp",
    version="1.6.0",
    description="PAY.JP python bindings",
    author="PAY.JP",
    author_email="support@pay.jp",
    packages=["payjp", "payjp.test"],
    url="https://github.com/payjp/payjp-python",
    install_requires=install_requires,
    python_requires=">=3.0",
)
