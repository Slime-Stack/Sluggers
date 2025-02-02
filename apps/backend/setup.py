from setuptools import setup, find_packages

setup(
    name='sluggers',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'flask',
        'requests',
        'python-dotenv',
        'pandas',
        'gunicorn',
        'pytz',
        'functions-framework',
        'setuptools',
        'google',
        'google-cloud',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'google-generativeai',
        'google-cloud-firestore',
        'google-cloud-texttospeech',
        'google-cloud-aiplatform',
        'google-cloud-pubsub',
        'google-cloud-secretmanager'
    ],
    entry_points={
        'console_scripts': [
            'sluggers=api.__main__:main',
        ],
    },
    description='An api for creating highlight sequences.',
    author='James Henderson',
    author_email='james@slimestack.com',
)
