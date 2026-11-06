#!/usr/bin/env bash
# Reset PAM faillock counters on unlock or session wake
faillock --user simple --reset 2>/dev/null || true
faillock --user david --reset 2>/dev/null || true
