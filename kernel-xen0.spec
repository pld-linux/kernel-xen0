#
# TODO:
# - test it
#
# 2.6.30 status:
# - builds x86_64
#
# Conditional build:
%bcond_without	source		# don't build kernel-source package
%bcond_with	noarch		# build noarch packages
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	pae		# build PAE (HIGHMEM64G) support on uniprocessor
%bcond_with	preempt-nort	# build preemptable no realtime kernel

%{?debug:%define with_verbose 1}

%ifnarch %{ix86}
%undefine	with_pae
%endif

%if "%{_arch}" == "noarch"
%define		with_noarch	1
%endif

%define		have_isa	1
%define		have_oss	1
%define		have_pcmcia	1
%define		have_sound	1
%define		have_drm	1

%ifnarch %{ix86} alpha ppc
%define		have_isa	0
%endif
%ifarch sparc sparc64
%define		have_drm	0
%define		have_oss	0
%define		have_pcmcia	0
%endif

%define		alt_kernel	xen0

# kernel release (used in filesystem and eventually in uname -r)
# modules will be looked from /lib/modules/%{kernel_release}
# localversion is just that without version for "> localversion"
%define		localversion %{rel}
%define		kernel_release %{version}_%{alt_kernel}-%{localversion}
%define		_kernelsrcdir	/usr/src/linux-%{version}_%{alt_kernel}

%define		basever	2.6.30
%define		postver	%{nil}
%define		rel		0.1

Summary:	The Linux kernel (the core of the Linux operating system)
Summary(de.UTF-8):	Der Linux-Kernel (Kern des Linux-Betriebssystems)
Summary(et.UTF-8):	Linuxi kernel (ehk operatsioonisüsteemi tuum)
Summary(fr.UTF-8):	Le Kernel-Linux (La partie centrale du systeme)
Summary(pl.UTF-8):	Jądro Linuksa
Name:		kernel-%{alt_kernel}
Version:	%{basever}%{postver}
Release:	%{rel}
Epoch:		3
License:	GPL v2
Group:		Base/Kernel

# git://git.kernel.org/pub/scm/linux/kernel/git/jeremy/xen.git xen/dom0/core
Source0:	http://xatka.net/~z/PLD/%{name}-%{basever}.tar.bz2
# Source0-md5:	eb8fc0005bf72707ddb83d113c372a8c
%if "%{postver}" != "%{nil}"
Source1:	http://www.kernel.org/pub/linux/kernel/v2.6/patch-%{version}.bz2
# Source1-md5:	6cac5e59d5562b591cdda485941204d5
%endif
Source2:	kernel-xen0-module-build.pl
Source3:	kernel-config.py
Source4:	kernel-config-update.py
Source5:	kernel-multiarch.make
Source6:	kernel-xen0-config.h
Source7:	kernel-xen0-multiarch.conf
Source8:	kernel-xen0-preempt-nort.config
Source9:	kernel-xen0-no-preempt-nort.config
URL:		http://www.kernel.org/
BuildRequires:	binutils >= 3:2.14.90.0.7
%ifarch sparc sparc64
BuildRequires:	elftoaout
%endif
BuildRequires:	%{kgcc_package} >= 5:3.2
BuildRequires:	module-init-tools
# for hostname command
BuildRequires:	net-tools
BuildRequires:	perl-base
BuildRequires:	python
BuildRequires:	python-modules
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	sed >= 4.0
%ifarch ppc
BuildRequires:	uboot-mkimage
%endif
Autoreqprov:	no
Requires:	/sbin/depmod
Requires:	coreutils
Requires:	geninitrd >= 2.57
Requires:	module-init-tools >= 0.9.9
Provides:	%{name}(vermagic) = %{kernel_release}
Obsoletes:	kernel-xen0-net-iwl3945
Obsoletes:	kernel-xen0-net-iwl4965
Conflicts:	e2fsprogs < 1.29
Conflicts:	isdn4k-utils < 3.1pre1
Conflicts:	jfsutils < 1.1.3
Conflicts:	module-init-tools < 0.9.10
Conflicts:	nfs-utils < 1.0.5
Conflicts:	oprofile < 0.9
Conflicts:	ppp < 1:2.4.0
Conflicts:	procps < 3.2.0
Conflicts:	quota-tools < 3.09
Conflicts:	reiserfsprogs < 3.6.3
Conflicts:	udev < 1:071
Conflicts:	util-linux < 2.10o
Conflicts:	xfsprogs < 2.6.0
ExclusiveOS:	Linux
%{?with_noarch:BuildArch:	noarch}
# TODO: arm ia64 ppc64 sparc64
ExclusiveArch:	%{ix86} %{x8664} alpha ppc sparc noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%ifarch %{ix86} %{x8664}
%define		target_arch_dir	x86
%else
%define		target_arch_dir	%{_target_base_arch}
%endif

# No ELF objects there to strip (skips processing 27k files)
%define		_noautostrip	.*%{_kernelsrcdir}/.*
%define		_noautochrpath	.*%{_kernelsrcdir}/.*

%define		initrd_dir	/boot

%define		topdir		%{_builddir}/%{name}-%{version}
%define		srcdir		%{topdir}/linux-%{basever}
%define		objdir		%{topdir}/%{targetobj}
%define		targetobj	%{_target_base_arch}-gcc-%(%{kgcc} -dumpversion)

