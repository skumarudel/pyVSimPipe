from setuptools import setup, find_packages

setup(
    name='pyVSimPipe',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'click',
        'pymysql',
        'pandas'
    ],
    include_package_data=True,
    entry_points='''
        [console_scripts]
        VSimPipe=pyVSimPipe.script.VSimPipe:cli
    '''
)
