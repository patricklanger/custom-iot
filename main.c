/*
 * Aktueller Stand:
 * - coap_saul funktioniert.
 * - cord_ep ist implementiert.
 * - Aufgabe 2.b:
 *     Wie bekommen wir die Adresse des Pi automatisch?
 *     1. Jedem IoT Knoten im lowpan Netz des Pi wird die Routeradresse (ABRO) mitgeteilt. -> Machen wir
 *     2. Neighbour Discovery -> Machen wir nicht
 *     - Implementiert mit gnrc_ipv6_nib_abr_t und mit gnrc_ipv6_nib_abr_print Liste Ausgeben lassen
 *   TODO -> FEHLER: State is unused ....
 *     - Wie speichern wir die IP in einer Variable jetzt? -> Ausprobieren
 * 4. Aufgabe 2.c:
 *     python... client: irgendwas damit?? https://aiocoap.readthedocs.io/en/latest/examples.html
 *     - Dummy client angelegt
 *     Programm soll:
 *     - Tri-axis Accelerometer auslesen, um zu erkennen wie rum das Gerät gehalten wird. Ausprobieren.
 *     - LEDs ansteuern
 *   TODO -> bei GET coap://[2001:67c:254:b0b2:affe:2896:134b:16e6]/saul/8-mma8x5x-SENSE_ACCEL
 *            - *** RIOT kernel panic: Gerät stürzt ab...
 *            - RD bemerkt nicht dass IoT devcie nicht mehr antwortet
 */

// #include <stdio.h>
// #include "msg.h"
// #include "xtimer.h"
//
//
// #include "net/gcoap.h"
// #include "shell.h"
// #include "fmt.h"
//
//
// #include "net/cord/common.h"
// #include "net/cord/ep_standalone.h"
// #include "net/cord/config.h"
// // #include "net/cord/lc.h"
// // #include "net/cord/epsim.h"
// #include "net/cord/ep.h"
//
// #include "net/gnrc/netif.h"
// #include "net/nanocoap.h"
// #include "net/sock/util.h"
// #include "net/gnrc/ipv6/nib/abr.h"
//
// #include "net/ipv6/addr.h"
#include <stdio.h>

#include "gcoap_example.h"
#include "gcoap_saul.h"

#include "shell.h"
#include "gcoap_example.h"
#include "msg.h"
#include "net/gcoap.h"
#include "net/cord/common.h"
#include "net/cord/ep_standalone.h"
#include "fmt.h"
#include "net/gnrc/ipv6/nib/abr.h"
#include "net/cord/config.h"
#include "net/ipv6/addr.h"
#include "net/cord/ep.h"
#include "net/sock/util.h"
#include "net/gnrc/netif.h"
#include "net/nanocoap.h"
#include "xtimer.h"

#define DEVELHELP 1

// Was passiert hier?
static int make_sock_ep(sock_udp_ep_t *ep, const char *addr)
{
    ep->port = 0;
    if (sock_udp_name2ep(ep, addr) < 0) {
        return -1;
    }
    /* if netif not specified in addr */
    if ((ep->netif == SOCK_ADDR_ANY_NETIF) && (gnrc_netif_numof() == 1)) {
        /* assign the single interface found in gnrc_netif_numof() */
        ep->netif = (uint16_t)gnrc_netif_iter(NULL)->pid;
    }
    ep->family  = AF_INET6;
    if (ep->port == 0) {
        ep->port = COAP_PORT;
    }
    return 0;
}

#define MAIN_QUEUE_SIZE (4)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

static const shell_command_t shell_commands[] = {
    { "coap", "CoAP example", gcoap_cli_cmd },
    { NULL, NULL, NULL }
};

// TODO einbauen wird für cord_ep_standalone_reg_cb benötigt
/* we will use a custom event handler for dumping cord_ep events */
static void _on_ep_event(cord_ep_standalone_event_t event)
{
    switch (event) {
        case CORD_EP_REGISTERED:
            puts("RD endpoint event: now registered with a RD");
            break;
        case CORD_EP_DEREGISTERED:
            puts("RD endpoint event: dropped client registration");
            break;
        case CORD_EP_UPDATED:
            puts("RD endpoint event: successfully updated client registration");
            break;
    }
}

static void register_on_rd(char *ip)
{
    // remote endpoint of the target Resource Directory (RD)
    sock_udp_ep_t remote;

    // Im _cord_ep_handler (Shell command) ist
    // argv[0] = cord_ep
    // argv[1] = register
    // argv[2] = ip der Service Discovery (Pi) ist jetzt char *ip
    // argv[3] = interface
    //ip ist gnrc_ipv6_nib_abr_t und muss in char*
    //net/ipv6/adr.h da ist tostring


    if (make_sock_ep(&remote, ip) < 0) {
        printf("error: unable to parse address\n");
        //return 1;
    }
    puts("Registering with RD now, this may take a short while...");
    // NULL weil wir kein registration interface angeben wollen sondern es
    // automatisch bestimmt wird.
    if (cord_ep_register(&remote, NULL) != CORD_EP_OK) {
        puts("error: registration failed");
    }
    else {
        puts("registration successful\n");
        cord_ep_dump_status();
    }
}

static void auto_register(void){
   void *state = NULL;
   gnrc_ipv6_nib_abr_t abr;

   puts("My border routers:");
   while (gnrc_ipv6_nib_abr_iter(&state, &abr)) {
     gnrc_ipv6_nib_abr_print(&abr);
   }
   //register_on_rd(&abr);
   char buffer[IPV6_ADDR_MAX_STR_LEN];
    ipv6_addr_to_str(buffer, (ipv6_addr_t*) &abr.addr, IPV6_ADDR_MAX_STR_LEN);

    char regif[IPV6_ADDR_MAX_STR_LEN + 2];

    sprintf(regif, "[%s]", buffer);

    puts("regif address:");
    puts(regif);

    //char * ip = "[2001:67c:254:b0b2:affe:2000:0:1]";
    register_on_rd(regif);

 }

int main(void)
{
    xtimer_sleep(2);
    /* for the thread running the shell */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);
    server_init();
    puts("gcoap example app");

    gcoap_saul_init();
    puts("gcoap_saul_init app");

    /* register event callback with cord_ep_standalone */
    cord_ep_standalone_reg_cb(_on_ep_event);

    auto_register();


//[2001:67c:254:b0b2:affe:2000:0:1]
    //char* ip = &abr;
    // char* ip = "[2001:67c:254:b0b2:affe:2000:0:1]";
    //register_on_rd(&abr);
    // register_on_rd(ip);

//TODO bei aiocoap-rd anmelden also nicht mehr über shell befehl sondern hierüber
// RIOT-Shellbefehle findet man unter RIOT/sys/shell/commands

    /* start shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should never be reached */
    return 0;
}
