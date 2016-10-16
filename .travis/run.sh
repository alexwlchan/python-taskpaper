#!/bin/bash

set -e
set -x

py.test test/

coverage run -m py.test test/
coverage report
