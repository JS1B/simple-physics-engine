from setuptools import setup, find_packages

setup(
    name='SimplePhysicsEngine',
    version='0.1',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'pygame',
        'PyOpenGL',
        'numpy',
    ],
    description='A simple simulation engine with basic physics and collision detection.',
    author='Piotr Krzemiński',
    author_email='p.krzeminski7@gmail.com',
    url='https://github.com/JS1B/simple-physics-engine',
)