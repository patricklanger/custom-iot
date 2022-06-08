/*
 * Aktueller Stand:
 * 1. coap_saul funktioniert
 * 2. cord_ep muss implementiert werden
 */

#include <stdio.h>
#include "msg.h"

#include "net/gcoap.h"
#include "shell.h"

#include "gcoap_example.h"
#include "gcoap_saul.h"

#define MAIN_QUEUE_SIZE (4)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

static const shell_command_t shell_commands[] = {
    { "coap", "CoAP example", gcoap_cli_cmd },
    { NULL, NULL, NULL }
};

// TODO einbauen wird für cord_ep_standalone_reg_cb benötigt
// /* we will use a custom event handler for dumping cord_ep events */
// static void _on_ep_event(cord_ep_standalone_event_t event)
// {
//     switch (event) {
//         case CORD_EP_REGISTERED:
//             puts("RD endpoint event: now registered with a RD");
//             break;
//         case CORD_EP_DEREGISTERED:
//             puts("RD endpoint event: dropped client registration");
//             break;
//         case CORD_EP_UPDATED:
//             puts("RD endpoint event: successfully updated client registration");
//             break;
//     }
// }

int main(void)
{
    /* for the thread running the shell */
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);
    server_init();
    puts("gcoap example app");

    gcoap_saul_init();
    puts("gcoap_saul_init app");

//TODO cord_ep ausführen
    // /* register event callback with cord_ep_standalone */
    // cord_ep_standalone_reg_cb(_on_ep_event);

//TODO bei aiocoap-rd anmelden also nicht mehr über shell befehl sondern hierüber
// RIOT-Shellbefehle findet man unter RIOT/sys/shell/commands

    /* start shell */
    puts("All up, running the shell now");
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    shell_run(shell_commands, line_buf, SHELL_DEFAULT_BUFSIZE);

    /* should never be reached */
    return 0;
}
