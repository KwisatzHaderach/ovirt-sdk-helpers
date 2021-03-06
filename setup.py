from setuptools import setup, find_packages

setup(
    name='ovirt-sdk-helpers',
    version='0.1',
    description='Helpers for oVirt python sdk',
    url='https://github.com/KwisatzHaderach/ovirt-sdk-helpers',
    author='Petr Matyas',
    author_email='p.matyas13@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=['ovirt-engine-sdk-python'],
    zip_safe=False
)
