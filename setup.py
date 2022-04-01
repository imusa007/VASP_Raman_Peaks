from setuptools import setup

setup(
    name='Raman',
    version='1.0',
    py_modules=['raman'],
    install_requires=[
        'ase==3.19.1',
        'click==7.1.2',
        'cycler==0.10.0',
        'kiwisolver==1.2.0',
        'matplotlib==3.2.2',
        'numpy==1.19.0',
        'pyparsing==2.4.7',
        'python-dateutil==2.8.1',
        'scipy==1.5.0',
        'six==1.15.0',
    ],
    entry_points='''
        [console_scripts]
        raman=raman:cli
    '''

)