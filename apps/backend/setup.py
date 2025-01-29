from setuptools import setup, find_packages

setup(
    name='sluggers',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'google-generativeai',
        'google-cloud-firestore',
        'google-cloud-texttospeech'
    ],
    entry_points={
        'console_scripts': [
            'sluggers=backend/api.__main__:main',
        ],
    },
    description='An api for creating highlight sequences.',
    author='James Henderson',
    author_email='james@slimestack.com',
)
