CONFIGS :=
CONFIG_NODEP :=
MAKE_OPTS :=
PYTHON := python
SCRIPTSDIR := .

include $(TARGETOBJ).mk

DEFCONFIG := $(KERNELOUTPUT)/pld_defconfig
KCONFIG   := $(KERNELOUTPUT)/.config

kernel-config			:= $(SCRIPTSDIR)/kernel-config.py
kernel-config-update	:= $(SCRIPTSDIR)/kernel-config-update.py

all := $(filter-out all Makefile,$(MAKECMDGOALS))

all:
	$(MAKE) -C $(KERNELSRC) O=$(KERNELOUTPUT) $(MAKE_OPTS) $(all)

$(KCONFIG): $(DEFCONFIG)

pykconfig: $(KERNELOUTPUT)/kernel.conf
	@echo '  $@ is up to date'

$(KERNELOUTPUT)/kernel.conf: $(KCONFIG) $(kernel-config-update)
	@echo '  kernel-config-update.py $(ARCH) $(KERNELOUTPUT)/.kernel.conf $< > $@'
	$(Q)$(PYTHON) $(kernel-config-update) $(ARCH) $(KERNELOUTPUT)/.kernel.conf $< > .kernel.conf.tmp
	$(Q)mv .kernel.conf.tmp $@

$(DEFCONFIG): $(KERNELOUTPUT)/.kernel.conf $(kernel-config)
	@echo '  kernel-config.py $(ARCH) $< $@'
	$(Q)> .defconfig.tmp
	$(Q)$(PYTHON) $(kernel-config) $(ARCH) $< .defconfig.tmp
	$(Q)mv .defconfig.tmp $@
	$(Q)ln -sf $@ $(KCONFIG)

$(KERNELOUTPUT)/.kernel.conf: $(CONFIGS) $(KERNELOUTPUT)/.kernel-nodep.conf
	$(Q)cat $^ > $@

$(KERNELOUTPUT)/.kernel-nodep.conf: $(CONFIG_NODEP)
	$(Q)if [ ! -f $@ ] || ! cmp -s $< $@; then \
		echo '  cat $< > $@'; \
		cat $< > $@; \
	fi

# vim:ft=make
