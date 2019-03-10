
# Python version to use needs to be provided by our caller
PY_BINARY=$1
echo "*** Zato RHEL/CentOS installation using $PY_BINARY ***"

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

curl https://bootstrap.pypa.io/get-pip.py | sudo $(type -p $PY_BINARY)

# Python3 customizations
if [[ $PY_BINARY != python2* ]];then
  PY_V=3
  sudo yum install -y centos-release-scl-rh
  sudo yum-config-manager --enable centos-sclo-rh-testing

  # On RHEL, enable RHSCL and RHSCL-beta repositories for you system:
  sudo yum-config-manager --enable rhel-server-rhscl-7-rpms
  sudo yum-config-manager --enable rhel-server-rhscl-beta-7-rpms

  # 2. Install the collection:
  sudo yum install -y rh-python36

  # 3. Start using software collections:
  scl enable rh-python36 bash
fi
if [[ "$EUID" -ne 0 ]];then
  sudo pip${PY_V} install -U setuptools virtualenv==15.1.0
else
  pip${PY_V} install -U setuptools virtualenv==15.1.0
fi

$PY_BINARY -m virtualenv .
source ./bin/activate
source ./_postinstall.sh $PY_BINARY
