
# Python version to use needs to be provided by our caller
PY_BINARY=$1
echo "*** Zato RHEL/CentOS installation using $PY_BINARY ***"

INSTALL_CMD="yum"

if [ "$(type -p dnf)" ]
then
    INSTALL_CMD="dnf"
    sudo ${INSTALL_CMD} update -y

    if [ ! "$(type -p lsb_release)" ]
    then
        sudo ${INSTALL_CMD} install -y redhat-lsb-core
    fi
fi

if [[ "$(lsb_release -sir)" =~ '^CentOS.8\.' ]]
then
    sudo ${INSTALL_CMD} install -y python3
    sudo ${INSTALL_CMD} -y groupinstall development
    sudo ${INSTALL_CMD} install -y 'dnf-command(config-manager)'
    sudo ${INSTALL_CMD} config-manager --set-enabled PowerTools
fi

sudo ${INSTALL_CMD} install -y \
    bzip2 bzip2-devel curl cyrus-sasl-devel gcc-c++ git haproxy \
    keyutils-libs-devel libev libev-devel libevent-devel libffi libffi-devel \
    libxml2-devel libxslt-devel libyaml-devel openldap-devel openssl \
    openssl-devel patch postgresql-devel python3-devel suitesparse swig uuid \
    uuid-devel wget

if [[ "$(lsb_release -sir)" =~ '^CentOS.8\.' ]]
then
    $PY_BINARY -m venv .
    source ./bin/activate
    source ./_postinstall.sh $PY_BINARY
else
    #  CentOS 7
    curl https://bootstrap.pypa.io/get-pip.py | $(type -p $PY_BINARY)
    $(type -p $PY_BINARY) -m pip --use-feature=2020-resolver install -U setuptools virtualenv==15.1.0 pip

    $PY_BINARY -m virtualenv .
    source ./bin/activate
    source ./_postinstall.sh $PY_BINARY
fi


