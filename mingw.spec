%bcond_without bootstrap

Name: mingw
Version: 7.0.0
Release: 1
Group: Development/Tools
Url: http://mingw-w64.org/
Source0: https://netix.dl.sourceforge.net/project/mingw-w64/mingw-w64/mingw-w64-release/mingw-w64-v%{version}.tar.bz2
Summary: Headers and libraries needed to compile Windows applications on Linux
License: Zope Public License
BuildRequires: make

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

%if %{with bootstrap}
# In bootstrap mode, we only care about headers
cd mingw-w64-headers
%endif

for i in i686-w32-mingw32 x86_64-w64-mingw32; do
	mkdir obj-${i}
	cd obj-${i}
	../configure --prefix=%{_prefix}/${i} --target=${i}
	cd ..
done

%build
%if %{with bootstrap}
# In bootstrap mode, we only care about headers
cd mingw-w64-headers
%endif
for i in i686-w32-mingw32 x86_64-w64-mingw32; do
	cd obj-${i}
	%make_build
	cd ..
done

%install
%if %{with bootstrap}
# In bootstrap mode, we only care about headers
cd mingw-w64-headers
%endif
for i in i686-w32-mingw32 x86_64-w64-mingw32; do
	cd obj-${i}
	%make_install
	cd ..
done

%files

%if %{with bootstrap}
%files -n cross-i686-w32-mingw32-libc-bootstrap
%else
%files -n cross-i686-w32-mingw32-libc
%endif
%{_prefix}/i686-w32-mingw32/include/*

%if %{with bootstrap}
%files -n cross-x86_64-w64-mingw32-libc-bootstrap
%else
%files -n cross-x86_64-w64-mingw32-libc
%endif
%{_prefix}/x86_64-w64-mingw32/include/*
