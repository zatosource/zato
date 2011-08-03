
Technical overview
==================

Zato clusters
-------------


Each Zato environment is comprised of one or more Zato clusters that allow for
the messages passing through to be handled in a secure and reliable way.

.. image:: zato-general-arch.png
   :align: center

A cluster has :ref:`a high-availability load balancer <ha-lb>` in front of the message processing servers.
External applications connect to the load balancer which distributes the load across one or more
servers according to the configured algorithm, with the round-robin being the default
one. The load balancer is smart enough to notice, in case of a failure, a server
to go down and stops forwarding messages to it. Conversly, when a server goes up,
the load balancer automatically recognizes it and starts dispatching requests
to it. There is no limit to the number of servers in a cluster and administrators
may take servers offline and online without disrupting message processing, no restarts
are ever required. Zato's HA load balancer is implemented on top of
`HAProxy <http://haproxy.1wt.eu/>`_. :ref:`(read more) <ha-lb>`

A :ref:`ZatoServer <zato-server>` is the entity which does the job of exposing
services to external applications and does the processing of incoming requests.
Servers are also capable of invoking other external applications through various
supported protocols and formats. Each server has also a highly-customizable built-in
scheduler which can be configured to fire background jobs. Servers are implemented
using a mix of `Circuits <http://bitbucket.org/prologic/circuits/wiki/Home>`_
and `lighttpd <http://www.lighttpd.net/>`_. :ref:`(read more) <zato-server>`

ZatoAdmin is a slick AJAX web-based administration console used for the management of clusters.
Each cluster has exactly one ZatoAdmin console although a single console may be reused
for managing multiple clusters. ZatoAdmin is implemented in
`Django <http://www.djangoproject.com/>`_ and `Circuits <http://bitbucket.org/prologic/circuits/wiki/Home>`_
with a balanced mix of `YUI <http://developer.yahoo.com/yui/2/>`_ and
`PrototypeJS <http://prototypejs.org/>`_ for frontend features. :ref:`(read more) <zato-admin>`

:ref:`ODB (Operational database) <odb>` is an SQL database used for storing
configuration common to all members of the cluster and is a place where
**TODO: LINK dictionaries** and **TODO: LINK run-time data** are stored. ODB
is also used for storing information required by Zato's asynchronous guaranteed
delivery mechanisms. ODB may installed on
`Oracle <http://www.oracle.com/technology/software/products/database/index.html>`_,
`PostgreSQL <http://www.postgresql.org/>`_ or
`MySQL <http://www.mysql.com/downloads/>`_ infrastructure.
:ref:`(read more) <odb>`

Zato uses `RabbitMQ <http://www.rabbitmq.com>`_ AMQP middleware for exchanging data
between servers participating in a cluster, servers never talk directly to each
other, messages are internally placed on and picked off RabbitMQ queues if there's a need
for synchronizing information between servers :ref:`(read more) <rabbit-mq>`

All Zato's components automatically use encrypted SSL/TLS channels with certificates for internal
communication wherever it's applicable and possible with no need for manual configuration
if not wanted. Everything works with sane and safe defaults out of the box.

.. _ha-lb:

High-availability load balancer
-------------------------------

foo bar

.. _zato-server:

ZatoServer
----------

.. image:: zato-server.png
   :align: center

A ZatoServer is a central processing place on which user-written services exist
and through which all incoming requests must eventually pass. Each server exposes
a number of world-facing interfaces for invoking services, such as SOAP, AMQP, JMS, FTP,
REST or plain HTTP and each server is responsible for securing the access to services
according to the configuration managed by :ref:`ZatoAdmin <zato-admin>`. All servers
are also capable of securely accessing external applications via AMQP, FTP, JMS, REST,
SOAP, SQL or plain HTTP again. In addition to that, every server has a built-in
mechanism for firing jobs configured for executing to a given schedule; one-time
jobs are handy for quick one-off occassions, interval-based jobs allow for a powerful
management of complex firing intervals, including skipping the events according to a holidays
calendar, and cron-style jobs use the syntax of a well known UNIX Cron scheduler.

Services running on servers may be either hot-deployed into a filesystem's pickup
directory or uploaded through the ZatoAdmin console. Either way, no restarts are required
for updating the running code and the message processing needs ever be disrupted.

Configuration specific to the given server, such an HTTP port to listen to,
is stored in a local `Bazaar <http://bazaar.canonical.com/en/>`_
repository which allows for a full audit log of changes to be taken and also lets
administrators manually make tweaks and adjustments with an ability to fully
rollback the changes.

From the operating system point of view ZatoServer is composed of two groups
of applications - parallel and singleton servers are built on top Circuits and
lighttpd sits in front of Circuits in order to secure access to services.

Each ParallelServer is a distinct operating system's process started from the main process
and each of them listens on the same socket, typicaly there are at least as
many ParallelServers as there are physical CPUs. Their name stems from the fact
that they're all running in parallel and each of them carries the same set of
services which process incoming messages. Such an approach means that Zato is able
to very easily take advantage of multi-core
hardware. During a server's startup, one of the ParallelServers spawns a SingletonServer's
thread which is responsible for carrying out tasks which can't be made parallel,
such as processing of hot-deployment events, flushing the configuration on disk
or invoking the scheduled background jobs.

Another group is lighttpd and its associated configuration agent. ParallelServers
never deal with HTTPS directly, that's the task of lighttpd which runs on the same
host in front of them, authenticates the requests and proxies them over to ParallelServers
using unencrypted HTTP. The SSL/TLS context is attached to the request so that ParallelServers,
if configured to, are able to perform the authorization based on a client's SSL/TLS
certificate. the Each lighttpd instance has assigned a configuration agent's
process which accepts requests from ZatoAdmin and soft-reloads lighttpd on demand,
again, the processing flow is never interrupted.

`Read more about creating and using Zato services <http://example.com>`_

`Read more about configuring ZatoServers <http://example.com>`_

.. _zato-admin:

ZatoAdmin
----------

foo bar

.. _odb:

ODB
-------------

foo bar

.. _rabbit-mq:

RabbitMQ
--------------

foo bar