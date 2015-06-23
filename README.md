apt-repo
--------

Debian Repository Manager

Easily create and manage a locally created debian repository for custom
software.

Relies on dpkg-deb and dpkg-scanpackages and so is currently limited to
debian-based Operating Systems until this software is made multiplatform.

This is not an official apt software release. It is a custom add-on. If
the folks at Debian decide to use apt-repo for their work, I will rename
this project.


News
====

* End of 0.10.x series announced, possible 0.10.6 release with more apt-pkg support
  Once 0.10.6 is released, migration support will be removed for simplicity and speed.
  If you use 0.9.x series, please update with 0.10.x and then move to 0.11.x.
  Once Milestone 1 is reached, we move into 1.x.x territory and officially move 
  towards stable.

* Version 0.10.0 is broken, use 0.10.1. Also: ipk packages are being supported.

* Version 0.9.8 is the last of the stable gdbm/shelve database packages.
  Version 0.10.x will now use the easier-to-manage configparser database
  which can be edited by hand and viewable in a text editor.

  The big issue with this so far is that there is a built-in migration
  tool that automatically runs in the 0.10.0 version every time an action
  is performed. 0.10.x series will have this until 0.11.x is released, in
  which case use of gdbm databases will be fully deprecated and unsupported.

  Sections are set in stone and keys in the configparser db are case-sensitive.
  This may cause some issues on Windows machines, which are not currently
  supported.

* Version 0.9.4 now includes the ability to add and remove `DEBIAN/` scripts
  like postinst and prerm using similar functionality as adding files.

  `apt-pkg [package name] control [file type: postinst or postrm or preinst, etc.] [path/to/script] (options if any)`

   `apt-pkg [package name] info` should show control as an attribute if your version supports it. Older packages
   will automatically include an empty control file attribute when upgrading. Even if the control attribute is
   empty, by default the control file at a minimum will be written to a package.

   You can override the default control file by specifying your own, via this command:

   `apt-pkg [package name] control control mycontrolfile.txt`

   Yes, you can specify a file of any extension and name and it gets written AS `control` or `postrm` or whatever file you specify.


Gotchas
=======

* Currently specifying multiple architectures for a package may break the build.

 
Getting Started
===============

* Download the debian binary installer package in the Releases tab.
* Tutorial: https://github.com/NucleaPeon/apt-repo/wiki/How-to-Set-up-a-New-Repository-with-Packages


Pre-requisites
==============

**Not implemented**

**Not required yet**

Generate your gpg key for your repositories using
    gpg --gen-key

Select RSA and a minimum of 2048 for encryption.

