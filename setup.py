from distutils.core import setup

setup(
    name='unicode-nazi',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    version='1.0',
    url='http://github.com/mitsuhiko/unicode-nazi',
    py_modules=['unicodenazi'],
    description='Annoying helper module that finds unicode/bytestring '
                'comparisions and other problems.',
    long_description=open('README').read(),
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: PHP',
        'Programming Language :: Python'
    ]
)
