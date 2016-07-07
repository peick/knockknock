import os
import re
import thread
import time

import pytest
from knockknock.log_file import LogFile


def append(path):
    for i in range(10):
        with open(path, 'a') as f:
            f.write('%d\n' % i)
            f.flush()
        time.sleep(0.5)
    f.close()


def rotate(path):
    for i in range(10):
        newfile = path + '.%d'
        with open(newfile, 'w') as f:
            f.write('initial value')

        os.rename(newfile, path)
        time.sleep(0.5)


def test_log_file_missing(tmpdir):
    log = LogFile(tmpdir.join('missing.log').strpath)
    gen = log.tail()

    with pytest.raises(IOError):
        next(gen)


@pytest.mark.timeout(30)
def test_read(tmpdir):
    f = tmpdir.join('read.log')
    f.write('initial value')

    log = LogFile(f.strpath)
    gen = log.tail()

    thread.start_new_thread(append, (f.strpath, ))

    line = next(gen)
    assert re.match(r'\d+\n', line)


@pytest.mark.timeout(30)
def test_file_rotating(tmpdir):
    f = tmpdir.join('rotate.log')
    f.write('initial value')

    log = LogFile(f.strpath)
    gen = log.tail()

    thread.start_new_thread(rotate, (f.strpath, ))

    line = next(gen)
    assert re.match(r'initial value$', line)
