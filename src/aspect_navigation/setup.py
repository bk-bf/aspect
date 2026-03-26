"""Setup configuration for aspect_navigation package."""

import os
from glob import glob
from setuptools import setup

package_name = 'aspect_navigation'

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
    description='Waypoint navigation nodes for the ASPECT lunar rover',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simple_waypoint_nav = aspect_navigation.simple_waypoint_nav:main',
        ],
    },
)
