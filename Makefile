# Default Makefile, for host native GNRC-based networking

APPLICATION = mygcoapsaul_example

# If no BOARD is found in the environment, use this default:
BOARD ?= native

# This has to be the absolute path to the RIOT base directory:
RIOTBASE ?= $(CURDIR)/RIOT

# Include packages that pull up and auto-init the link layer.
# NOTE: 6LoWPAN will be included if IEEE802.15.4 devices are present
USEMODULE += netdev_default

USEMODULE += auto_init_gnrc_netif
# Specify the mandatory networking modules
USEMODULE += gnrc_ipv6_default
#USEMODULE += gnrc_ipv6_nib_6lbr
USEMODULE += gnrc_ipv6_router_default
# Additional networking modules that can be dropped if not needed
USEMODULE += gnrc_icmpv6_echo

USEMODULE += gcoap
USEMODULE += saul_default
USEMODULE += cord_ep_standalone

# Required by gcoap example
USEMODULE += od
USEMODULE += fmt
USEMODULE += netutils
# Add also the shell, some shell commands
USEMODULE += shell
USEMODULE += shell_commands
USEMODULE += ps

# Comment this out to disable code in RIOT that does safety checking
# which is not needed in a production environment but helps in the
# development process:
DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1

# Instead of simulating an Ethernet connection, we can also simulate
# an IEEE 802.15.4 radio using ZEP
USE_ZEP ?= 0

# set the ZEP port for native
ZEP_PORT_BASE ?= 17754
ifeq (1,$(USE_ZEP))
  TERMFLAGS += -z [::1]:$(ZEP_PORT_BASE)
  USEMODULE += socket_zep

  ifneq (,$(ZEP_MAC))
    TERMFLAGS += --eui64=$(ZEP_MAC)
  endif
endif

include $(RIOTBASE)/Makefile.include

# Add Buffer Size
CFLAGS += -DCONFIG_GCOAP_PDU_BUF_SIZE=1024

# For now this goes after the inclusion of Makefile.include so Kconfig symbols
# are available. Only set configuration via CFLAGS if Kconfig is not being used
# for this module.
ifndef CONFIG_KCONFIG_MODULE_GCOAP
## Uncomment to redefine port, for example use 61616 for RFC 6282 UDP compression.
#GCOAP_PORT = 5683
#CFLAGS += -DCONFIG_GCOAP_PORT=$(GCOAP_PORT)

## Uncomment to redefine request token length, max 8.
#GCOAP_TOKENLEN = 2
#CFLAGS += -DCONFIG_GCOAP_TOKENLEN=$(GCOAP_TOKENLEN)

# Increase from default for confirmable block2 follow-on requests
GCOAP_RESEND_BUFS_MAX ?= 2
CFLAGS += -DCONFIG_GCOAP_RESEND_BUFS_MAX=$(GCOAP_RESEND_BUFS_MAX)
endif

#######################################################################
### Protokolldaten pufferung, Relevanz herausfinden
CFLAGS += -DCONFIG_GCOAP_PDU_BUF_SIZE=1024
##Channel?
CFLAGS += -DCONFIG_IEEE802154_DEFAULT_CHANNEL=22
CFLAGS += -DCONFIG_GNRC_IPV6_NIB_SLAAC=1


###Fuer Resource Directory###
# For debugging and demonstration purposes, we limit the lifetime to 60s
# Set CONFIG_CORD_LT only if not being set via Kconfig
# ifndef CONFIG_CORD_LT
# #Lebensdauer
# CFLAGS += -DCONFIG_CORD_LT=60
# #Endpunktname des Knotens
# #CFLAGS += "-DCONFIG_CORD_EP=EP_Test_Name
# endif
