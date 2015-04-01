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

News
====

* Version 0.9.4 now includes the ability to add and remove `DEBIAN/` scripts
  like postinst and prerm using similar functionality as adding files.

  `apt-pkg [package name] control [file type: postinst or postrm or preinst, etc.] [path/to/script] (options if any)`
  
   `apt-pkg [package name] info` should show control as an attribute if your version supports it. Older packages
   will automatically include an empty control file attribute when upgrading. Even if the control attribute is
   empty, by default the control file at a minimum will be written to a package.

   You can override the default control file by specifying your own, via this command:

   `apt-pkg [package name] control control mycontrolfile.txt`

   Yes, you can specify a file of any extension and name and it gets written AS `control` or `postrm` or whatever file you specify.

Getting Started
===============

* Download the debian binary installer
* Tutorial: https://github.com/NucleaPeon/apt-repo/wiki/How-to-Set-up-a-New-Repository-with-Packages


Pre-requisites
==============

Generate your gpg key for your repositories using
    gpg --gen-key

Select RSA and a minimum of 2048 for encryption.


TODO
====

* Store relative or absolute paths in the database to package files to make it portable. Right now, the path the user enters is what is the key. If they enter an absolute and relative path for the same files, the latter add command is what overrides the former. Instead, --relpath or --abspath will transform all added and removed file paths into a relative or absolute path respectively so no collisions occur. Use relpath for portable package databases and abspath for packages that may move from folder to folder yet require same files.
