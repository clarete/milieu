# -*- coding: utf-8 -*-
# milieu - Environment variables manager
#
# Copyright (c) 2013  Yipit, Inc <coders@yipit.com>
# Copyright (c) 2013-2014  Lincoln Clarete <lincoln@clarete.li>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import commands

# Aliasing to avoid typing and caching the dot resolution
run = commands.getoutput


def test_get():
    # Given that I have a variable inside of a file,
    # When I try to get its value,
    # Then I see the value is right
    (run('python -m milieu -f tests/functional/fixtures/env.cfg get FAVORITE_SUPER_HERO')
     .should.equal('Batman NANANANANA'))


def test_get_uri():
    (run('python -m milieu -d tests/functional/fixtures/env get-uri user SERVER_URI')
     .should.equal('user@mserver.com'))
    (run('python -m milieu -d tests/functional/fixtures/env get-uri password SERVER_URI')
     .should.equal('passwd'))
    (run('python -m milieu -d tests/functional/fixtures/env get-uri host SERVER_URI')
     .should.equal('mserver.com'))
    (run('python -m milieu -d tests/functional/fixtures/env get-uri port SERVER_URI')
     .should.equal('25'))
