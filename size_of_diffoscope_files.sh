#!/bin/bash

du -sh results --exclude="buildcache" --exclude="*.buildinfo" --exclude="*.buildcompare" --exclude="*.buildspec"
