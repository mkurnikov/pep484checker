from setuptools import setup, find_packages

setup(
    name='pep484checker',
    version='0.1.0',
    description='Reference implementation of the runtime checker for PEP484.',
    url='https://github.com/mkurnikov/pep484checker',

    author='Maxim Kurnikov',
    author_email='maxim.kurnikov@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5'
    ],
    packages=find_packages(exclude=['tests'])
)