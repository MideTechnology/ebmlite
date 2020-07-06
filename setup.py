import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    'numpy',
    ]

TEST_REQUIRES = [
    'pytest',
    'codecov',
    'pytest-cov',
    ]

setuptools.setup(
        name='ebmlite',
        version='3.0.1',
        author='Mide Technology',
        author_email='help@mide.com',
        description='A lightweight, "pure Python" library for parsing EBML (Extensible Binary Markup Language) data.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/MideTechnology/ebmlite',
        license='MIT',
        classifiers=['Development Status :: 5 - Production/Stable',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',],
        keywords='ebml binary matroska webm',
        packages=setuptools.find_packages(),
        package_dir={'': '.'},
        package_data={
            '': ['schemata/*', 'tests/*.ide', 'tests/*.mkv']
        },
        test_suite='tests',
        install_requires=INSTALL_REQUIRES,
        extras_require={
            'test': INSTALL_REQUIRES + TEST_REQUIRES,
            },
)
