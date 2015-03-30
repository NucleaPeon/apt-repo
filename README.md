apt-repo
--------

Debian Repository Manager

Easily create and manage a locally created debian repository for custom
software.

Hooks into dh-make so it can also aide in the creation of debian packages.
Hooks into gpg for package signing automatically if desired.

This is not an official apt software release. It is a custom add-on. If
the folks at Debian decide to use apt-repo for their work, I will rename
this project.

Getting Started
===============

* Download the debian binary installer
* Tutorial: https://github.com/NucleaPeon/apt-repo/wiki/How-to-Set-up-a-New-Repository-with-Packages


Pre-requisites
==============

Generate your gpg key using
    gpg --gen-key

Select RSA and a minimum of 2048 for encryption.
