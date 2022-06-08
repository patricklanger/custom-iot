//Mit diesem Code example registrieren wir die IoT Knoten im Resource Directory (RD) auf dem Raspberry Pi
#include <stdio.h>

#include "fmt.h"
#include "shell.h"
#include "net/ipv6/addr.h"
#include "net/gcoap.h"
#include "net/cord/common.h"
#include "net/cord/ep_standalone.h"


#define MAIN_QUEUE_SIZE     (8)
static msg_t _main_msg_queue[MAIN_QUEUE_SIZE];

#define NODE_INFO  "SOME NODE INFORMATION"

//Callback Nachrichten werden hier erzeugt
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

/* define some dummy CoAP resources */
static ssize_t _handler_dummy(coap_pkt_t *pdu,uint8_t *buf, size_t len, void *ctx) {
    /* kontext ctx wird uerbergeben, aus dem holen wir uns das Device */
    (void)ctx;

    /* get random data */
    int16_t val = 23;

    //Wie server.c Zeile 156
    //Init: Initalisiert Anwort zum zurueckschicken
    //finish: Bereitet Payload vor, speichert das in resp_len
    //fmt_s16_dec = konvertiert Zahl in String, also Zeichenkette
    //Zeichenkette geht in payload und wird zurueckgegeben
    gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
    size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);
    resp_len += fmt_s16_dec((char *)pdu->payload, val);
    return resp_len;
}

static ssize_t _handler_info(coap_pkt_t *pdu, uint8_t *buf, size_t len, void *ctx) {
    /* kontext ctx wird uerbergeben, aus dem holen wir uns das Device */
    (void)ctx;

    //Genau wir bei dummy Handler
    //Wir geben die NODE_INFO zurueck (String)
    gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
    size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);
    size_t slen = sizeof(NODE_INFO);
    memcpy(pdu->payload, NODE_INFO, slen);
    return resp_len + slen;
}

//Resourcen, die wir haben wollen als Array mit Resourcen
//GET Resourcen, die wir bekommen wird verarbeitet hier im Programm (Bis jetzt nur handler dummy mit 23)
static const coap_resource_t _resources[] = {
    //Info, hum = Luftfeuchtigkeit, temp = Temperatur
    { "/node/info",  COAP_GET, _handler_info, NULL },
    { "/sense/hum",  COAP_GET, _handler_dummy, NULL },
    { "/sense/temp", COAP_GET, _handler_dummy, NULL }
};

static gcoap_listener_t _listener = {
    //Startpunkt fuer die Ressourcen
    .resources     = (coap_resource_t *)&_resources[0],
    //Arraygroesse mit Ressourcen
    .resources_len = ARRAY_SIZE(_resources),
    //
    .next          = NULL
};

int main(void)
{
    // wir brauchen eine Queue für den Thread, der die Shell ausführt, um
    //potenziell schnell eingehende Netzwerkpakete zu empfangen
    msg_init_queue(_main_msg_queue, MAIN_QUEUE_SIZE);

    //Loggt in die konsole
    puts("CoRE RD client example!\n");

    /* setup CoAP resources */
    gcoap_register_listener(&_listener);

    //Registrieren Sie einen Callback, um über Änderungen des RD-Endpunktstatus benachrichtigt zu werden.
    //Zu jedem Zeitpunkt kann nur ein einziger Callback aktiv sein,
    //so dass das Setzen eines neuen Callbacks den bestehenden überschreibt.
    cord_ep_standalone_reg_cb(_on_ep_event);

    //Loggt in die konsole
    puts("Client information:");
    //cord_common_get_ep = Ermittelt die lokale Endpunktkennung / Vielleicht EP Test Name
    //(int)CONFIG_CORD_LT = Lebensdauer aus Makefile
    printf("  ep: %s\n", cord_common_get_ep());
    printf("  lt: %is\n", (int)CONFIG_CORD_LT);

    //Groesse fur Puffer, der zum Lesen einer Zeile verwendet wird
    char line_buf[SHELL_DEFAULT_BUFSIZE];
    //Rueckportierender Alias (Null (Array Befehlsstruktur, Puffer zum lesen einer Z., Groesse Puffer))
    shell_run(NULL, line_buf, SHELL_DEFAULT_BUFSIZE);

    return 0;
}
