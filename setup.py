from setuptools import setup

setup(
  name = 'ppa6',
  packages = ['ppa6'],
  version = '0.5',
  license='MIT',
  description = 'Utility for printing on Peripage A6/A6+ via bluetooth',
  author = 'bitrate16',
  author_email = 'bitrate16@gmail.com',
  url = 'https://github.com/bitrate16/ppa6-python',
  download_url = 'https://github.com/bitrate16/ppa6-python/archive/v0.5.tar.gz',
  keywords = ['PERIPAGE', 'BLUETOOTH', 'THERMAL PRINTER', 'PRINTER'],
  install_requires=[
          'PyBluez>=0.23',
          'Pillow>=8.2.0',
		  'argparse>=1.1',
		  'qrcode>=6.1',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
  entry_points={
	'console_scripts': [
      'ppa6 = ppa6.__main__:main'  
	]
  }
)