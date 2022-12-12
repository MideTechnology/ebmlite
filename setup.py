import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
#    'numpy',
    ]

TEST_REQUIRES = [
    'pytest>=4.6',
    'codecov',
    'pytest-cov',
    'flake8<5.0',
    'pytest-flake8',
    'pytest-console-scripts',
    'pytest-xdist[psutil]',
    'filelock',
    ]

setuptools.setup(
        name='ebmlite',
        version='3.3.1',
        author='Mide Technology',
        author_email='help@mide.com',
        description='A lightweight, "pure Python" library for parsing EBML (Extensible Binary Markup Language) data.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/MideTechnology/ebmlite/tree/master',
        license='MIT',
        classifiers=['Development Status :: 5 - Production/Stable',
                     'License :: OSI Approved :: MIT License',
                     'Natural Language :: English',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Programming Language :: Python :: 3.10',
                     'Programming Language :: Python :: 3.11',
                     ],
        keywords='ebml binary matroska webm',
        packages=setuptools.find_packages(exclude="tests"),
        package_dir={'': '.'},
        package_data={
            '': ['schemata/*']
        },
        entry_points={'console_scripts': [
            'view-ebml=ebmlite.tools.view_ebml:main',
            'ebml2xml=ebmlite.tools.ebml2xml:main',
            'xml2ebml=ebmlite.tools.xml2ebml:main',
            'list-schemata=ebmlite.tools.list_schemata:main',
        ]},
        test_suite='tests',
        install_requires=INSTALL_REQUIRES,
        extras_require={
            'test': INSTALL_REQUIRES + TEST_REQUIRES,
            },
)
