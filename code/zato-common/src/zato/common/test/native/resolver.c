/*
 * A preloaded library that resolves the host names under one domain through the DNS server of a test session,
 * the way the endpoint name of a managed database service is resolved through the DNS of its provider. Every call
 * to getaddrinfo for such a name sends a new query, so a changed answer takes effect for the next connection.
 * All other names are resolved by the C library as usual.
 *
 * Zato_Test_DNS_Server names the server as address:port and Zato_Test_DNS_Domain names the domain, with its leading dot.
 * Both are read on each call, so a test process sets them after it starts.
 */

#define _GNU_SOURCE
#include <arpa/inet.h>
#include <arpa/nameser.h>
#include <dlfcn.h>
#include <netdb.h>
#include <netinet/in.h>
#include <resolv.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>

#define ENV_SERVER "Zato_Test_DNS_Server"
#define ENV_DOMAIN "Zato_Test_DNS_Domain"
#define ANSWER_SIZE 512
#define QUERY_TIMEOUT_SECONDS 2
#define QUERY_ATTEMPTS 3
#define DECIMAL_BASE 10
#define IPV4_ADDRESS_SIZE 4

typedef int (*getaddrinfo_function)(const char *, const char *, const struct addrinfo *, struct addrinfo **);

/* Whether a name ends with the domain, compared without regard to case. */
static int is_in_domain(const char *name, const char *domain) {
    size_t name_length = strlen(name);
    size_t domain_length = strlen(domain);

    if (name_length <= domain_length) {
        return 0;
    }

    const char *name_suffix = name + name_length - domain_length;
    int out = strcasecmp(name_suffix, domain) == 0;

    return out;
}

/* Fills in the address of the DNS server from its address:port form. */
static int parse_server(const char *server, struct sockaddr_in *address) {
    const char *colon = strrchr(server, ':');

    if (colon == NULL) {
        return -1;
    }

    char host[INET_ADDRSTRLEN];
    size_t host_length = (size_t) (colon - server);

    if (host_length >= sizeof(host)) {
        return -1;
    }

    memcpy(host, server, host_length);
    host[host_length] = '\0';

    long port = strtol(colon + 1, NULL, DECIMAL_BASE);

    memset(address, 0, sizeof(*address));
    address->sin_family = AF_INET;
    address->sin_port = htons((unsigned short) port);

    if (inet_pton(AF_INET, host, &address->sin_addr) != 1) {
        return -1;
    }

    return 0;
}

/* Queries the DNS server for the IPv4 address of a name and returns an EAI_* code, or 0 with the address filled in. */
static int query_address(const char *name, const char *server, char *address, size_t address_size) {
    struct sockaddr_in server_address;

    if (parse_server(server, &server_address) != 0) {
        return EAI_SYSTEM;
    }

    /* A state of its own, which uses the DNS server of the test session as its only server and no search domains */
    struct __res_state state;
    memset(&state, 0, sizeof(state));

    if (res_ninit(&state) != 0) {
        return EAI_SYSTEM;
    }

    state.nscount = 1;
    state.nsaddr_list[0] = server_address;
    state.retrans = QUERY_TIMEOUT_SECONDS;
    state.retry = QUERY_ATTEMPTS;
    state.options &= ~((unsigned long) (RES_DNSRCH | RES_DEFNAMES));

    unsigned char answer[ANSWER_SIZE];
    int length = res_nquery(&state, name, ns_c_in, ns_t_a, answer, sizeof(answer));
    int lookup_error = state.res_h_errno;

    res_nclose(&state);

    /* A name the server does not know is reported as such, and a server that does not answer as a temporary failure */
    if (length < 0) {
        if (lookup_error == HOST_NOT_FOUND) {
            return EAI_NONAME;
        }
        return EAI_AGAIN;
    }

    ns_msg message;

    if (ns_initparse(answer, length, &message) != 0) {
        return EAI_FAIL;
    }

    int count = ns_msg_count(message, ns_s_an);

    for (int index = 0; index < count; index++) {
        ns_rr record;

        if (ns_parserr(&message, ns_s_an, index, &record) != 0) {
            return EAI_FAIL;
        }

        if (ns_rr_type(record) != ns_t_a) {
            continue;
        }

        if (ns_rr_rdlen(record) != IPV4_ADDRESS_SIZE) {
            continue;
        }

        if (inet_ntop(AF_INET, ns_rr_rdata(record), address, (socklen_t) address_size) == NULL) {
            return EAI_FAIL;
        }

        return 0;
    }

    return EAI_NODATA;
}

int getaddrinfo(const char *node, const char *service, const struct addrinfo *hints, struct addrinfo **res) {
    getaddrinfo_function real_getaddrinfo = (getaddrinfo_function) dlsym(RTLD_NEXT, "getaddrinfo");

    const char *server = getenv(ENV_SERVER);
    const char *domain = getenv(ENV_DOMAIN);

    /* Names outside of the domain, and all names while no server is configured, are resolved as usual */
    if (node == NULL || server == NULL || domain == NULL) {
        return real_getaddrinfo(node, service, hints, res);
    }

    if (!is_in_domain(node, domain)) {
        return real_getaddrinfo(node, service, hints, res);
    }

    char address[INET_ADDRSTRLEN];
    int result = query_address(node, server, address, sizeof(address));

    if (result != 0) {
        return result;
    }

    /* The address found is turned into the result by the C library itself, with the same service and hints */
    struct addrinfo numeric_hints;

    if (hints == NULL) {
        memset(&numeric_hints, 0, sizeof(numeric_hints));
    } else {
        numeric_hints = *hints;
    }

    numeric_hints.ai_flags |= AI_NUMERICHOST;
    numeric_hints.ai_family = AF_INET;

    int out = real_getaddrinfo(address, service, &numeric_hints, res);
    return out;
}
