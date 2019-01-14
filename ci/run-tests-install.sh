#!/bin/bash -e

cd "$(dirname "$0")"/..
REPO_ROOT="$PWD"

mkdir -p "$HOME/rootcern"
if [[ -x "$HOME/rootcern/root/bin/root.exe" ]]; then
  echo "ROOT is installed, skipping"
else
  echo "ROOT is not installed, installing it"
  pushd "$HOME/rootcern"
    curl https://root.cern.ch/download/root_v6.14.06.Linux-ubuntu14-x86_64-gcc4.8.tar.gz | tar xzf -
  popd
fi

source "$HOME/rootcern/root/bin/thisroot.sh"
export PYTHONUSERBASE="$HOME/pythonlocal"

pushd "$REPO_ROOT"
  pip install -e . --user
  pip install nose --user
popd
