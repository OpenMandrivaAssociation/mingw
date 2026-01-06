%bcond_with bootstrap

# to only build libc, a requirement to build other libraries
%bcond_without libraries

Name: mingw
Version: 13.0.0
Release: 3
Group: Development/Tools
Url: https://mingw-w64.org/
Source0: https://netix.dl.sourceforge.net/project/mingw-w64/mingw-w64/mingw-w64-release/mingw-w64-v%{version}.tar.bz2
Summary: Headers and libraries needed to compile Windows applications on Linux
License: Zope Public License
BuildRequires: make
BuildRequires: libtool-base

%if ! %{with bootstrap}
BuildRequires: cross-i686-w64-mingw32-binutils
BuildRequires: cross-i686-w64-mingw32-gcc-bootstrap
%if ! %{without libraries}
BuildRequires: cross-i686-w64-mingw32-libc
%else
BuildRequires: cross-i686-w64-mingw32-libc-bootstrap >= 13.0.0-1
%endif
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
BuildRequires: cross-x86_64-w64-mingw32-binutils
BuildRequires: cross-x86_64-w64-mingw32-gcc-bootstrap
%if ! %{without libraries}
BuildRequires: cross-x86_64-w64-mingw32-libc
%else
BuildRequires: cross-x86_64-w64-mingw32-libc-bootstrap >= 13.0.0-1
%endif
%endif
%endif

%if %{with bootstrap}
Recommends: cross-i686-w64-mingw32-libc-bootstrap
%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
Recommends: cross-x86_64-w64-mingw32-libc-bootstrap
%endif
%else
Recommends: cross-i686-w64-mingw32-libc
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
%package -n cross-i686-w64-mingw32-libc
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
%rename cross-i686-w64-mingw32-libc-bootstrap
BuildArch: noarch

%description -n cross-i686-w64-mingw32-libc
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-x86_64-w64-mingw32-libc
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
%rename cross-x86_64-w64-mingw32-libc-bootstrap
BuildArch: noarch

%description -n cross-x86_64-w64-mingw32-libc
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-i686-w64-mingw32-libc-bootstrap
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
BuildArch: noarch

%description -n cross-i686-w64-mingw32-libc-bootstrap
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-x86_64-w64-mingw32-libc-bootstrap
Summary: Basic libraries and headers needed to cross-compile Windows applications
Group: Development/Tools
BuildArch: noarch

%description -n cross-x86_64-w64-mingw32-libc-bootstrap
Basic libraries and headers needed to cross-compile Windows applications

%package -n cross-i686-w64-mingw32-winpthreads
Summary: POSIX threading APIs for mingw-w64
Group: Development/Tools
BuildArch: noarch

%description -n cross-i686-w64-mingw32-winpthreads
This library provides POSIX threading APIs for mingw-w64.

%package -n cross-x86_64-w64-mingw32-winpthreads
Summary: POSIX threading APIs for mingw-w64
Group: Development/Tools
BuildArch: noarch

%description -n cross-x86_64-w64-mingw32-winpthreads
This library provides POSIX threading APIs for mingw-w64.

%package -n cross-i686-w64-mingw32-libmangle
Summary: Name demangling for mingw-w64
Group: Development/Tools
BuildArch: noarch

%description -n cross-i686-w64-mingw32-libmangle
Libmangle is library for translating C++ symbols produced by Microsoft
Visual Studio C++ suite of tools into human readable names.

%package -n cross-x86_64-w64-mingw32-libmangle
Summary: Name demangling for mingw-w64
Group: Development/Tools
BuildArch: noarch

%description -n cross-x86_64-w64-mingw32-libmangle
Libmangle is library for translating C++ symbols produced by Microsoft
Visual Studio C++ suite of tools into human readable names.

%prep
%autosetup -p1 -n mingw-w64-v%{version}
%ifarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
TARGETS=i686-w64-mingw32
%else
TARGETS="i686-w64-mingw32 x86_64-w64-mingw32"
%endif

find . -name config.guess -o -name config.sub |while read r; do
	cp -f %{_datadir}/libtool/config/$(basename $r) $r
done

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

	case "$i" in
		x86_64-*)
		opt_lib32=--disable-lib32
		;;
		*)
		opt_lib32=
		;;
	esac

	opt_crt=--with-crt
	opt_libraries=--with-libraries=all

%if %{with bootstrap}
	opt_crt=--without-crt
	opt_libraries=--without-libraries
%endif

%if %{without libraries}
	opt_libraries=--without-libraries