%define		CommonOpts	HOSTCC="%{kgcc}" HOSTCFLAGS="-Wall -Wstrict-prototypes %{rpmcflags} -fomit-frame-pointer"
%if "%{_target_base_arch}" != "%{_arch}"
	%define	MakeOpts %{CommonOpts} ARCH=%{_target_base_arch} CROSS_COMPILE=%{_target_cpu}-pld-linux-
	%define	DepMod /bin/true

	%if "%{_arch}" == "x86_64" && "%{_target_base_arch}" == "i386"
	%define	MakeOpts %{CommonOpts} CC="%{kgcc}" ARCH=%{_target_base_arch}
	%define	DepMod /sbin/depmod
	%endif

%else
	%define MakeOpts %{CommonOpts} CC="%{kgcc}"
	%define	DepMod /sbin/depmod
%endif

%define __features Enabled features:\
%{?debug: - DEBUG}\
%define Features %(echo "%{__features}
%{?with_pae: - PAE (HIGHMEM64G) support}" | sed '/^$/d')
# vim: "

%description
This package contains the Linux kernel that is used to boot and run
your system. It contains few device drivers for specific hardware.
Most hardware is instead supported by modules loaded after booting.

%{Features}

%description -l de.UTF-8
Das Kernel-Packet enthält den Linux-Kernel (vmlinuz), den Kern des
Linux-Betriebssystems. Der Kernel ist für grundliegende
Systemfunktionen verantwortlich: Speicherreservierung,
Prozeß-Management, Geräte Ein- und Ausgaben, usw.

%{Features}

%description -l fr.UTF-8
Le package kernel contient le kernel linux (vmlinuz), la partie
centrale d'un système d'exploitation Linux. Le noyau traite les
fonctions basiques d'un système d'exploitation: allocation mémoire,
allocation de process, entrée/sortie de peripheriques, etc.

%{Features}

%description -l pl.UTF-8
Pakiet zawiera jądro Linuksa niezbędne do prawidłowego działania
Twojego komputera. Zawiera w sobie sterowniki do sprzętu znajdującego
się w komputerze, takiego jak sterowniki dysków itp.

%{Features}

%package vmlinux
Summary:	vmlinux - uncompressed kernel image
Summary(de.UTF-8):	vmlinux - dekompressiertes Kernel Bild
Summary(pl.UTF-8):	vmlinux - rozpakowany obraz jądra
Group:		Base/Kernel

%description vmlinux
vmlinux - uncompressed kernel image.

%description vmlinux -l de.UTF-8
vmlinux - dekompressiertes Kernel Bild.

%description vmlinux -l pl.UTF-8
vmlinux - rozpakowany obraz jądra.

%package dirs
Summary:	common dirs for kernel packages
Summary(pl.UTF-8):	Katalogi wspólne dla pakietów kernela
Group:		Base/Kernel

%description dirs
This package provides common dirs shared between various kernel
packages.

%description dirs -l pl.UTF-8
Katalog ten udostepnia katalogi współdzielone pomiędzy różnymi
pakietami kernela.

%package drm
Summary:	DRM kernel modules
Summary(de.UTF-8):	DRM Kernel Treiber
Summary(pl.UTF-8):	Sterowniki DRM
Group:		Base/Kernel
Requires:	%{name} = %{epoch}:%{version}-%{release}
Autoreqprov:	no

%description drm
DRM kernel modules.

%description drm -l de.UTF-8
DRM Kernel Treiber.

%description drm -l pl.UTF-8
Sterowniki DRM.

%package pcmcia
Summary:	PCMCIA modules
Summary(de.UTF-8):	PCMCIA Module
Summary(pl.UTF-8):	Moduły PCMCIA
Group:		Base/Kernel
Requires:	%{name} = %{epoch}:%{version}-%{release}
Conflicts:	pcmcia-cs < 3.1.21
Conflicts:	pcmciautils < 004
Autoreqprov:	no

%description pcmcia
PCMCIA modules.

%description pcmcia -l de.UTF-8
PCMCIA Module.

%description pcmcia -l pl.UTF-8
Moduły PCMCIA.

%package sound-alsa
Summary:	ALSA kernel modules
Summary(de.UTF-8):	ALSA Kernel Module
Summary(pl.UTF-8):	Sterowniki dźwięku ALSA
Group:		Base/Kernel
Requires:	%{name} = %{epoch}:%{version}-%{release}
Autoreqprov:	no

%description sound-alsa
ALSA (Advanced Linux Sound Architecture) sound drivers.

%description sound-alsa -l de.UTF-8
ALSA (Advanced Linux Sound Architecture) Sound-Treiber.

%description sound-alsa -l pl.UTF-8
Sterowniki dźwięku ALSA (Advanced Linux Sound Architecture).

%package sound-oss
Summary:	OSS kernel modules
Summary(de.UTF-8):	OSS Kernel Module
Summary(pl.UTF-8):	Sterowniki dźwięku OSS
Group:		Base/Kernel
Requires:	%{name} = %{epoch}:%{version}-%{release}
Autoreqprov:	no

%description sound-oss
OSS (Open Sound System) drivers.

%description sound-oss -l de.UTF-8
OSS (Open Sound System) Treiber.

%description sound-oss -l pl.UTF-8
Sterowniki dźwięku OSS (Open Sound System).

%package firmware
Summary:	Firmware for Linux kernel drivers
Summary(pl.UTF-8):	Firmware dla sterowników z jądra Linuksa
Group:		System Environment/Kernel

%description firmware
Firmware for Linux kernel drivers.

%description firmware -l pl.UTF-8
Firmware dla sterowników z jądra Linuksa.

%package config
Summary:	Kernel config and module symvers
Summary(pl.UTF-8):	Konfiguracja jądra i wersje symboli w modułach (symvers)
Group:		Development/Building
Autoreqprov:	no
Conflicts:	rpmbuild(macros) < 1.433

%description config
Kernel config and module symvers.

%description config -l pl.UTF-8
Konfiguracja jądra i wersje symboli w modułąch (symvers).

%package headers
Summary:	Header files for the Linux kernel
Summary(de.UTF-8):	Header Dateien für den Linux-Kernel
Summary(pl.UTF-8):	Pliki nagłówkowe jądra Linuksa
Group:		Development/Building
Requires:	%{name}-config = %{epoch}:%{version}-%{release}
Autoreqprov:	no

%description headers
These are the C header files for the Linux kernel, which define
structures and constants that are needed when rebuilding the kernel or
building kernel modules.

%description headers -l de.UTF-8
Dies sind die C Header Dateien für den Linux-Kernel, die definierte
Strukturen und Konstante beinhalten, die beim rekompilieren des Kernels
oder bei Kernel Modul kompilationen gebraucht werden.

%description headers -l pl.UTF-8
Pakiet zawiera pliki nagłówkowe jądra, niezbędne do rekompilacji jądra
oraz budowania modułów jądra.

%package module-build
Summary:	Development files for building kernel modules
Summary(de.UTF-8):	Development Dateien die beim Kernel Modul kompilationen gebraucht werden
Summary(pl.UTF-8):	Pliki służące do budowania modułów jądra
Group:		Development/Building
Requires:	%{name}-headers = %{epoch}:%{version}-%{release}
Autoreqprov:	no

%description module-build
Development files from kernel source tree needed to build Linux kernel
modules from external packages.

%description module-build -l de.UTF-8
Development Dateien des Linux-Kernels die beim kompilieren externer
Kernel Module gebraucht werden.

%description module-build -l pl.UTF-8
Pliki ze drzewa źródeł jądra potrzebne do budowania modułów jądra
Linuksa z zewnętrznych pakietów.

%package source
Summary:	Kernel source tree
Summary(de.UTF-8):	Der Kernel Quelltext
Summary(pl.UTF-8):	Kod źródłowy jądra Linuksa
Group:		Development/Building
Requires:	%{name}-module-build = %{epoch}:%{version}-%{release}
Autoreqprov:	no

%description source
This is the source code for the Linux kernel. You can build a custom
kernel that is better tuned to your particular hardware.

%description source -l de.UTF-8
Das Kernel-Source-Packet enthält den source code (C/Assembler-Code)
des Linux-Kernels. Die Source-Dateien werden gebraucht, um viele
C-Programme zu kompilieren, da sie auf Konstanten zurückgreifen, die
im Kernel-Source definiert sind. Die Source-Dateien können auch
benutzt werden, um einen Kernel zu kompilieren, der besser auf Ihre
Hardware ausgerichtet ist.

%description source -l fr.UTF-8
Le package pour le kernel-source contient le code source pour le noyau
linux. Ces sources sont nécessaires pour compiler la plupart des
programmes C, car il dépend de constantes définies dans le code
source. Les sources peuvent être aussi utilisée pour compiler un noyau
personnalisé pour avoir de meilleures performances sur des matériels
particuliers.

%description source -l pl.UTF-8
Pakiet zawiera kod źródłowy jądra systemu.

%package doc
Summary:	Kernel documentation
Summary(de.UTF-8):	Kernel Dokumentation
Summary(pl.UTF-8):	Dokumentacja do jądra Linuksa
Group:		Documentation
Autoreqprov:	no

%description doc
This is the documentation for the Linux kernel, as found in
/usr/src/linux/Documentation directory.

%description doc -l de.UTF-8
Dies ist die Kernel Dokumentation wie sie im 'Documentation'
Verzeichniss vorgefunden werden kann.

%description doc -l pl.UTF-8
Pakiet zawiera dokumentację do jądra Linuksa pochodzącą z katalogu
/usr/src/linux/Documentation.

%prep
%setup -qc
ln -s %{SOURCE2} kernel-module-build.pl
ln -s %{SOURCE3} kernel-config.py
ln -s %{SOURCE4} kernel-config-update.py
ln -s %{SOURCE5} Makefile

cd linux-%{basever}
%if "%{postver}" != "%{nil}"
%{__bzip2} -dc %{SOURCE1} | %{__patch} -p1 -s
%endif

# Fix EXTRAVERSION in main Makefile
sed -i 's#EXTRAVERSION =.*#EXTRAVERSION = %{postver}_%{alt_kernel}#g' Makefile

# cleanup backups after patching
find '(' -name '*~' -o -name '*.orig' -o -name '.gitignore' ')' -print0 | xargs -0 -r -l512 rm -f

%if %{without noarch}
%build
install -d %{objdir}
cat > %{targetobj}.mk <<'EOF'
# generated by %{name}.spec
KERNELSRC		:= %{_builddir}/%{name}-%{version}/linux-%{basever}
KERNELOUTPUT	:= %{objdir}

SRCARCH		:= %{target_arch_dir}
ARCH		:= %{_target_base_arch}
Q			:= %{!?with_verbose:@}
MAKE_OPTS	:= %{MakeOpts}

CONFIGS += %{_sourcedir}/kernel-xen0-multiarch.conf
%if %{with preempt-nort}
CONFIGS += %{_sourcedir}/kernel-xen0-preempt-nort.config
%else
CONFIGS += %{_sourcedir}/kernel-xen0-no-preempt-nort.config
%endif

# config where we ignore timestamps
CONFIG_NODEP += %{objdir}/.kernel-autogen.conf
EOF

# update config at spec time
# if you have config file, add it to above Makefile
pykconfig() {
	set -x
	echo '# %{name}.spec overrides'
	echo 'LOCALVERSION="-%{localversion}"'

	%{?debug:echo '# debug options'}
	%{?debug:echo 'DEBUG_SLAB=y'}
	%{?debug:echo 'DEBUG_PREEMPT=y'}
	%{?debug:echo 'RT_DEADLOCK_DETECT=y'}

%ifarch %{ix86}
	echo '# x86 tuneup'
	%ifarch i386
	echo 'M386=y'
	echo 'X86_F00F_BUG=y'
	%endif
	%ifarch i486
	echo 'M486=y'
	echo 'X86_F00F_BUG=y'
	%endif
	%ifarch i586
	echo 'M586=y'
	echo 'X86_F00F_BUG=y'
	%endif
	%ifarch i686
	echo 'M686=y'
	%endif
	%ifarch pentium3
	echo 'MPENTIUMIII=y'
	%endif
	%ifarch pentium4
	echo 'MPENTIUM4=y'
	%endif
	%ifarch athlon
	echo 'MK7=y'
	echo 'X86_PPRO_FENCE='
	echo 'X86_USE_3DNOW=y'
	%endif
	%ifarch i686 athlon pentium3 pentium4
	%if %{with pae}
		echo 'HIGHMEM4G=n'
		echo 'HIGHMEM64G=y'
		echo 'X86_PAE=y'
	%endif
	echo 'MATH_EMULATION=n'
	%endif
%endif
}

# generate .config and kernel.conf
pykconfig > %{objdir}/.kernel-autogen.conf
%{__make} TARGETOBJ=%{targetobj} pykconfig

# build kernel
%{__make} TARGETOBJ=%{targetobj} all

# build reverse config and show diff
%{__make} TARGETOBJ=%{targetobj} pykconfig
diff -u %{_sourcedir}/kernel-xen0-multiarch.conf %{objdir}/kernel.conf || :
%endif # arch build

%install
rm -rf $RPM_BUILD_ROOT
# touch for noarch build (exclude list)
install -d $RPM_BUILD_ROOT%{_kernelsrcdir}/include/linux
touch $RPM_BUILD_ROOT%{_kernelsrcdir}/include/linux/{utsrelease,version,autoconf-dist}.h

%if %{without noarch}
%{__make} %{MakeOpts} %{!?with_verbose:-s} modules_install \
	-C %{objdir} \
	%{?with_verbose:V=1} \
	DEPMOD=%{DepMod} \
	INSTALL_MOD_PATH=$RPM_BUILD_ROOT \
	KERNELRELEASE=%{kernel_release}

mkdir $RPM_BUILD_ROOT/lib/modules/%{kernel_release}/misc
rm -f $RPM_BUILD_ROOT/lib/modules/%{kernel_release}/{build,source}
touch $RPM_BUILD_ROOT/lib/modules/%{kernel_release}/{build,source}

# /boot
install -d $RPM_BUILD_ROOT/boot
cp -a %{objdir}/System.map $RPM_BUILD_ROOT/boot/System.map-%{kernel_release}
install %{objdir}/vmlinux $RPM_BUILD_ROOT/boot/vmlinux-%{kernel_release}
%ifarch %{ix86} %{x8664}
cp -a %{objdir}/arch/%{target_arch_dir}/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-%{kernel_release}
%endif
%ifarch ppc ppc64
install %{objdir}/vmlinux $RPM_BUILD_ROOT/boot/vmlinuz-%{kernel_release}
%endif
%ifarch alpha sparc sparc64
	%{__gzip} -cfv %{objdir}/vmlinux > %{objdir}/vmlinuz
	cp -a %{objdir}/vmlinuz $RPM_BUILD_ROOT/boot/vmlinuz-%{kernel_release}
%ifarch sparc
	elftoaout %{objdir}/arch/sparc/boot/image -o %{objdir}/vmlinux.aout
	install %{objdir}/vmlinux.aout $RPM_BUILD_ROOT/boot/vmlinux.aout-%{kernel_release}
%endif
%ifarch sparc64
	elftoaout %{objdir}/arch/sparc64/boot/image -o %{objdir}/vmlinux.aout
	install %{objdir}/vmlinux.aout $RPM_BUILD_ROOT/boot/vmlinux.aout-%{kernel_release}
%endif
%endif # ifarch alpha sparc sparc64

# for initrd
touch $RPM_BUILD_ROOT/boot/initrd-%{kernel_release}.gz

%if "%{_target_base_arch}" != "%{_arch}"
touch $RPM_BUILD_ROOT/lib/modules/%{kernel_release}/modules.dep
%endif

# /etc/modrobe.d
install -d $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{kernel_release}

# /usr/src/linux
# maybe package these to -module-build, then -headers could be noarch
cp -a %{objdir}/Module.symvers $RPM_BUILD_ROOT%{_kernelsrcdir}/Module.symvers-dist
cp -aL %{objdir}/.config $RPM_BUILD_ROOT%{_kernelsrcdir}/config-dist
cp -a %{objdir}/include/linux/autoconf.h $RPM_BUILD_ROOT%{_kernelsrcdir}/include/linux/autoconf-dist.h
cp -a %{objdir}/include/linux/{utsrelease,version}.h $RPM_BUILD_ROOT%{_kernelsrcdir}/include/linux
%endif # arch dependant

%if %{with noarch}
# test if we can hardlink -- %{_builddir} and $RPM_BUILD_ROOT on same partition
if cp -al %{srcdir}/COPYING $RPM_BUILD_ROOT/COPYING 2>/dev/null; then
	l=l
	rm -f $RPM_BUILD_ROOT/COPYING
fi
cp -a$l %{srcdir}/* $RPM_BUILD_ROOT%{_kernelsrcdir}

install -d $RPM_BUILD_ROOT/lib/modules/%{kernel_release}
cp -a %{SOURCE6} $RPM_BUILD_ROOT%{_kernelsrcdir}/include/linux/config.h
%endif # arch independant

# collect module-build files and directories
# Usage: kernel-module-build.pl $rpmdir $fileoutdir
fileoutdir=$(pwd)
cd $RPM_BUILD_ROOT%{_kernelsrcdir}
%{__perl} %{topdir}/kernel-module-build.pl %{_kernelsrcdir} $fileoutdir
cd -

%clean
rm -rf $RPM_BUILD_ROOT

%preun
if [ -x /sbin/new-kernel-pkg ]; then
	/sbin/new-kernel-pkg --remove %{kernel_release}
fi

%post
ln -sf vmlinuz-%{kernel_release} /boot/vmlinuz-%{alt_kernel}
ln -sf System.map-%{kernel_release} /boot/System.map-%{alt_kernel}
if [ ! -e /boot/vmlinuz ]; then
	ln -sf vmlinuz-%{alt_kernel} /boot/vmlinuz
	ln -sf System.map-%{alt_kernel} /boot/System.map
	ln -sf initrd-%{alt_kernel} %{initrd_dir}/initrd
fi

%depmod %{kernel_release}

/sbin/geninitrd -f --initrdfs=initramfs  %{initrd_dir}/initrd-%{kernel_release}.gz %{kernel_release}
ln -sf initrd-%{kernel_release}.gz %{initrd_dir}/initrd-%{alt_kernel}

if [ -x /sbin/new-kernel-pkg ]; then
	if [ -f /etc/pld-release ]; then
		title=$(sed 's/^[0-9.]\+ //' < /etc/pld-release)
	else
		title='PLD Linux'
	fi

	title="$title %{alt_kernel}"

	/sbin/new-kernel-pkg --initrdfile=%{initrd_dir}/initrd-%{kernel_release}.gz --install %{kernel_release} --banner "$title"
elif [ -x /sbin/rc-boot ]; then
	/sbin/rc-boot 1>&2 || :
fi

%post vmlinux
ln -sf vmlinux-%{kernel_release} /boot/vmlinux-%{alt_kernel}

%post drm
%depmod %{kernel_release}

%postun drm
%depmod %{kernel_release}

%post pcmcia
%depmod %{kernel_release}

%postun pcmcia
%depmod %{kernel_release}

%post sound-alsa
%depmod %{kernel_release}

%postun sound-alsa
%depmod %{kernel_release}

%post sound-oss
%depmod %{kernel_release}

%postun sound-oss
%depmod %{kernel_release}

%post headers
rm -f %{_prefix}/src/linux-%{alt_kernel}
ln -snf %{basename:%{_kernelsrcdir}} %{_prefix}/src/linux-%{alt_kernel}

%postun headers
if [ "$1" = "0" ]; then
	if [ -L %{_prefix}/src/linux-%{alt_kernel} ]; then
		if [ "$(readlink %{_prefix}/src/linux-%{alt_kernel})" = "linux-%{version}_%{alt_kernel}" ]; then
			rm -f %{_prefix}/src/linux-%{alt_kernel}
		fi
	fi
fi

%triggerin module-build -- %{name} = %{epoch}:%{version}-%{release}
ln -sfn %{_kernelsrcdir} /lib/modules/%{kernel_release}/build
ln -sfn %{_kernelsrcdir} /lib/modules/%{kernel_release}/source

%triggerun module-build -- %{name} = %{epoch}:%{version}-%{release}
if [ "$1" = "0" ]; then
	rm -f /lib/modules/%{kernel_release}/{build,source}
fi

%if %{without noarch}
%files
%defattr(644,root,root,755)
%ifarch sparc sparc64
/boot/vmlinux.aout-%{kernel_release}
%endif
/boot/vmlinuz-%{kernel_release}
/boot/System.map-%{kernel_release}
%ghost /boot/initrd-%{kernel_release}.gz
%dir /lib/modules/%{kernel_release}
%dir /lib/modules/%{kernel_release}/kernel
/lib/modules/%{kernel_release}/kernel/arch
/lib/modules/%{kernel_release}/kernel/crypto
/lib/modules/%{kernel_release}/kernel/drivers
%if %{have_drm}
%exclude /lib/modules/%{kernel_release}/kernel/drivers/gpu/drm
%endif
/lib/modules/%{kernel_release}/kernel/fs
/lib/modules/%{kernel_release}/kernel/kernel
/lib/modules/%{kernel_release}/kernel/lib
/lib/modules/%{kernel_release}/kernel/net
%dir /lib/modules/%{kernel_release}/kernel/sound
/lib/modules/%{kernel_release}/kernel/sound/soundcore.*
%if %{have_sound}
%ifnarch sparc sparc64
%exclude /lib/modules/%{kernel_release}/kernel/drivers/media/video/*/*-alsa.ko*
%endif
%endif
%dir /lib/modules/%{kernel_release}/misc
%if %{have_pcmcia}
%exclude /lib/modules/%{kernel_release}/kernel/drivers/pcmcia
%exclude /lib/modules/%{kernel_release}/kernel/drivers/*/pcmcia
%exclude /lib/modules/%{kernel_release}/kernel/drivers/bluetooth/*_cs.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/isdn/hardware/avm/avm_cs.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/net/wireless/*_cs.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/net/wireless/hostap/hostap_cs.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/parport/parport_cs.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/serial/serial_cs.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/telephony/ixj_pcmcia.ko*
%exclude /lib/modules/%{kernel_release}/kernel/drivers/usb/host/sl811_cs.ko*
%endif
%ghost /lib/modules/%{kernel_release}/modules.*
%ghost /lib/modules/%{kernel_release}/build
%ghost /lib/modules/%{kernel_release}/source

%dir %{_sysconfdir}/modprobe.d/%{kernel_release}

%files dirs
%defattr(644,root,root,755)
%dir %{_kernelsrcdir}

%ifarch alpha %{ix86} %{x8664} ppc ppc64 sparc sparc64
%files vmlinux
%defattr(644,root,root,755)
/boot/vmlinux-%{kernel_release}
%endif

%if %{have_drm}
%files drm
%defattr(644,root,root,755)
/lib/modules/%{kernel_release}/kernel/drivers/gpu/drm
%endif

%if %{have_pcmcia}
%files pcmcia
%defattr(644,root,root,755)
/lib/modules/%{kernel_release}/kernel/drivers/pcmcia
/lib/modules/%{kernel_release}/kernel/drivers/*/pcmcia
/lib/modules/%{kernel_release}/kernel/drivers/bluetooth/*_cs.ko*
/lib/modules/%{kernel_release}/kernel/drivers/isdn/hardware/avm/avm_cs.ko*
/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/*_cs.ko*
/lib/modules/%{kernel_release}/kernel/drivers/net/wireless/hostap/hostap_cs.ko*
/lib/modules/%{kernel_release}/kernel/drivers/parport/parport_cs.ko*
/lib/modules/%{kernel_release}/kernel/drivers/serial/serial_cs.ko*
/lib/modules/%{kernel_release}/kernel/drivers/telephony/ixj_pcmcia.ko*
/lib/modules/%{kernel_release}/kernel/drivers/usb/host/sl811_cs.ko*
/lib/modules/%{kernel_release}/kernel/sound/pcmcia
%endif

%if %{have_sound}
%files sound-alsa
%defattr(644,root,root,755)
/lib/modules/%{kernel_release}/kernel/sound
%exclude %dir /lib/modules/%{kernel_release}/kernel/sound
%exclude /lib/modules/%{kernel_release}/kernel/sound/soundcore.*
%if %{have_oss}
%exclude /lib/modules/%{kernel_release}/kernel/sound/oss
%endif
%if %{have_pcmcia}
%exclude /lib/modules/%{kernel_release}/kernel/sound/pcmcia
%endif

%if %{have_oss}
%files sound-oss
%defattr(644,root,root,755)
/lib/modules/%{kernel_release}/kernel/sound/oss
%endif			# %{have_oss}
%endif			# %{have_sound}

%files firmware
%dir /lib/firmware/3com
/lib/firmware/3com/3C359.bin
/lib/firmware/3com/typhoon.bin
%dir /lib/firmware/acenic
/lib/firmware/acenic/tg1.bin
/lib/firmware/acenic/tg2.bin
%dir /lib/firmware/adaptec
/lib/firmware/adaptec/starfire_rx.bin
/lib/firmware/adaptec/starfire_tx.bin
%dir /lib/firmware/advansys
/lib/firmware/advansys/3550.bin
/lib/firmware/advansys/38C0800.bin
/lib/firmware/advansys/38C1600.bin
/lib/firmware/advansys/mcode.bin
/lib/firmware/atmsar11.fw
%dir /lib/firmware/av7110
/lib/firmware/av7110/bootcode.bin
%dir /lib/firmware/bnx2
/lib/firmware/bnx2/bnx2-mips-06-4.6.16.fw
/lib/firmware/bnx2/bnx2-mips-09-4.6.17.fw
/lib/firmware/bnx2/bnx2-rv2p-06-4.6.16.fw
/lib/firmware/bnx2/bnx2-rv2p-09-4.6.15.fw
/lib/firmware/bnx2x-e1-4.8.53.0.fw
/lib/firmware/bnx2x-e1h-4.8.53.0.fw
%dir /lib/firmware/cis
/lib/firmware/cis/3CCFEM556.cis
/lib/firmware/cis/3CXEM556.cis
/lib/firmware/cis/LA-PCM.cis
/lib/firmware/cis/LA-PCM.cis
%dir /lib/firmware/cpia2
/lib/firmware/cpia2/stv0672_vp4.bin
%dir /lib/firmware/cxgb3
/lib/firmware/cxgb3/t3b_psram-1.1.0.bin
/lib/firmware/cxgb3/t3c_psram-1.1.0.bin
/lib/firmware/cxgb3/t3fw-7.4.0.bin
%dir /lib/firmware/dabusb
/lib/firmware/dabusb/bitstream.bin
/lib/firmware/dabusb/firmware.fw
%dir /lib/firmware/e100
/lib/firmware/e100/d101m_ucode.bin
/lib/firmware/e100/d101s_ucode.bin
/lib/firmware/e100/d102e_ucode.bin
%dir /lib/firmware/edgeport
/lib/firmware/edgeport/boot.fw
/lib/firmware/edgeport/boot2.fw
/lib/firmware/edgeport/down.fw
/lib/firmware/edgeport/down2.fw
/lib/firmware/edgeport/down3.bin
%dir /lib/firmware/emi26
/lib/firmware/emi26/bitstream.fw
/lib/firmware/emi26/firmware.fw
/lib/firmware/emi26/loader.fw
%dir /lib/firmware/emi62
/lib/firmware/emi62/bitstream.fw
/lib/firmware/emi62/loader.fw
/lib/firmware/emi62/midi.fw
/lib/firmware/emi62/spdif.fw
%dir /lib/firmware/ess
/lib/firmware/ess/maestro3_assp_kernel.fw
/lib/firmware/ess/maestro3_assp_minisrc.fw
/lib/firmware/intelliport2.bin
%dir /lib/firmware/kaweth
/lib/firmware/kaweth/new_code.bin
/lib/firmware/kaweth/new_code_fix.bin
/lib/firmware/kaweth/trigger_code.bin
/lib/firmware/kaweth/trigger_code_fix.bin
%dir /lib/firmware/keyspan_pda
/lib/firmware/keyspan_pda/keyspan_pda.fw
/lib/firmware/keyspan_pda/xircom_pgs.fw
%dir /lib/firmware/korg
/lib/firmware/korg/k1212.dsp
/lib/firmware/mts_cdma.fw
/lib/firmware/mts_edge.fw
/lib/firmware/mts_gsm.fw
%dir /lib/firmware/ositech
/lib/firmware/ositech/Xilinx7OD.bin
%dir /lib/firmware/qlogic
/lib/firmware/qlogic/1040.bin
/lib/firmware/qlogic/12160.bin
/lib/firmware/qlogic/1280.bin
%dir /lib/firmware/sun
/lib/firmware/sun/cassini.bin
%dir /lib/firmware/tehuti
/lib/firmware/tehuti/bdx.bin
%dir /lib/firmware/tigon
/lib/firmware/tigon/tg3.bin
/lib/firmware/tigon/tg3_tso.bin
/lib/firmware/tigon/tg3_tso5.bin
/lib/firmware/ti_3410.fw
/lib/firmware/ti_5052.fw
%ifarch %{ix86} ppc
/lib/firmware/tr_smctr.bin
%endif
%dir /lib/firmware/ttusb-budget
/lib/firmware/ttusb-budget/dspbootcode.bin
%dir /lib/firmware/vicam
/lib/firmware/vicam/firmware.fw
/lib/firmware/whiteheat.fw
/lib/firmware/whiteheat_loader.fw
%dir /lib/firmware/yam
/lib/firmware/yam/1200.bin
/lib/firmware/yam/9600.bin
%dir /lib/firmware/yamaha
/lib/firmware/yamaha/ds1_ctrl.fw
/lib/firmware/yamaha/ds1_dsp.fw
/lib/firmware/yamaha/ds1e_ctrl.fw
%ifnarch %{x8664} sparc
/lib/firmware/yamaha/yss225_registers.bin
%endif

%files config
%defattr(644,root,root,755)
%{_kernelsrcdir}/config-dist
%{_kernelsrcdir}/Module.symvers-dist
%dir %{_kernelsrcdir}/include
%dir %{_kernelsrcdir}/include/linux
%{_kernelsrcdir}/include/linux/autoconf-dist.h
%{_kernelsrcdir}/include/linux/utsrelease.h
%{_kernelsrcdir}/include/linux/version.h
%endif # noarch package

%if %{with noarch}
%files headers
%defattr(644,root,root,755)
%{_kernelsrcdir}/include
%exclude %{_kernelsrcdir}/include/linux/autoconf-dist.h
%exclude %{_kernelsrcdir}/include/linux/utsrelease.h
%exclude %{_kernelsrcdir}/include/linux/version.h
%dir %{_kernelsrcdir}/arch
%dir %{_kernelsrcdir}/arch/[!K]*
%{_kernelsrcdir}/arch/*/include
%dir %{_kernelsrcdir}/security
%dir %{_kernelsrcdir}/security/selinux
%{_kernelsrcdir}/security/selinux/include
#%{_kernelsrcdir}/config-dist
#%{_kernelsrcdir}/Module.symvers-dist

%files module-build -f aux_files
%defattr(644,root,root,755)
%{_kernelsrcdir}/Kbuild
%ifarch ppc ppc64
%{_kernelsrcdir}/arch/powerpc/lib/crtsavres.*
%endif
%{_kernelsrcdir}/arch/*/kernel/asm-offsets*
%{_kernelsrcdir}/arch/*/kernel/sigframe*.h
%{_kernelsrcdir}/drivers/lguest/lg.h
%{_kernelsrcdir}/kernel/bounds.c
%dir %{_kernelsrcdir}/scripts
%dir %{_kernelsrcdir}/scripts/kconfig
%{_kernelsrcdir}/scripts/Kbuild.include
%{_kernelsrcdir}/scripts/Makefile*
%{_kernelsrcdir}/scripts/basic
%{_kernelsrcdir}/scripts/mkmakefile
%{_kernelsrcdir}/scripts/mod
%{_kernelsrcdir}/scripts/setlocalversion
%{_kernelsrcdir}/scripts/*.c
%{_kernelsrcdir}/scripts/*.sh
%{_kernelsrcdir}/scripts/kconfig/*
%{_kernelsrcdir}/scripts/mkcompile_h
%dir %{_kernelsrcdir}/scripts/selinux
%{_kernelsrcdir}/scripts/selinux/Makefile
%dir %{_kernelsrcdir}/scripts/selinux/mdp
%{_kernelsrcdir}/scripts/selinux/mdp/Makefile
%{_kernelsrcdir}/scripts/selinux/mdp/*.c

%files doc
%defattr(644,root,root,755)
%{_kernelsrcdir}/Documentation

%if %{with source}
%files source -f aux_files_exc
%defattr(644,root,root,755)
%{_kernelsrcdir}/arch/*/[!Mik]*
%{_kernelsrcdir}/arch/*/kernel/[!M]*
%{_kernelsrcdir}/arch/ia64/ia32/[!M]*
%{_kernelsrcdir}/arch/ia64/install.sh
%{_kernelsrcdir}/arch/m68k/ifpsp060/[!M]*
%{_kernelsrcdir}/arch/m68k/ifpsp060/MISC
%{_kernelsrcdir}/arch/parisc/install.sh
%{_kernelsrcdir}/arch/x86/ia32/[!M]*
%{_kernelsrcdir}/arch/ia64/kvm
%{_kernelsrcdir}/arch/powerpc/kvm
%ifarch ppc ppc64
%exclude %{_kernelsrcdir}/arch/powerpc/lib/crtsavres.*
%endif
%{_kernelsrcdir}/arch/s390/kvm
%{_kernelsrcdir}/arch/x86/kvm
%exclude %{_kernelsrcdir}/arch/*/kernel/asm-offsets*
%exclude %{_kernelsrcdir}/arch/*/kernel/sigframe*.h
%exclude %{_kernelsrcdir}/drivers/lguest/lg.h
%{_kernelsrcdir}/block
%{_kernelsrcdir}/crypto
%{_kernelsrcdir}/drivers
%{_kernelsrcdir}/firmware
%{_kernelsrcdir}/fs
%{_kernelsrcdir}/init
%{_kernelsrcdir}/ipc
%{_kernelsrcdir}/kernel
%exclude %{_kernelsrcdir}/kernel/bounds.c
%{_kernelsrcdir}/lib
%{_kernelsrcdir}/mm
%{_kernelsrcdir}/net
%{_kernelsrcdir}/virt
%{_kernelsrcdir}/samples
%{_kernelsrcdir}/scripts/*
%exclude %{_kernelsrcdir}/scripts/Kbuild.include
%exclude %{_kernelsrcdir}/scripts/Makefile*
%exclude %{_kernelsrcdir}/scripts/basic
%exclude %{_kernelsrcdir}/scripts/kconfig
%exclude %{_kernelsrcdir}/scripts/mkmakefile
%exclude %{_kernelsrcdir}/scripts/mod
%exclude %{_kernelsrcdir}/scripts/setlocalversion
%exclude %{_kernelsrcdir}/scripts/*.c
%exclude %{_kernelsrcdir}/scripts/*.sh
%{_kernelsrcdir}/sound
%{_kernelsrcdir}/security
%exclude %{_kernelsrcdir}/security/selinux/include
%{_kernelsrcdir}/usr
%{_kernelsrcdir}/COPYING
%{_kernelsrcdir}/CREDITS
%{_kernelsrcdir}/MAINTAINERS
%{_kernelsrcdir}/README
%{_kernelsrcdir}/REPORTING-BUGS
%endif
%endif
