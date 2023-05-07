from setuptools import setup

setup(
    name = 'peripage',
    packages = ['peripage'],
    version = '1.1',
    license='MIT',
    description = 'Utility for printing on Peripage printers via bluetooth',
    author = 'bitrate16',
    author_email = 'bitrate16@gmail.com',
    url = 'https://github.com/bitrate16/peripage-python',
    download_url = 'https://github.com/bitrate16/peripage-python/archive/v1.1.tar.gz',
    keywords = ['PERIPAGE', 'BLUETOOTH', 'THERMAL PRINTER', 'PRINTER'],
    install_requires=[
        'PyBluez>=0.23',
        'Pillow>=8.2.0',
        'argparse>=1.1',
        'qrcode>=6.1',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    entry_points={
        'console_scripts': [
            'peripage = peripage.__main__:main'
        ]
    }
)
