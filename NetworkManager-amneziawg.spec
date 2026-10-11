%global commit      8d5221e689015df03616ac4116bc16f0939dec6d
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           NetworkManager-amneziawg
Version:        0.9.11
Release:        1.git%{shortcommit}%{?dist}
Summary:        NetworkManager VPN plugin for AmneziaWG VPN

License:        GPL-2.0-or-later
URL:            https://github.com/vovochka404/network-manager-amneziawg
Source0:        %{url}/archive/%{commit}/network-manager-amneziawg-%{shortcommit}.tar.gz

# GTK4 connection editor (GNOME Settings) and runtime GTK3/GTK4 editor selection
Patch0:         0001-feat-add-GTK4-editor-UI.patch
Patch1:         0002-feat-add-GNOME-auth-dialog-helper-for-VPN-secrets.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  gettext
BuildRequires:  intltool
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(libnm) >= 1.14
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(libnma)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libnma-gtk4)

Requires:       NetworkManager >= 1:1.14
Requires:       dbus-common
# Both backends (netlink and awg-quick) drive the kernel module, so it is
# mandatory. AWG 3.1 settings need module and tools 3.0 or newer.
Requires:       (kmod-amneziawg or akmod-amneziawg)
Recommends:     amneziawg-tools >= 3.0

%description
This package contains software for integrating AmneziaWG VPN capabilities with
NetworkManager: the service, the connection import/export plugin and the shared
core library. Supports the AmneziaWG 2.0 obfuscation parameters and the 3.1
parameters (header protection key, content padding, rekey/keepalive timings,
random trailers, disable cookies).

%package        gnome
Summary:        NetworkManager VPN plugin for AmneziaWG - GTK connection editors
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       NetworkManager-libnm%{?_isa}
Supplements:    (%{name} and gnome-shell)

%description gnome
This package contains the GTK3 and GTK4 connection editors for the
NetworkManager AmneziaWG VPN plugin, used by nm-connection-editor, GNOME
Settings and other libnma based front ends.

%prep
%autosetup -p1 -n network-manager-amneziawg-%{commit}

%build
# The tarball has no git metadata, so the CMake version detection falls back to
# its built-in default; that value only feeds CPack, which is not used here.
# DIST_VERSION is what the service reports in its startup log line.
%cmake \
    -DDIST_VERSION=%{version}-%{release} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DWITH_GTK3=ON \
    -DWITH_GTK4=ON
%cmake_build

%install
%cmake_install
%find_lang %{name}

%check
# The test suite resolves its fixtures from the source root; %%cmake runs from
# there, so run it directly instead of through the out-of-tree build dir.
%{__cmake_builddir}/nm-amneziawg-test

%files -f %{name}.lang
%license COPYING
%doc CONTRIBUTING.md README.md CHANGELOG.md
%{_libexecdir}/nm-amneziawg-service
%{_libexecdir}/nm-amneziawg-auth-dialog
%{_prefix}/lib/NetworkManager/VPN/nm-amneziawg-service.name
%{_libdir}/NetworkManager/libnm-vpn-plugin-amneziawg.so
%{_libdir}/NetworkManager/libnm-vpn-plugin-amneziawg-core.so
%{_datadir}/dbus-1/system.d/nm-amneziawg-service.conf
%{_metainfodir}/*.metainfo.xml

%files gnome
%{_libdir}/NetworkManager/libnm-vpn-plugin-amneziawg-editor.so
%{_libdir}/NetworkManager/libnm-gtk4-vpn-plugin-amneziawg-editor.so

%changelog
* Sun Oct 11 2026 Pavel Artsishevsky <polter.rnd@gmail.com> - 0.9.11-1.git8d5221e
- Add GTK4 connection editor and the GNOME auth dialog helper (now shows the stored keys)

* Sun Oct 11 2026 Pavel Artsishevsky <polter.rnd@gmail.com> - 0.9.11-0.1.git8d5221e
- Snapshot of master including AmneziaWG 3.1 import/editor/netlink support
