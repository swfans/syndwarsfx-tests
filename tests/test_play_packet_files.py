# -*- coding: utf-8 -*-

""" Test for Syndicate Wars Port.

    This test runs packet files on missions, starting the game for each packet
    file.
    Run it using `pytest` in project root folder.
"""

# Copyright (C) 2023 Mefistotelis <mefistotelis@gmail.com>
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

import glob
import itertools
import logging
import os
import re
import sys
import pathlib
import pytest
import subprocess


LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize("pckt_inp_fn", [fn for fn in itertools.chain.from_iterable([ glob.glob(e, recursive=True) for e in (
    './qdata/savegame/rc*m*.s01',
  ) ]) if os.path.isfile(fn)] )
def test_play_empty_packet_files(pckt_inp_fn):
    """ Test of missions startup. Loads short packet file for each mission, the file soon executes quit packet.
    """
    LOGGER.info("Testcase file: {:s}".format(pckt_inp_fn))

    pckt_path, pckt_filename = os.path.split(pckt_inp_fn)
    pckt_path = pathlib.Path(pckt_path)
    pckt_basename, pckt_fileext = os.path.splitext(pckt_filename)
    log_fn = "{:s}.log".format(pckt_basename)
    logs_out_path = "test_out"
    match = re.search('^rc[0]*([0-9]+)m[0]*([0-9]+).s[0]*([0-9]+)$', pckt_filename)
    assert match, "Test bug: Cannot parse packet file name \"{}\"".format(pckt_filename)
    campgn = match.group(1)
    missi = match.group(2)
    pcktno = match.group(3)
    logs_out_fn = os.sep.join([logs_out_path, log_fn])
    if not os.path.exists(logs_out_path):
        os.makedirs(logs_out_path)
    # Run the game
    command = [os.path.join(".", "syndwarsfx"), "-W", "-q", "-m", "{},{}".format(campgn,missi), "-p", "{}".format(pcktno)]
    if False: # Debug
        command = ["c:/msys64/mingw32/bin/gdb", "-q", "-ex", "set env DEBUG_BF_AUDIO 1", "-ex", "set pagination off", "-ex", "set logging overwrite on", "-ex", "set logging on", "-ex", "run", "-ex", "exit", "--args"] + command
        gdblog_out_fn = os.sep.join([logs_out_path, "{:s}-gdb.log".format(pckt_basename)])
    LOGGER.info(' '.join(command))
    proc = subprocess.run(command, capture_output=True, text=True)
    LOGGER.info(proc.stdout)
    os.replace("error.log", logs_out_fn)
    if False: # Debug
        os.replace("gdb.txt", gdblog_out_fn)
    assert proc.returncode == 0, "Game precess exited with code {}".format(proc.returncode)
    log = open(logs_out_fn, "r").read()
    assert "LbDataFree" in log, "Log file does not contain cleanup, execution did not ended normally"
