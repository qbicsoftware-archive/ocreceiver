from setuptools import setup

setup(name='ocreceiver',
      version='0.1',
      description='Listens for uploaded files and creates marker files for'
                  ' the dropboxhandler.',
      author="Sven Fillinger",
      author_email="sven.fillinger@qbic.uni-tuebingen.de",
      license='MIT',
      packages=['ocreceiver'],
      install_requires=[
            'pyyaml'
      ],
      scripts=['bin/ocreceiver']
)