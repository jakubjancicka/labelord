from setuptools import setup

with open('README') as f:
    long_description = ''.join(f.readlines())

setup(
    name='labelord_jancijak',
    version='0.4.0',
    description='Management of GitHub labels',
    long_description=long_description,
    keywords='Github,labels,management,synchronization',
    author='Jakub Jancicka',
    author_email='jakub.jancicka@fit.cvut.cz',
    license='GNU GPLv3',
    url='https://github.com/jakubjancicka/labelord',
    packages=['labelord'],
    package_data={'labelord': ['templates/*.html', 'static/*.css', 'config.cfg.sample']},
    install_requires=['flask', 'click', 'requests', 'configparser', 'werkzeug'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'betamax', 'flexmock'],   
    entry_points={
        'console_scripts': [
            'labelord = labelord.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
        ],
    zip_safe=False,
)
