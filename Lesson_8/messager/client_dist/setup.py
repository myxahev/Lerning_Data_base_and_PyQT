from setuptools import setup, find_packages

setup(name="Messager_Petr_Smirnov",
      version="0.0.1",
      description="Messager Server",
      author="Petr Smirnov",
      author_email="",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
