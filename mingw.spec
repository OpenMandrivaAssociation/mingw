%bcond_with bootstrap

Name: mingw
Version: 7.0.0
Release: 4
Group: Development/Tools
Url: http://mingw-w64.org/
Source0: https://netix.dl.sourceforge.net/project/mingw-w64/mingw-w64/mingw-w64-release/mingw-w64-v%{version}.tar.bz2
Patch0: widl-aarch64-buildfix.patch
Patch1: widl-riscv-buildfix.patch
Summary: Headers and libraries needed to compile Windows applications on Linux
License: Zope Public License
BuildRequires: make
BuildRequires: libtool-base
%if ! %{with bootstrap}
BuildRequires: cross-i686-w32-mingw32-binutils
BuildRequires: cross-i686-w32-mingw32-gcc-bootstrap
BuildRequires: cross-i686-w32-mingw32-libc-bootstrap
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
BuildRequires: cross-x86_64-w64-mingw32-binutils
BuildRequires: cross-x86_64-w64-mingw32-gcc-bootstrap
BuildRequires: cross-x86_64-w64-mingw32-libc-bootstrap
%endif
%endif
%if %{with bootstrap}
Recommends: cross-i686-w32-mingw32-libc-bootstrap
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
Recommends: cross-x86_64-w64-mingw32-libc-bootstrap
%endif
%else
Recommends: cross-i686-w32-mingw32-libc
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
Recommends: cross-x86_64-w64-mingw32-libc
%endif
%endif

%description
Headers and libraries needed to compile Windows applications on Linux

# Let's name it like Linux crosscompiles so we don't have to
# special-case everything...
%package -n cross-i686-w32-mingw32-libc
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
%rename cross-i686-w32-mingw32-libc-bootstrap
BuildArch: noarch

%description -n cross-i686-w32-mingw32-libc
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-x86_64-w64-mingw32-libc
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
%rename cross-x86_64-w64-mingw32-libc-bootstrap
BuildArch: noarch

%description -n cross-x86_64-w64-mingw32-libc
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-i686-w32-mingw32-libc-bootstrap
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
BuildArch: noarch

%description -n cross-i686-w32-mingw32-libc-bootstrap
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-x86_64-w64-mingw32-libc-bootstrap
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
BuildArch: noarch

%description -n cross-x86_64-w64-mingw32-libc-bootstrap
Basic libraries and headers needed to cross-compile Windows applications

%prep
%autosetup -p1 -n mingw-w64-v%{version}
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
TARGETS=i686-w32-mingw32
%else
TARGETS="i686-w32-mingw32 x86_64-w64-mingw32"
%endif

find . -name config.guess -o -name config.sub |while read r; do
	cp -f %{_datadir}/libtool/config/$(basename $r) $r
done

%if %{with bootstrap}
# In bootstrap mode, we only care about headers
cd mingw-w64-headers
%endif

for i in $TARGETS; do
%if ! %{with bootstrap}
	# For some reason the configure script doesn't
	# automatically use the correct cross tools
	export CC=${i}-gcc
	export CXX=${i}-g++
	export AS=${i}-as
	export AR=${i}-ar
	export RANLIB=${i}-ranlib
	export DLLTOOL=${i}-dlltool
%endif
	mkdir obj-${i}
	cd obj-${i}
	if ! ../configure --prefix=%{_prefix}/${i} --target=${i} --host=${i} --enable-experimental=all; then
		echo "Configure failed:"
		echo "================="
		for cl in `find . -name config.log`; do
			[ -e "$cl" ] || continue
			echo "*** $cl:"
			cat $cl
			echo
		done
		exit 1
	fi
	cd ..
%if ! %{with bootstrap}
	unset CC
	unset CXX
	unset AS
	unset AR
	unset RANLIB
	unset DLLTOOL
%endif
done

%if %{with bootstrap}
cd ..
%endif

# We need to build tools separately because
# we want them to be native Linux binaries,
# not using the cross compilers.
# Also, except for widl, there's no difference
# between 32-bit and 64-bit targets for those tools,
# eliminating the need for separate i686-w32-mingw32 and
# x86_64-w64-mingw32 builds
cd mingw-w64-tools
for i in *; do
	[ -e "$i/configure" ] || continue
	[ "$i" = "widl" ] && continue
	cd $i
	mkdir obj
	cd obj
	../configure --prefix=%{_prefix}
	cd ../..
done
cd widl
for i in $TARGETS; do
	mkdir obj-${i}
	cd obj-${i}
	../configure --prefix=%{_prefix} --target=${i}
	cd ..
done

%build
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
TARGETS=i686-w32-mingw32
%else
TARGETS="i686-w32-mingw32 x86_64-w64-mingw32"
%endif

%if %{with bootstrap}
# In bootstrap mode, we only care about headers
cd mingw-w64-headers
%endif
for i in $TARGETS; do
	cd obj-${i}
	%make_build -j1
	cd ..
done

%if %{with bootstrap}
cd ..
%endif

# We need to build tools separately because
# we want them to be native Linux binaries,
# not using the cross compilers.
# Also, there's no difference between 32-bit
# and 64-bit targets for those tools, eliminating
# the need for separate i686-w32-mingw32 and
# x86_64-w64-mingw32 targets
cd mingw-w64-tools
for i in *; do
	[ -e "$i/configure" ] || continue
	[ "$i" = "widl" ] && continue
	cd $i/obj
	%make_build
	cd ../..
done
cd widl
for i in $TARGETS; do
	cd obj-${i}
	%make_build
	cd ..
done

%install
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
TARGETS=i686-w32-mingw32
%else
TARGETS="i686-w32-mingw32 x86_64-w64-mingw32"
%endif

%if %{with bootstrap}
# In bootstrap mode, we only care about headers
cd mingw-w64-headers
%endif
for i in $TARGETS; do
	cd obj-${i}
	%make_install
	cd ..
done

%if %{with bootstrap}
cd ..
%endif

# We need to build tools separately because
# we want them to be native Linux binaries,
# not using the cross compilers.
# Also, there's no difference between 32-bit
# and 64-bit targets for those tools, eliminating
# the need for separate i686-w32-mingw32 and
# x86_64-w64-mingw32 targets
cd mingw-w64-tools
for i in *; do
	[ -e "$i/configure" ] || continue
	[ "$i" = "widl" ] && continue
	cd $i/obj
	%make_install
	cd ../..
done
cd widl
for i in $TARGETS; do
	cd obj-${i}
	%make_install
	cd ..
done

%files
%{_bindir}/*

%if %{with bootstrap}
%files -n cross-i686-w32-mingw32-libc-bootstrap
%else
%files -n cross-i686-w32-mingw32-libc
%{_prefix}/i686-w32-mingw32/lib/*
%endif
%{_prefix}/i686-w32-mingw32/include/*

%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
%if %{with bootstrap}
%files -n cross-x86_64-w64-mingw32-libc-bootstrap
%else
%files -n cross-x86_64-w64-mingw32-libc
%{_prefix}/x86_64-w64-mingw32/lib/*
%{_prefix}/x86_64-w64-mingw32/lib32
%endif
%{_prefix}/x86_64-w64-mingw32/include/*
%endif