%endif

	if ! ../configure --prefix=%{_prefix}/${i} --target=${i} --host=${i} \
	     --with-default-msvcrt=msvcrt ${opt_lib32} --enable-experimental=all \
	     --with-headers ${opt_crt} ${opt_libraries} --without-tools
	then
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

# We need to build tools separately because
# we want them to be native Linux binaries,
# not using the cross compilers.
# Also, except for widl, there's no difference
# between 32-bit and 64-bit targets for those tools,
# eliminating the need for separate i686-w64-mingw32 and
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
%ifarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
TARGETS=i686-w64-mingw32
%else
TARGETS="i686-w64-mingw32 x86_64-w64-mingw32"
%endif

for i in $TARGETS; do
	cd obj-${i}
	%make_build #-j1
	cd ..
done

# We need to build tools separately because
# we want them to be native Linux binaries,
# not using the cross compilers.
# Also, there's no difference between 32-bit
# and 64-bit targets for those tools, eliminating
# the need for separate i686-w64-mingw32 and
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
%ifarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
TARGETS=i686-w64-mingw32
%else
TARGETS="i686-w64-mingw32 x86_64-w64-mingw32"
%endif

for i in $TARGETS; do
	cd obj-${i}
	%make_install
	cd ..
done

# We need to build tools separately because
# we want them to be native Linux binaries,
# not using the cross compilers.
# Also, there's no difference between 32-bit
# and 64-bit targets for those tools, eliminating
# the need for separate i686-w64-mingw32 and
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
cd ../..

# Replace dummy pthread headers with winpthreads headers
for i in $TARGETS; do
for hdr in pthread.h pthread_compat.h pthread_signal.h \
           pthread_time.h pthread_unistd.h sched.h semaphore.h; do
    install -D -m644 mingw-w64-libraries/winpthreads/include/${hdr} \
            %{buildroot}%{_prefix}/${i}/include/${hdr}
done
done

%files
%{_bindir}/*

%if %{with bootstrap}
%files -n cross-i686-w64-mingw32-libc-bootstrap
%else
%files -n cross-i686-w64-mingw32-libc
%{_prefix}/i686-w64-mingw32/lib/*
# winpthreads
%if ! %{without libraries}
%exclude %{_prefix}/i686-w64-mingw32/lib/libpthread.*
%exclude %{_prefix}/i686-w64-mingw32/lib/libwinpthread.*
%endif
# libmangle
%if ! %{without libraries}
%exclude %{_prefix}/i686-w64-mingw32/lib/libmangle.*
%exclude %{_prefix}/i686-w64-mingw32/include/libmangle.h
%endif
%endif
%{_prefix}/i686-w64-mingw32/include/*

%if ! %{with bootstrap}
%if ! %{without libraries}
%files -n cross-i686-w64-mingw32-winpthreads
%{_prefix}/i686-w64-mingw32/bin/libwinpthread-1.dll
%{_prefix}/i686-w64-mingw32/lib/libpthread.*
%{_prefix}/i686-w64-mingw32/lib/libwinpthread.*

%files -n cross-i686-w64-mingw32-libmangle
%{_prefix}/i686-w64-mingw32/lib/libmangle.*
%{_prefix}/i686-w64-mingw32/include/libmangle.h
%endif
%endif

%ifnarch %{ix86}
# FIXME need to figure out why i686->x86_64 crosscompilers
# aren't working
%if %{with bootstrap}
%files -n cross-x86_64-w64-mingw32-libc-bootstrap
%else
%files -n cross-x86_64-w64-mingw32-libc
%{_prefix}/x86_64-w64-mingw32/lib/*
# winpthreads
%if ! %{without libraries}
%exclude %{_prefix}/x86_64-w64-mingw32/lib/libpthread.*
%exclude %{_prefix}/x86_64-w64-mingw32/lib/libwinpthread.*
%endif
# libmangle
%if ! %{without libraries}
%exclude %{_prefix}/x86_64-w64-mingw32/lib/libmangle.*
%exclude %{_prefix}/x86_64-w64-mingw32/include/libmangle.h
%endif
%endif
%{_prefix}/x86_64-w64-mingw32/include/*

%if ! %{with bootstrap}
%if ! %{without libraries}
%files -n cross-x86_64-w64-mingw32-winpthreads
%{_prefix}/x86_64-w64-mingw32/bin/libwinpthread-1.dll
%{_prefix}/x86_64-w64-mingw32/lib/libpthread.*
%{_prefix}/x86_64-w64-mingw32/lib/libwinpthread.*

%files -n cross-x86_64-w64-mingw32-libmangle
%{_prefix}/x86_64-w64-mingw32/lib/libmangle.*
%{_prefix}/x86_64-w64-mingw32/include/libmangle.h
%endif
%endif
%endif
