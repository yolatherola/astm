from setuptools import setup, find_packages

setup(
    name='astm',  # Укажите название вашего пакета
    version='0.1',  # Укажите версию вашего пакета
    packages=find_packages(),  # Найти все пакеты внутри вашего проекта автоматически
    install_requires=[
        'Django==4.2.5'
        # Добавьте другие зависимости, если они есть
    ],
)