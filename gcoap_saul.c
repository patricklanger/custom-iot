

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "net/gcoap.h"
#include "net/nanocoap.h"
#include "saul.h"
#include "saul_reg.h"

#include "gcoap_saul.h"

static coap_resource_t _resources[GCOAP_RES_MAX];

static char _paths[GCOAP_RES_MAX][GCOAP_PATH_LEN];

//Initialisiert werden Ressourcen = leer erstmal
//Ressourcen und Listener werden in gcoap listener befuellt
static gcoap_listener_t _listener = {
    _resources,
    0,
    GCOAP_SOCKET_TYPE_UNDEF,
    gcoap_encode_link,
    NULL,
    NULL
};

//PDU = Protokolldateneinheit die zwischen Peer hin und her geschickt wird
// beinhaltet Metadaten wie GET, PUT, ...

static ssize_t saul_handler(coap_pkt_t* pdu, uint8_t *buf, size_t len, void *ctx) {
    /* kontext ctx wird uerbergeben, aus dem holen wir uns das Saul Device */
    saul_reg_t* saul_dev = (saul_reg_t*) ctx;

    phydat_t data = {0};
    int dim = 0;
    //Es wird geguckt, ob Get oder Put benutzt wird
    coap_method_flags_t method_flag = coap_method2flag(coap_get_code_detail(pdu));

    switch(method_flag) {
        case COAP_GET:
            /* Lese Saul Device und wenn < 0 dann schicke ERROR*/
            //Ergebnis wird in Data gespeichert, wenn dim = -1 dann ERROR zurueck
            dim = saul_reg_read(saul_dev, &data);
            if(dim < 0) {
                return gcoap_response(pdu, buf, len, COAP_CODE_INTERNAL_SERVER_ERROR);
            }

            //Wie server.c Zeile 156
            //Aufruf um Antowrt zu initialisieren
            //ADD_Format, um Optionen (Nutzdaten) hinzuzufuegen
            //finish, um PDU Metadaten zu vervollstaendigen
            //Zurueckgegebene Metadaten laenge in resp_len speichern
            gcoap_resp_init(pdu, buf, len, COAP_CODE_CONTENT);
            coap_opt_add_format(pdu, COAP_FORMAT_TEXT);
            size_t resp_len = coap_opt_finish(pdu, COAP_OPT_FINISH_PAYLOAD);

            /* write value to payload (json format) */
            //Speichern ergebnis in resp_len / wir wandeln fuer export in json um
            char valueBuf[20];
            phydat_to_json(&data, dim, valueBuf);

            snprintf((char*)pdu->payload, len, "{\"value\": %s}", valueBuf);
            printf("%s\n", (char*)pdu->payload);

            return resp_len;

        case COAP_PUT:
            /* limit payload length, darf nicht groesser 8 hin */
            if (pdu->payload_len > 8) {
                return gcoap_response(pdu, buf, len, COAP_CODE_BAD_REQUEST);
            }

            /* deswegen nicht groesser 8, weil auf 9 etwas abgelegt wird */
            //convert the payload to an integer and update the internal value */
            char payload[9] = {0};
            //Wo wird gespeichert ? payload / Was wird gespeichert ? / Welche groesse
            memcpy(payload, (char*)pdu->payload, pdu->payload_len);

            /* convert payload to int32 */
            char *endptr;
            //endptr = Verweis auf naechtes zeichen in payload, wenn es das nicht gibt
            //also == payload, dann shcicke bad request
            //10 gueltige zeichen
            int32_t val = (int32_t) strtoul(payload, &endptr, 10);
            if(endptr == payload) {
                return gcoap_response(pdu, buf, len, COAP_CODE_BAD_REQUEST);
            }

            /* /fit = Skalierung/ convert int32 to phydat_t */
            phydat_fit(&data, &val, 1);

            /* write value to saul device , kontrollieren ob es funtkioniert oder nicht */
            if(saul_reg_write(saul_dev, &data) < 0) {
                return gcoap_response(pdu, buf, len, COAP_CODE_INTERNAL_SERVER_ERROR);
            }
            //GCOAP Response
            return gcoap_response(pdu, buf, len, COAP_CODE_CHANGED);
    }

    return 0;
}

//Inhalt (Id, req_name, Hilfsfunktion (konvertiert Klassenid in str)) fuer gcoap_saul_init()
//static inline ist nur hinweis fuer compiler als sogenannte exception (Fehlerwerfen)
//buffer = Dort wird abgespeichert
//CGOAP_SAUL_PATHLEN = Maximale Anzahl der Bytes
//"saul..." = Formatzeichenkette Saul Registry
static inline void generate_path(char *buffer, int id, saul_reg_t *reg) {
    snprintf(buffer, GCOAP_PATH_LEN, "/saul/%d-%s-%s",
             id,
             reg->name,
             saul_class_to_str(reg->driver->type));
}

//Vgerleicht Strings, Wenn ungleich (return <0 oder >0), wenn gleich (return 0) fur das sortieren
static inline int compare_path(const void *a, const void *b) {
    return strcmp(((coap_resource_t*)a)->path, ((coap_resource_t*)b)->path);
}


void gcoap_saul_init(void) {
    /* Coap Ressourcen fuer alle Saul Devices erstellen */
    int n = 0;
    for(saul_reg_t *reg = saul_reg_find_nth(0); n < GCOAP_RES_MAX && reg != NULL; reg = saul_reg_find_nth(++n)) {
        /* Pfad fuer Saul geraete generieren (In generate_path werden diese nach ID, reg in abgespeichert) */
        generate_path(_paths[n], n, reg);

        /* Erstellen von Coap-Ressourcen mit Saul-Device als Kontext */
        //Fuer jedes Device werden die Methoden PUT und GET erstellt
        //reg sind Devices aus der Registry
        //In Path wird fuer jede ID in der reg den Pfad zur entsprechenden Device
        _resources[n] = (coap_resource_t) {
            .path = _paths[n],
            .methods = COAP_GET | COAP_PUT,
            .handler = saul_handler,
            .context = reg
        };
    }

    /* Coap resourcen muessen fuer gcoap_register_listerner sortiert werden */
    qsort(_resources, n, sizeof(coap_resource_t), compare_path);

    //Resourcen Menge ist nach for Schleife in n gespeichert und Resource_len bekommt n initialisiert
    _listener.resources_len = n;

    //Fuer Verwendung von gcoap Resourcen
    gcoap_register_listener(&_listener);
}
