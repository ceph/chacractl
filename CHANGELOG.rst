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
