# TODO
# - strange error when accessing "/~watch-info":
#   [Thu Feb 10 03:16:16 2005] [warn] " 1\n\b" concurrency counter went negative; resetting to zero

%bcond_without	ipv6		# disable IPv6 support

%define		mod_name	watch
%define 	apxs		/usr/sbin/apxs1
Summary:	Apache module: Monitoring Interface for MRTG
Summary(pl):	Modu� do apache: Interfejs do monitorowania za pomoc� MRTG
Name:		apache1-mod_%{mod_name}
Version:	3.18
Release:	3
License:	BSD
Group:		Networking/Daemons
Source0:	http://www.snert.com/Software/download/mod_watch%(echo %{version} | tr -d .).tgz
# Source0-md5:	1409df800f24214bed16ca753b9967ff
Source1:	%{name}.conf
Patch0:		%{name}-PLD-v6stuff.patch
URL:		http://www.snert.com/Software/mod_watch/
BuildRequires:	%{apxs}
BuildRequires:	apache1-devel >= 1.3.33-2
#{?with_ipv6:BuildRequires:	apache1(ipv6)-devel}
Requires:	apache1 >= 1.3.33-2
Obsoletes:	apache-mod_%{mod_name} <= %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR 2>/dev/null)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR 2>/dev/null)

%description
This module will watch and collect the bytes, requests, and documents
in & out per virtual host, file owner, remote-ip address, directory or
location, and the web server as a whole. This module was designed for
use with MRTG, which will make nice graphical representations of the
data, but is general enough that it can be applied to other purposes,
as the raw data is accessed by a URL. This module supports
mod_vhost_alias and mod_gzip.

%description -l pl
Ten modu� kontroluje i zbiera informacje na temat ilo�ci przes�anych
bajt�w (przychodz�cych i wychodz�cych) wg. serwera wirtualnego, w�a�ciciela
plik�w, zdalnego adresu ip, katalogu lub lokacji oraz serwera jako ca�o�ci.
Modu� zosta� zaprojektowany do pracy z MRTG, dzi�ki czemu otrzymamy �adn�,
graficzn� reprezentacje danych. Modu� wspiera mod_vhost_alias oraz mod_gzip.

%prep
%setup -q -n mod_%{mod_name}-%{version}
%{?with_ipv6:%patch -p0}

mv mod_watch.html mod_watch_pl.html

%build
%{__make} build-dynamic \
	APXS=%{apxs}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}/conf.d}

install mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/conf.d/90_mod_%{mod_name}.conf

sed -e 's/<!--#/<!--/g' index.shtml > mod_watch.html

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/apache start\" to start apache HTTP daemon."
fi

%postun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%triggerpostun -- %{name} < 3.18-1.1
if grep -q '^Include conf\.d' /etc/apache/apache.conf; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	sed -i -e '
		/^Include.*mod_%{mod_name}\.conf/d
	' /etc/apache/apache.conf
else
	# they're still using old apache.conf
	sed -i -e '
		s,^Include.*mod_%{mod_name}\.conf,Include %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf,
	' /etc/apache/apache.conf
fi
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
fi

%files
%defattr(644,root,root,755)
%doc CHANGES* *.html
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/conf.d/*_mod_%{mod_name}.conf
%attr(755,root,root) %{_pkglibdir}/*
