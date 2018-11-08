import os

from setuptools import setup

from redistypes import __version__


f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
long_description = f.read()
f.close()


setup(
    name='redistypes',
    version=__version__,

    author='Vladimir Shkoda',
    author_email='vladimir.shkoda.51@gmail.com',

    description='Redis native types for Python',
    long_description=long_description,

    url='https://github.com/vladimirshkoda/redis-bindings',
    license='MIT',
    keywords=(
        'Redis key-value store bindings types descriptor orm'
    ),
    packages=['redistypes'],
    install_requires=['redis'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development',
    ],
)
