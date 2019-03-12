import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="labvirtual",
    version="1.0.0",
    author="Erico Mendonça",
    author_email="erico.mendonca@gmail.com",
    description="QEMU/KVM web console frontend for virtual machines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doccaz/labvirtual",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Topic :: Systems Administration",
        "Topic :: System :: Operating System"
    ],
)
