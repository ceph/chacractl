0.0.21
------
Release Date: May 12, 2020

* Add Python3 compatibility

0.0.20
------
Release Date: January 30th, 2019

* Pinning ``requests-toolbelt`` to 0.9.1.  Prevents requiring ``pyopenssl``

0.0.19
------
Release Date: January 29th, 2019

* Add ``pyopenssl`` as a requirement since ``requests_toolbelt`` doesn't seem
  to require it anymore

0.0.18
------
Release Date: January 23th, 2019

* Release 0.0.17 did not contain the multipart upload support

0.0.17
------
**BOTCHED RELEASE**
Release Date: January 23th, 2019

* Use multipart uploads to prevent the 2GB issue that was supposedly fixed
  by 0.0.16

0.0.16
------
Release Date: August 20th, 2018

* Fix an issue for POSTing files larger than 2GB

0.0.15
------
Release Date: April 3rd, 2017

* Fix an issue where an HTTP response might be ``None``

0.0.14
------
Release Date: March 22nd, 2017

* Retry failed HTTP operations, improving robustness of the many requests
  the tool has to perform when dealing with large amounts of packages.


0.0.13
------
Release Date: December 9th, 2016

* Fix an issue with filenames vs. paths if a digest doesn't match


0.0.12
------
Release Date: September 28th, 2016

* Improve logging around checksum mismatches


0.0.12
------
Release Date: September 28th, 2016

* Improve logging around checksum mismatches


0.0.11
------
Release Date: September 27th, 2016

* Fix updating with checksum verification, where the URL would be wrong for PUT
  requests


0.0.10
------
Release Date: September 20th, 2016

* Fix ``TypeError`` when uploading. Missing ``self`` on method's signature


0.0.9
-----
Release Date: September 20th, 2016

* Add option to verify binaries were correctly uploaded via checksums.
* When uploading, fix a bug where a non-200 response would trigger an
  UnboundLocal error


0.0.8
-----
Release Date: June 13th, 2016

* Adds ``ssl_verify`` option for configuraton, to prevent issues on local
  chacra instances where self signed ssl certs are used
* Reset the chacractl config for tests that needs them
* add travis.yml configuration
* binaries: fix issue when deleting, treating 204 as an error
* binaries: silence warnings when deleting


0.0.7
-----
Release Date: December 21st, 2015

* Fix unicode issues when uploading binaries as text.
* Implement support for project creation


0.0.6
-----
Release Date: December 2nd, 2015

* Minor fix for DELETE operations, actually making them work

0.0.5
-----
Release Date: November 9rd, 2015

* Use the filename when doing a PUT to re-upload a binary

0.0.4
-----
Release Date: November 3rd, 2015

* Fix an issue when raising errors when posting to a 404 url

0.0.3
-----
Release Date: November 3rd, 2015

* Add a ``--force`` flag to be able to re-upload binaries

0.0.2
-----
Release Date: October 27th, 2015

* Implement the 'exists' subcommand to check existance of URL endpoints

0.0.1
-----
Release Date: October 20th, 2015

* Initial release.
