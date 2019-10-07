
# Python version to use needs to be provided by our caller
PY_BINARY=$1
echo "*** Zato RHEL/CentOS installation using $PY_BINARY ***"

if ! [ -x "$(command -v lsb_release)" ]; then
  sudo yum install -y redhat-lsb-core
fi
if [[ -n "$(lsb_release -r|grep '\s8.')" ]]; then
    sudo yum -y install \
        bzip2 bzip2-devel curl cyrus-sasl-devel gcc-c++ git haproxy \
        keyutils-libs-devel libev libev-devel libevent-devel libffi libffi-devel \
        libxml2-devel libxslt-devel openldap-devel openssl \
        openssl-devel patch postgresql-devel python-devel suitesparse swig uuid \
        wget
else
    PYTHON_VER="2.7.15"
    PYTHON_URL="https://zato.io/support/python27/python27.tar.bz2"
    PYTHON_PREFIX="/opt/zato/python/$PYTHON_VER"
    PATH="$PYTHON_PREFIX/bin:$PATH"

    sudo yum -y install \
        bzip2 bzip2-devel curl cyrus-sasl-devel gcc-c++ git haproxy \
        keyutils-libs-devel libev libev-devel libevent-devel libffi libffi-devel \
        libxml2-devel libxslt-devel libyaml-devel openldap-devel openssl \
        openssl-devel patch postgresql-devel python-devel suitesparse swig uuid \
        uuid-devel wget

    if ! [ "$(type -p $PY_BINARY)" ]
    then
        # CentOS 6.x requires python2.7 build.
        curl "$PYTHON_URL" | tac | tac | sudo tar -C / -jx
    fi
fi

curl https://bootstrap.pypa.io/get-pip.py | sudo $(type -p $PY_BINARY)
sudo $(type -p $PY_BINARY) -m pip install -U setuptools virtualenv==15.1.0 pip

$PY_BINARY -m virtualenv .
source ./bin/activate
source ./_postinstall.sh $PY_BINARY
