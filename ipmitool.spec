Name:         ipmitool
Summary:      Utility for IPMI control
Version:      1.8.11
Release:      6%{?dist}
License:      BSD
Group:        System Environment/Base
URL:          http://ipmitool.sourceforge.net/
Source0:      http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.bz2
Source1:      openipmi-ipmievd.sysconf
Buildroot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: openssl-devel readline-devel ncurses-devel
Requires(post): chkconfig
Requires(preun): chkconfig
Obsoletes: OpenIPMI-tools < 2.0.14-3
Provides: OpenIPMI-tools = 2.0.14-3

Patch1: ipmitool-1.8.10-ipmievd-init.patch
Patch2: ipmitool-1.8.10-ipmievd-condrestart.patch
Patch3: ipmitool-1.8.11-ipmieved-pidfile.patch

%description
This package contains a utility for interfacing with devices that support
the Intelligent Platform Management Interface specification.  IPMI is
an open standard for machine health, inventory, and remote power control.

This utility can communicate with IPMI-enabled devices through either a
kernel driver such as OpenIPMI or over the RMCP LAN protocol defined in
the IPMI specification.  IPMIv2 adds support for encrypted LAN
communications and remote Serial-over-LAN functionality.

It provides commands for reading the Sensor Data Repository (SDR) and
displaying sensor values, displaying the contents of the System Event
Log (SEL), printing Field Replaceable Unit (FRU) information, reading and
setting LAN configuration, and chassis power control.

%prep

%setup -q
%patch1 -p1 -b .ipmievd-init
%patch2 -p0 -b .condrestart
%patch3 -p1 -b .ipmievd-pidfile

for f in AUTHORS ChangeLog; do
    iconv -f iso-8859-1 -t utf8 < ${f} > ${f}.utf8
    mv ${f}.utf8 ${f}
done

%build
# --disable-dependency-tracking speeds up the build
# --enable-file-security adds some security checks
# --disable-intf-free disables FreeIPMI support - we don't want to depend on
#   FreeIPMI libraries, FreeIPMI has its own ipmitoool-like utility.
%configure --disable-dependency-tracking --enable-file-security --disable-intf-free
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

install -Dpm 755 contrib/ipmievd.init.redhat %{buildroot}%{_initrddir}/ipmievd
install -Dpm 644 %SOURCE1 %{buildroot}%{_sysconfdir}/sysconfig/ipmievd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add ipmievd

%preun
if [ $1 = 0 ]; then
   service ipmievd stop >/dev/null 2>&1
   /sbin/chkconfig --del ipmievd
fi

%postun
if [ "$1" -ge "1" ]; then
    service ipmievd condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/sysconfig/ipmievd
%{_initrddir}/ipmievd
%{_bindir}/*
%{_sbindir}/*
%{_mandir}/man*/*
%doc %{_datadir}/doc/ipmitool
%{_datadir}/ipmitool


%changelog
* Wed Jun  2 2010 Jan Safranek <jsafrane@redhat.com> - 1.8.11-6
- Changed ipmievd to use /var/run/ipmievd.pid file by default (#596809)

* Wed Mar  3 2010 Jan Safranek <jsafrane@redhat.com> - 1.8.11-5
- Fixed exit code of ipmievd initscript with wrong arguments (#562186)

* Fri Dec 11 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.8.11-4.1
- Rebuilt for RHEL 6

* Mon Nov  2 2009 Jan Safranek  <jsafrane@redhat.com> 1.8.11-4
- fix ipmievd initscript 'condrestart' action (#532188)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.8.11-3
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Jan Safranek <jsafrane@redhat.com> 1.8.11-1
- updated to new version

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> 1.8.10-3
- rebuild with new openssl

* Tue Oct 14 2008 Jan Safranek <jsafrane@redhat.com> 1.8.10-2
- fix issues found during package review:
  - clear Default-Start: line in the init script, the service should be 
    disabled by default
  - added Obsoletes: OpenIPMI-tools
  - compile with --disable-dependency-tracking to speed things up
  - compile with --enable-file-security
  - compile with --disable-intf-free, don't depend on FreeIPMI libraries
    (FreeIPMI has its own ipmitool-like utility)

* Mon Oct 13 2008 Jan Safranek <jsafrane@redhat.com> 1.8.10-1
- package created, based on upstream .spec file
