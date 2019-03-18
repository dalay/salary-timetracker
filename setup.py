from os.path import join, dirname
from setuptools import setup, find_packages
import timetracker


setup(
    name='salary-timetracker',
    version=timetracker.__version__,
    description='A simple and easy timetracker for loging working hours and automatic wage calculation.',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    license='GPL',
    packages=find_packages(),
    test_suite='tests',
    entry_points={
            'console_scripts': [
                'tt = timetracker:main',
                'timetracker = timetracker:main'
            ]
    },
    author='Alexandr Jurow',
    author_email='pythonwayru@gmail.com',
    url='http://github.com/dalay/salary-timetracker',
    keywords=['timetracker', 'salary', 'freelance'],
    install_requires=['prettytable'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
)
