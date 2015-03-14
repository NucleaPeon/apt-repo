Library Readme
--------------

This folder contains python modules that represent debian programs that have
been converted into multiplatform versions.

For example: the programs `dpkg-scanpackages` and `dpkg-deb --build [folder]`
will eventually be converted into python modules.

In the interim, the modules should perform the actual process (Popen) of the
debian version until such time as they can be converted so the code won't
change during the transition.
