#!/bin/bash

# shortcut to use the debutils.gpg and debutils.sec.gpg keyring pair only
GPG="`which gpg` --no-default-keyring --keyring ./debutils.gpg --secret-keyring ./debutils.sec.gpg"

if [ ! -e "debutils.key" ]; then
    echo "No ASCII armored keyfile to import!"
    exit -1
fi

$GPG --import ./debutils.key
$GPG --allow-secret-key-import --import ./debutils.key
