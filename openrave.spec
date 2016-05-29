%global octave_distpkg %{?_vendor:%_vendor}%{?!_vendor:distributions}
%global with_singleprecision %{?_with_singleprecision:1}%{?!_with_singleprecision:0}

%global commit 2baf4e38600b7540433ef05d3022d31d5f946035
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global checkout git%{shortcommit}

# filter internal openrave plugins
%global __provides_exclude_from ^%{_libdir}/openrave/plugins/.*$
%global __requires_exclude ^libconfigurationcache\.so.*$

Name:           openrave
Version:        0.9.0
Release:        15.%{checkout}%{?dist}
Summary:        Open Robotics Automation Virtual Environment

License:        LGPLv3+ and ASL 2.0
URL:            http://openrave.programmingvision.com

Source0:        https://github.com/rdiankov/openrave/archive/%{commit}/openrave-%{shortcommit}.tar.gz

# qhull changed their include path in F25
# patch created with
# grep -rIil --exclude-dir="3rdparty" "qhull/" * | \
#   xargs sed -i "s/qhull\//libqhull\//g"
Patch0:         openrave.qhull.patch
# A bug in the cmake config causes a symlink creation
# /usr/bin/openrave -> /usr/bin/openrave
# sent upstream: https://github.com/rdiankov/openrave/pull/404
Patch1:         openrave.fix-dead-symlink.patch
# Fix openrave issue #323
# This is only a workaround until upstream finds a proper fix.
Patch2:         openrave.spatialtree.patch

# The following patches are sent upstream:
# https://github.com/rdiankov/openrave/pull/403
# Parameters of the declaration and definition of the function don't match
Patch3:         openrave.fix-checkramp-parameter-mismatch.patch
# The SubParabolicSmoother's implementation is buggy and was therefore removed
# from the library librplanners. However, it was still referenced in the
# interface, causing undefined reference errors.
Patch4:         openrave.remove-subparabolicsmoother.patch
# Remove missing implementation for a function in the configuration cache.
Patch5:         openrave.fix-configurationcache-update-free-configurations.patch
Patch6:         openrave.fix-abs-paths.patch

# fails to build on arm, because of assembler instruction 'pause', which is not
# available on arm architectures
ExcludeArch: %{arm}

# models are in a separate noarch package
Requires:       %{name}-models = %{version}-%{release}

# bundled libraries
# upstream projects are dead
# convexdecomposition is taken from SVN
# no version information could be found for ivcon
Provides:       bundled(convexdecomposition) = svn3
Provides:       bundled(ivcon)

BuildRequires:  cmake
BuildRequires:  gettext
BuildRequires:  python2-devel

BuildRequires:  ann-devel
BuildRequires:  assimp-devel
BuildRequires:  boost-devel
BuildRequires:  boost-python
BuildRequires:  bullet-devel
BuildRequires:  collada-dom-devel
BuildRequires:  crlibm-devel
BuildRequires:  fparser-devel
BuildRequires:  gmp-devel
BuildRequires:  h5py
BuildRequires:  lapack-devel
BuildRequires:  libxml2-devel
BuildRequires:  minizip-devel
BuildRequires:  mpfi-devel
BuildRequires:  mpfr-devel
BuildRequires:  octave-devel
BuildRequires:  ode-devel
BuildRequires:  OpenSceneGraph-devel
BuildRequires:  OpenSceneGraph-qt-devel
BuildRequires:  pcre-devel
BuildRequires:  qhull-devel
BuildRequires:  SoQt-devel
BuildRequires:  sympy

BuildRequires:  dos2unix
BuildRequires:  doxygen
BuildRequires:  python-docutils
BuildRequires:  python-sphinx

