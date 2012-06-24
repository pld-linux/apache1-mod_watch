%define		mod_name	watch
%define 	apxs		/usr/sbin/apxs1
Summary:	Apache module: Monitoring Interface for MRTG
Summary(pl):	Modu� do apache: Interfejs do monitorowania za pomoc� MRTG
Name:		apache1-mod_%{mod_name}
Version:	3.18
Release:	1
License:	BSD
Group:		Networking/Daemons
Source0:	http://www.snert.com/Software/download/mod_watch%(echo %{version} | tr -d .).tgz
# Source0-md5:	1409df800f24214bed16ca753b9967ff
Source1:	%{name}.conf
Patch0:		%{name}-PLD-v6stuff.patch
URL:		http://www.snert.com/Software/mod_watch/
BuildRequires:	%{apxs}
BuildRequires:	apache1-devel
Requires(post,preun):	%{apxs}
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	apache1
Obsoletes:	apache-mod_%{mod_name} <= %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir	%(%{apxs} -q LIBEXECDIR)
%define		_sysconfdir	%(%{apxs} -q SYSCONFDIR)

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
%patch -p0

%build
%{__make} build-dynamic \
	APXS=%{apxs}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkglibdir},%{_sysconfdir}}

install mod_%{mod_name}.so $RPM_BUILD_ROOT%{_pkglibdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/mod_watch.conf

mv mod_watch.html mod_watch_pl.html
sed -e 's/<!--#/<!--/g' index.shtml > mod_watch.html

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{apxs} -e -a -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
if [ -f %{_sysconfdir}/apache.conf ] && \
    ! grep -q "^Include.*mod_watch.conf" %{_sysconfdir}/apache.conf; then
	echo "Include %{_sysconfdir}/mod_watch.conf" >> %{_sysconfdir}/apache.conf
fi
if [ -f /var/lock/subsys/apache ]; then
	/etc/rc.d/init.d/apache restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/apache start\" to start apache http daemon."
fi

%preun
if [ "$1" = "0" ]; then
	%{apxs} -e -A -n %{mod_name} %{_pkglibdir}/mod_%{mod_name}.so 1>&2
	umask 027
	grep -v "^Include.*mod_watch.conf" %{_sysconfdir}/apache.conf > \
		%{_sysconfdir}/apache.conf.tmp
	mv -f %{_sysconfdir}/apache.conf.tmp %{_sysconfdir}/apache.conf
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc CHANGES* *.html
%attr(755,root,root) %{_pkglibdir}/*
%{_sysconfdir}/mod_watch.conf
