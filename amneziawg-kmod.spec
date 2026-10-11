%if 0%{?fedora}
%global buildforkernels akmod
%global debug_package %{nil}
%endif

%global pkgname amneziawg

Name:           %{pkgname}-kmod
Summary:        Kernel module (kmod) for %{pkgname}
Version:        3.1.20260906
Release:        1%{?dist}
License:        GPL-2.0-only

URL:            https://github.com/amnezia-vpn/amneziawg-linux-kernel-module
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{pkgname}-linux-kernel-module-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  bc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  kmodtool

# Nothing is compiled here: the build only repackages the sources as akmod-amneziawg.
# akmods itself requires the compiler and kernel-devel that the on-machine module build needs.

# kmodtool generates the akmod-amneziawg and kmod-amneziawg packages
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{pkgname} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

# kmodtool makes every akmod/kmod package require %%{pkgname}-kmod-common. In
# the wild amneziawg-tools provides it; ship it here too so the module can be
# installed on its own. It is only built for the akmod source rebuild, never
# for the per-kernel module rebuilds done by akmods on the user's machine.
%if %{undefined kernels}
%package        -n %{pkgname}-kmod-common
Summary:        Common files for the %{pkgname} kernel module
BuildArch:      noarch
Provides:       %{pkgname}-kmod-common = %{version}-%{release}

%description    -n %{pkgname}-kmod-common
Meta package satisfying the %{pkgname}-kmod-common dependency of the akmod and
kmod packages. It carries only the license of the kernel module.

%files          -n %{pkgname}-kmod-common
%license COPYING
%endif

%description
Kernel module for AmneziaWG, a WireGuard fork with traffic obfuscation (junk
packets, magic headers, custom protocol signature packets, and the 3.x header
protection, padding and timing parameters). It provides the "amneziawg" network
device driver used by amneziawg-tools and NetworkManager-amneziawg.

This source package builds the akmod, which rebuilds the module for every
installed kernel.

%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{pkgname} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%autosetup -p1 -n amneziawg-linux-kernel-module-%{version}

for kernel_version in %{?kernel_versions} ; do
    cp -a src _kmod_build_${kernel_version%%___*}
done

%build
# src/version.h hard-codes a release string that lags behind the tag. The
# kernel build bypasses src/Makefile, so hand the version over here: it is what
# /sys/module/amneziawg/version reports and what the userland feature gating
# in NetworkManager-amneziawg reads.
for kernel_version in %{?kernel_versions} ; do
    make V=1 %{?_smp_mflags} -C ${kernel_version##*___} \
        M=${PWD}/_kmod_build_${kernel_version%%___*} \
        WIREGUARD_VERSION=%{version} modules
done

%install
for kernel_version in %{?kernel_versions}; do
    install -D -m 755 _kmod_build_${kernel_version%%___*}/amneziawg.ko \
        %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/amneziawg.ko
done
%{?akmod_install}

%changelog
* Sun Oct 11 2026 Pavel Artsishevsky <polter.rnd@gmail.com> - 3.1.20260906-1
- Initial package, AmneziaWG kernel module 3.1.20260906 as akmod
