"""Setup configuration for aspect_control package."""

import os
from glob import glob
from setuptools import setup

package_name = 'aspect_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kirill',
    maintainer_email='boychenkokirill@gmail.com',
    description='Teleoperation and low-level control nodes for the ASPECT lunar rover',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_node = aspect_control.teleop_node:main',
        ],
    },
)
