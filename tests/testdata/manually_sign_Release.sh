#!/bin/bash

# shortcut to use the debutils.gpg and debutils.sec.gpg keyring pair only
GPG="`which gpg` --no-default-keyring --keyring ./debutils.gpg --secret-keyring ./debutils.sec.gpg"

# ensure we're in tests/testdata
cd "$(dirname "$0")"

# get the signature of the Debutils key from the keyring pair
KEY_SIG=$( $GPG --list-sigs | awk '/^sig/ {print $3}' )

# generate detached signature Release.gpg
echo "Signing with key ${KEY_SIG}"
$GPG --default-key $KEY_SIG --armor --detach-sign --sign --output Release.gpg Release

# and verify:
echo ""
echo "Verifying signature..."
$GPG -vv --verify ./Release.gpg ./Release