%description
OpenRAVE is targeted for real-world autonomous robot applications, and
includes a seamless integration of 3-D simulation, visualization, planning,
scripting and control.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python2-%{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        models
Summary:        Model files for %{name}
BuildArch:      noarch

%description    models
The %{name}-models package contains model files for %{name}.


%package        doc
License:        CC-BY
Summary:        Documentation for %{name}
BuildArch:      noarch

%description    doc
The %{name}-doc package contains documentation for %{name}.


%package -n     python2-%{name}
Summary:        Python2 bindings for OpenRAVE
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       flann-python
Requires:       sympy

%description -n python2-%{name}
The python2-%{name} package contains Python2 bindings for
developing applications that use %{name}.


%package        octave
Summary:        Octave bindings for OpenRAVE
Group:          Development/Languages
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       octave(api) = %{octave_api}

%description    octave
The %{name}-octave package contains Octave bindings for
developing applications that use %{name}.


%prep
%setup -q -n %{name}-%{commit}
%if 0%{?fedora} >= 25
%patch0 -p1
%endif
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
# remove 3rd party libraries
rm -rf 3rdparty/{ann,collada-*,crlibm-*,fparser-*,flann-*,minizip,pcre-*,qhull,zlib} sympy*.tgz

%build

mkdir build
pushd build

# only add shlib dependency if it is actually used
# see https://fedoraproject.org/wiki/Common_Rpmlint_issues#unused-direct-shlib-dependency
export CXXFLAGS="%{optflags} -Wl,--as-needed"
%cmake \
  -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
  -DOPT_VIDEORECORDING=OFF \
%if %{with_singleprecision}
  -DOPT_DOUBLE_PRECISION=OFF \
%endif
  -DOPENRAVE_BIN_SUFFIX="" \
  -DOPENRAVE_LIBRARY_SUFFIX="" \
  -DOPENRAVE_SHARE_DIR:STRING="share/openrave" \
  -DOPENRAVE_SHARE_ABSOLUTE_DIR:STRING="%{_datadir}/openrave" \
  -DOPENRAVE_CMAKE_INSTALL_DIR:STRING="openrave" \
  -DOPENRAVE_DATA_INSTALL_ABSOLUTE_DIR="%{_datadir}/openrave" \
  -DOPENRAVE_PLUGINS_INSTALL_DIR="%{_libdir}/openrave/plugins" \
  -DOPENRAVE_PLUGINS_INSTALL_ABSOLUTE_DIR="%{_libdir}/openrave/plugins" \
  -DOPENRAVE_INCLUDE_INSTALL_DIR:STRING="openrave" \
  -DOPENRAVE_OCTAVE_INSTALL_DIR="%{_libexecdir}/octave/packages/openrave-%{version}" \
  -DOPENRAVE_OCTAVE_INSTALL_ABSOLUTE_DIR="%{_libexecdir}/octave/packages/openrave-%{version}" \
  -DCPACK_PACKAGE_INSTALL_DIRECTORY:STRING="openrave" \
  ..

# Having version at this level should be fine, otherwise could use:
#  -DOPENRAVE_INCLUDE_DIRNAME="openrave"

%make_build
popd

pushd docs
export rootdir=$PWD
echo "STRIP_FROM_PATH        = $rootdir
PROJECT_NUMBER = `/bin/sh ../build/openrave-config --version`
ALIASES += openraveversion=`/bin/sh ../build/openrave-config --version`
" | cat Doxyfile.html Doxyfile.en - > Doxyfile.html.en
doxygen -u Doxyfile.html.en

mkdir -p build/en
doxygen Doxyfile.html.en
rm -f build/en/coreapihtml/installdox
popd

dos2unix AUTHORS

%install
%make_install
find %{buildroot} -type f -name '*.la' -delete
# delete backup files of unclean patching
rm -rf %{buildroot}%{_datadir}/%{name}/models/barrett/.~

# Included in license tag, do not install second time
rm %{buildroot}%{_datadir}/%{name}/COPYING %{buildroot}%{_datadir}/%{name}/LICENSE.*

# Move bash completion to the right location
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions/
mv %{buildroot}%{_datadir}/%{name}/openrave_completion.bash \
  %{buildroot}%{_datadir}/bash-completion/completions/%{name}.bash

# remove openrave.bash which is used to set up paths for custom installs and is
# useless for a systemwide install
rm -f %{buildroot}%{_datadir}/%{name}/openrave.bash

# rename openrave-createplugin.py
mv %{_bindir}/openrave-createplugin.py %{_bindir}/openrave-createplugin

%find_lang %{name}
%find_lang %{name}_plugins_configurationcache
%find_lang %{name}_plugins_ikfastsolvers
%find_lang %{name}_plugins_oderave
%find_lang %{name}_plugins_rplanners

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files -f %{name}.lang -f %{name}_plugins_configurationcache.lang -f %{name}_plugins_ikfastsolvers.lang -f %{name}_plugins_oderave.lang -f %{name}_plugins_rplanners.lang
%license AUTHORS COPYING LICENSE.apache LICENSE.lgpl
%{_bindir}/openrave
%{_datadir}/bash-completion/completions/%{name}.bash
%{_libdir}/*.so.*
%{_libdir}/openrave
%dir %{_datadir}/%{name}

%files models
%license AUTHORS COPYING LICENSE.apache LICENSE.lgpl
%{_datadir}/%{name}/data
%{_datadir}/%{name}/models
%{_datadir}/%{name}/robots

%files devel
%{_bindir}/openrave-config
%{_bindir}/openrave-createplugin
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_libdir}/cmake/*
%{_datadir}/%{name}/matlab
%{_datadir}/%{name}/cppexamples

%files doc
%doc docs/build/en/coreapihtml/*

%files octave
%{_libexecdir}/octave/packages/*

%files -n python2-%{name}
%{_bindir}/openrave.py
%{_bindir}/openrave-robot.py
%{python2_sitearch}/*

%changelog
* Sun May 29 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-15.git2baf4e3
- Install locale files
- Fix absolute path defs (e.g. /usr/usr/share -> /usr/share in openrave-config)
- Remove unnecessary openrave.bash (not useful for a systemwide install)
- openrave-devel requires python2-openrave

* Wed May 25 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-14.20160519git2baf4e3
- Also compute requirements of plugins (remove __requires_exclude_from)

* Wed May 25 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-13.20160519git2baf4e3
- Add patch to remove the SubParabolicSmoother
- Add patch for missing function definition in libconfigurationcache

* Wed May 25 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-12.20160519git2baf4e3
- Add patch to fix dead symlink /usr/bin/openrave -> /usr/bin/openrave
- Add workaround patch for openrave issue #323
- Add patch for mismatching signature in function declaration/definition in
  librplanners

* Thu May 19 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-11.20160519git2baf4e3
- Add Provides: for bundled libraries

* Thu May 19 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-10.20160519git2baf4e3
- Update to newest upstream commit 2baf4e3
- Remove patches that were included upstream

* Tue May 17 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-9.20160503git0d603e2
- Exclude libconfigurationcache from the required libs
- Fix CXXFLAGS to only link against dependencies that are actually used

* Mon May 16 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-8.20160503git0d603e2
- Add patch to fix all GCC 6.1 errors
- Add patch to fix template instantiation in std::make_pair

* Wed May 11 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-7.20160503git0d603e2
- Add patch to fix qhull include path on F25

* Tue May 03 2016 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-6.20160503git0d603e2
- Update to commit 0d603e2

* Fri Jul 03 2015 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-5.20150703git9c48ee1
- Update to commit 9c48ee1
- Remove upstreamed pkgconfig patch
- Remove erroneous pyscript-permissions patch
- Fix licenses: doc is licensed under CC-BY, add license files to models subpackage

* Wed Jul 01 2015 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-4.20150624gitb32979b
- Split models into separate package

* Wed Jul 01 2015 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-3.20150624gitb32979b
- Exclude openrave plugins from Requires
- ExcludeArch arm
- Re-add minizip-devel build requirement

* Mon Jun 29 2015 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-2.20150624gitb32979b
- Clean up requirements, remove unnecessary BuildRequires and Requires
- Exclude openrave plugins from Provides
- Rename python package to python2-openrave

* Wed Jun 24 2015 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-1.20150624gitb32979b
- Update to post-release commit 32979b

* Tue Jun 02 2015 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-0.1.20150514gitb8fa1bb
- Update to commit b8fa1bb

* Sat Jun 07 2014 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-0.1.20140607gitce4a799
- Update to commit ce4a799

* Thu Oct 24 2013 Till Hofmann <hofmann@kbsg.rwth-aachen.de> - 0.9.0-0.20131211gitcc95d323
- Update to commit cc95d323

* Thu Apr 19 2012 Tim Niemueller <tim@niemueller.de> - 0.6.4-1
- Update to 0.6.4
- More patches upstreamed, only tiny sympy patch required
- Use external fparser

* Wed Jan 11 2012 Tim Niemueller <tim@niemueller.de> - 0.5.0-2
- Update to r2948 which includes upstreamed patches

* Sun Dec 04 2011 Tim Niemueller <tim@niemueller.de> - 0.5.0-1
- Update to 0.5.0

* Mon Jul 25 2011 Tim Niemueller <tim@niemueller.de> - 0.4.1-2
- Use double precision by default

* Thu Jul 21 2011 Tim Niemueller <tim@niemueller.de> - 0.4.1-1
- Update to 0.4.1 (including patch)

* Fri Apr 01 2011 Tim Niemueller <tim@niemueller.de> - 0.2.20-0.2.svn2227
- Update patch for current unavailability of BOOST_IOSTREAMS_USE_DEPRECATED

* Thu Mar 31 2011 Tim Niemueller <tim@niemueller.de> - 0.2.20-0.1.svn2227
- Update to latest trunk
- Drop upstreamed patches

* Thu Mar 31 2011 Tim Niemueller <tim@niemueller.de> - 0.2.19-0.2.svn2184
- Disable double precision
- Fix documentation generation

* Mon Mar 21 2011 Tim Niemueller <tim@niemueller.de> - 0.2.19-0.1.svn2184
- Update to latest trunk version
- Use system-wide installed collada library

* Tue Feb 08 2011 Tim Niemueller <tim@niemueller.de> - 0.2.18-0.3.svn1975
- Updated patch and added BR to use external crlibm

* Mon Jan 31 2011 Tim Niemueller <tim@niemueller.de> - 0.2.18-0.2.svn1975
- Use external flann library

* Thu Jan 27 2011 Tim Niemueller <tim@niemueller.de> - 0.2.18-0.1.svn1975
- Initial package

