from setuptools import setup

setup(
    name='alarmcenter',
    version='0.0.0',
    description='A "little thought invested" approach to ingesting Dahua alarms',
    url='https://github.com/w531t4/alarmcenter',
    author='Aaron White',
    author_email='w531t4@gmail.com',
    license='GPL-3.0-or-later',
    packages=['alarmcenter'],
    install_requires=['redis>=2.10.6',
                      ],
    entry_points = {
        'console_scripts': ['alarmcenter=alarmcenter.command_line:main'],
    }
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Topic :: System :: Logging',
        'Programming Language :: Python :: 3.11',
    ],
)