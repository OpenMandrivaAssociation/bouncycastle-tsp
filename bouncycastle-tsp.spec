%global ver 1.46
%global archivever  jdk16-%(echo %{ver}|sed 's|\\\.||')

Summary:          TSP libraries for Bouncy Castle
Name:             bouncycastle-tsp
Version:          %{ver}
Release:          3
Group:            System/Libraries
License:          MIT
URL:              http://www.bouncycastle.org/
Source0:          http://www.bouncycastle.org/download/bctsp-%{archivever}.tar.gz
Source1:          http://repo2.maven.org/maven2/org/bouncycastle/bctsp-jdk16/%{version}/bctsp-jdk16-%{version}.pom
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:    jpackage-utils >= 1.5
Requires:         jpackage-utils >= 1.5
Requires(post):   jpackage-utils >= 1.7
Requires(postun): jpackage-utils >= 1.7
BuildArch:        noarch
BuildRequires:    bouncycastle-mail = %{version}
Requires:         bouncycastle-mail = %{version}
BuildRequires:    java-devel >= 1.6
Requires:         java >= 1.6
BuildRequires:    junit4

Provides:         bctsp = %{version}-%{release}

%description
Bouncy Castle consists of a lightweight cryptography API and is a provider 
for the Java Cryptography Extension and the Java Cryptography Architecture.
This library package offers additional classes, in particular 
generators/processors for Time Stamp Protocol (TSP), for Bouncy Castle.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Requires:       jpackage-utils

%description javadoc
API documentation for the %{name} package.

%prep
%setup -q -n bctsp-%{archivever}
mkdir src
unzip -qq src.zip -d src/
# Remove provided binaries
find . -type f -name "*.class" -exec rm -f {} \;
find . -type f -name "*.jar" -exec rm -f {} \;

%build
pushd src
  export CLASSPATH=$(build-classpath bcprov bcmail junit4)
  %javac -g -target 1.5 -encoding UTF-8 $(find . -type f -name "*.java")
  jarfile="../bctsp-%{version}.jar"
  # Exclude all */test/* , cf. upstream
  files="$(find . -type f \( -name '*.class' -o -name '*.properties' \) -not -path '*/test/*')"
  test ! -d classes && mf="" \
    || mf="`find classes/ -type f -name "*.mf" 2>/dev/null`"
  test -n "$mf" && %jar cvfm $jarfile $mf $files \
    || %jar cvf $jarfile $files
popd

%install
rm -rf $RPM_BUILD_ROOT

# install bouncy castle tsp
install -dm 755 $RPM_BUILD_ROOT%{_javadir}
install -pm 644 bctsp-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/bctsp-%{version}.jar
pushd $RPM_BUILD_ROOT%{_javadir}
  ln -sf bctsp-%{version}.jar bctsp.jar
popd
install -dm 755 $RPM_BUILD_ROOT%{_javadir}/gcj-endorsed
pushd $RPM_BUILD_ROOT%{_javadir}/gcj-endorsed
  ln -sf ../bctsp-%{version}.jar bctsp-%{version}.jar
popd

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# maven pom
install -dm 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 %{SOURCE1} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-bctsp.pom
%add_to_maven_depmap org.bouncycastle bctsp-jdk16 %{version} JPP bctsp

%check
pushd src
  export CLASSPATH=$PWD:$(build-classpath junit4 bcprov bcmail)
  for test in $(find . -name AllTests.class) ; do
    test=${test#./} ; test=${test%.class} ; test=${test//\//.}
    # TODO: failures; get them fixed and remove || :
    %java org.junit.runner.JUnitCore $test || :
  done
popd

%post
%update_maven_depmap

%postun
%update_maven_depmap

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc *.html
%{_javadir}/bctsp.jar
%{_javadir}/bctsp-%{version}.jar
%{_javadir}/gcj-endorsed/bctsp-%{version}.jar
%{_mavenpomdir}/JPP-bctsp.pom
%{_mavendepmapfragdir}/%{name}

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}/

