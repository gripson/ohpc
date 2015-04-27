#
# spec file for package superlu
#
# Copyright (c) 2013 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

#-fsp-header-comp-begin-----------------------------

%include %{_sourcedir}/FSP_macros

# FSP convention: the default assumes the gnu toolchain and openmpi
# MPI family; however, these can be overridden by specifing the
# compiler_family and mpi_family variables via rpmbuild or other
# mechanisms.

%{!?compiler_family: %define compiler_family gnu}
%{!?mpi_family: %define mpi_family openmpi}
%{!?PROJ_DELIM:      %define PROJ_DELIM      %{nil}}

# Compiler dependencies
BuildRequires: lmod%{PROJ_DELIM} coreutils
%if %{compiler_family} == gnu
BuildRequires: gnu-compilers%{PROJ_DELIM}
Requires:      gnu-compilers%{PROJ_DELIM}
# hack to install MKL for the moment
BuildRequires: intel-compilers%{PROJ_DELIM}
%endif
%if %{compiler_family} == intel
BuildRequires: gcc-c++ intel-compilers%{PROJ_DELIM}
Requires:      gcc-c++ intel-compilers%{PROJ_DELIM}
%if 0%{?FSP_BUILD}
BuildRequires: intel_licenses
%endif
%endif

#-fsp-header-comp-end-------------------------------

# Base package name
%define pname superlu
%define PNAME %(echo %{pname} | tr [a-z] [A-Z])

Name:           %{pname}-%{compiler_family}%{PROJ_DELIM}
Summary:        A general purpose library for the direct solution of linear equations
License:        BSD-3-Clause
Group:          Development/Libraries/C and C++
Version:        4.3
Release:        0
#Source:         http://crd-legacy.lbl.gov/~xiaoye/SuperLU/superlu_4.3.tar.gz
Source:         %{pname}-%{version}.tar.gz
Source2:        README.SUSE
# PATCH-FEATURE-OPENSUSE superlu-4.3-make.patch : add compiler and build flags in make.inc
Patch:          superlu-4.3-make.patch
# PATCH-FIX-UPSTREAM superlu-4.3-include.patch : avoid implicit declaration warnings
Patch1:         superlu-4.3-include.patch
# PATCH-FIX-UPSTREAM superlu-4.3-dont-opt-away.diff
Patch2:         superlu-4.3-dont-opt-away.diff
# PATCH-FIX-OPENSUSE superlu-4.3-remove-hsl.patch [bnc#796236] 
# The Harwell Subroutine Library (HSL) routine m64ad.c have been removed
# from the original sources for legal reasons. This patch disables the inclusion of
# this routine in the library which, however, remains fully functionnal
Patch3:         superlu-4.3-disable-hsl.patch
Url:            http://crd.lbl.gov/~xiaoye/SuperLU/
BuildRequires:  tcsh
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

# Default library install path
%define install_path %{FSP_LIBS}/%{compiler_family}/%{pname}/%version

%description
SuperLU is an algorithm that uses group theory to optimize LU
decomposition of sparse matrices. It's the fastest direct solver for
linear systems that the author is aware of.

Docu can be found on http://www.netlib.org.

%prep
%setup -q -n %{pname}-%{version}
%patch -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
make lib

mkdir tmp 
(cd tmp; ar -x ../lib/libsuperlu_%{version}.a)
$(F90) -shared -Wl,-soname,libsuperlu.so.4 -o lib/libsuperlu.so tmp/*.o

%install
mkdir -p %{buildroot}%{install_path}/lib
mkdir -p %{buildroot}%{install_path}/include
install -m644 SRC/*.h %{buildroot}%{install_path}/include
install -m755 lib/libsuperlu.so %{buildroot}%{install_path}/lib/libsuperlu.so.%{version}
pushd %{buildroot}%{install_path}/lib
ln -s libsuperlu.so.%{version} libsuperlu.so.4
ln -s libsuperlu.so.4 libsuperlu.so
popd

#fix permissions
#chmod 644 MATLAB/*

# remove all build examples
#cd EXAMPLE
#make clean
#rm -rf *itersol*
#cd ..
#mv EXAMPLE examples
#cp FORTRAN/README README.fortran

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{FSP_HOME}

%changelog
