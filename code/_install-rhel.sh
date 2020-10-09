
# Python version to use needs to be provided by our caller
PY_BINARY=python3
echo "*** Zato RHEL/CentOS installation using $PY_BINARY ***"

INSTALL_CMD="yum"

if [ "$(type -p dnf)" ]
then
    INSTALL_CMD="dnf"
    ${INSTALL_CMD} update -y

    if [ ! "$(type -p lsb_release)" ]
    then
        ${INSTALL_CMD} install -y redhat-lsb-core
    fi
fi

sudo ${INSTALL_CMD} install -y \
    bzip2 bzip2-devel curl cyrus-sasl-devel gcc-c++ git haproxy \
    keyutils-libs-devel libev libev-devel libevent-devel libffi libffi-devel \
    libxml2-devel libxslt-devel libyaml-devel openldap-devel openssl \
    openssl-devel patch postgresql-devel python3 python3-devel suitesparse swig uuid \
    uuid-devel wget

if [[ "$(lsb_release -sir)" =~ '^CentOS.8\.' ]]
    ${INSTALL_CMD} install -y python3
    ${INSTALL_CMD} -y groupinstall development
    ${INSTALL_CMD} install -y 'dnf-command(config-manager)'
    ${INSTALL_CMD} config-manager --set-enabled PowerTools

    $PY_BINARY -m venv .
    source ./bin/activate
    source ./_postinstall.sh $PY_BINARY
else
    #  CentOS 7
    curl https://bootstrap.pypa.io/get-pip.py | sudo $(type -p $PY_BINARY)
    sudo $(type -p $PY_BINARY) -m pip install -U setuptools virtualenv==15.1.0 pip

    $PY_BINARY -m virtualenv .
    source ./bin/activate
    source ./_postinstall.sh $PY_BINARY
fi


