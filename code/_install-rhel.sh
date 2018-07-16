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

if ! [ "$(type -p python2.7)" ]
then
    # CentOS 6.x requires python2.7 build.
    curl "$PYTHON_URL" | tac | tac | sudo tar -C / -jx
fi

curl https://bootstrap.pypa.io/get-pip.py | sudo $(type -p python2.7)
sudo $(type -p python2.7) -m pip install -U setuptools virtualenv==15.1.0

python2.7 -m virtualenv .
source ./bin/activate
source ./_postinstall.sh
