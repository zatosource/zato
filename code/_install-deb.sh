#!/bin/bash

#set -x

CURDIR="${BASH_SOURCE[0]}";RL="readlink";([[ `uname -s`=='Darwin' ]] || RL="$RL -f")
while([ -h "${CURDIR}" ]) do CURDIR=`$RL "${CURDIR}"`; done
N="/dev/null";pushd .>$N;cd `dirname ${CURDIR}`>$N;CURDIR=`pwd`;popd>$N

# Python version to use needs to be provided by our caller
PY_BINARY=$1
INSTALL_PYTHON=${2:-y}
SKIP_OS=${3:-n}
CLEAR_VENV=${4:-n}
echo "*** Zato installation using $PY_BINARY ***"

if [[ "$SKIP_OS" != "y" ]]; then
    # Always run an update so there are no surprises later on when it actually
    # comes to fetching the packages from repositories.
    #sudo apt-get update

    if ! [ -x "$(command -v lsb_release)" ]; then
      sudo apt-get install -y lsb-release
    fi

    if [[ "$INSTALL_PYTHON" == "y" ]]; then
      PYTHON_DEPENDENCIES="$PY_BINARY $PY_BINARY-dev"
    fi

    sudo apt-get install -y \
        build-essential curl git haproxy \
        libffi-dev libkrb5-dev libldap2-dev libpq-dev \
        libsasl2-dev libssl-dev libxml2-dev libxslt1-dev libyaml-dev openssl \
        lsb-release ${PYTHON_DEPENDENCIES}

    # On Debian and Ubuntu the binary goes to /usr/sbin/haproxy so we need to
    # symlink it to a directory that can be easily found on PATH so that starting
    # the load-balancer is possible without tweaking its configuration file.
    if [[ "$(lsb_release -sir)" =~ '^(Debian|Ubuntu)' ]]
    then
        sudo ln -sf /usr/sbin/haproxy /usr/bin/haproxy
    fi
fi

# Use uv from support-linux/bin
UV_BIN="$CURDIR/support-linux/bin/uv"

if [[ "$CLEAR_VENV" == "y" ]]; then
    echo Clearing existing virtual environment in $CURDIR
    rm -rf $CURDIR/bin $CURDIR/lib $CURDIR/lib64 $CURDIR/include $CURDIR/pyvenv.cfg
fi

# Resolve to an absolute path so that uv uses exactly this interpreter
# instead of substituting one of its own managed Python installations.
PY_BINARY_PATH=$(command -v $PY_BINARY)

echo Creating virtual environment in $CURDIR using uv and $PY_BINARY_PATH
$UV_BIN venv "$(realpath $CURDIR)" --python $PY_BINARY_PATH --python-preference only-system --allow-existing -q

# uv writes a .gitignore with "*" into the venv root, which is this source directory,
# and that would hide every new file from git.
rm -f "$CURDIR/.gitignore"

echo Activating virtualenv in $CURDIR
source $CURDIR/bin/activate

echo Setting up environment in $CURDIR
$CURDIR/bin/python $CURDIR/util/zato_environment.py install

echo Adding support-linux to Python path
SITE_PACKAGES=$($CURDIR/bin/python -c "import site; print(site.getsitepackages()[0])")
echo "$CURDIR/support-linux" > "$SITE_PACKAGES/zato_hl7v2.pth"

# Copy the prebuilt HL7v2 Rust extension matching this Python version into the package,
# support-linux/zato_hl7v2/ holds one binary per supported interpreter.
EXT_SUFFIX=$($CURDIR/bin/python -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
HL7V2_SO="$CURDIR/support-linux/zato_hl7v2/zato_hl7v2_rs$EXT_SUFFIX"
if [[ -f "$HL7V2_SO" ]]; then
    echo Copying HL7v2 Rust extension for $EXT_SUFFIX
    cp "$HL7V2_SO" "$CURDIR/zato-common/src/zato/hl7v2_rs/"
else
    echo "Note: no prebuilt HL7v2 Rust extension for $EXT_SUFFIX in $CURDIR/support-linux/zato_hl7v2/"
fi

mkdir -p "$CURDIR/zato-libs"
cp "$CURDIR/zato-libs.pth" "$SITE_PACKAGES/zato-libs.pth"

if ! [ -x "$(command -v cargo)" ] && ! [ -f "$HOME/.cargo/env" ]; then
    echo Installing Rust
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
fi

if [ -f "$HOME/.cargo/env" ]; then
    . "$HOME/.cargo/env"
fi

# lego obtains certificates from Let's Encrypt and Pebble is the local ACME server that its tests run against
Lego_Version=v5.5.1
Pebble_Version=v2.10.1

case "$(uname -m)" in
    x86_64)  ACME_Architecture=amd64 ;;
    aarch64) ACME_Architecture=arm64 ;;
    *)       echo "Unsupported architecture for lego and Pebble: $(uname -m)"; exit 1 ;;
esac

ACME_Download_Dir=$(mktemp -d)

echo Installing lego $Lego_Version
curl -fsSL -o "$ACME_Download_Dir/lego.tar.gz" \
    "https://github.com/go-acme/lego/releases/download/$Lego_Version/lego_${Lego_Version}_linux_$ACME_Architecture.tar.gz"
tar -xzf "$ACME_Download_Dir/lego.tar.gz" -C "$ACME_Download_Dir" lego
install -m 0755 "$ACME_Download_Dir/lego" "$CURDIR/bin/lego"

echo Installing Pebble $Pebble_Version
curl -fsSL -o "$ACME_Download_Dir/pebble.tar.gz" \
    "https://github.com/letsencrypt/pebble/releases/download/$Pebble_Version/pebble-linux-$ACME_Architecture.tar.gz"
tar -xzf "$ACME_Download_Dir/pebble.tar.gz" -C "$ACME_Download_Dir"
install -m 0755 "$ACME_Download_Dir/pebble-linux-$ACME_Architecture/linux/$ACME_Architecture/pebble" "$CURDIR/bin/pebble"

rm -rf "$ACME_Download_Dir"

echo Installing maturin
$UV_BIN pip install maturin

echo Building Rust components
make -C "$CURDIR/.." build

echo ⭐ Successfully installed `zato --version`
