from distutils.core import setup
setup(
  name = 'ppa6',
  packages = ['ppa6'],
  version = '0.1',
  license='MIT',
  description = 'Utility for printing on Peripage A6/A6+ via bluetooth',
  author = 'bitrate16',
  author_email = 'bitrate16@gmail.com',
  url = 'https://github.com/bitrate16/ppa6-python',
  download_url = 'https://github.com/bitrate16/ppa6-python/archive/v_01.tar.gz',
  keywords = ['PERIPAGE', 'BLUETOOTH', 'THERMAL PRINTER', 'PRINTER'],
  install_requires=[
          'PyBluez==0.3',
          'Pillow==8.1.2',
		  'argparse==1.1',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)