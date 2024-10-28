#!/bin/bash

# Load the bash shell script
source /glade/u/apps/derecho/23.09/spack/opt/spack/lmod/8.7.24/gcc/7.5.0/c645/lmod/lmod/init/bash

# This is obtained from the derecho login node by running:
# echo "/glade/campaign/univ/ucit0011/ClimaModules-Derecho:$MODULEPATH"
export MODULEPATH="/glade/campaign/univ/ucit0011/ClimaModules-Derecho:/glade/campaign/univ/ucit0011/ClimaModules-Derecho:/glade/u/apps/derecho/modules/23.09/oneapi/2023.2.1:/glade/u/apps/derecho/modules/23.09/Core::/glade/work/nefrathe/spack-downstreams/derecho/modules/23.09/gcc/13.2.0:/glade/u/apps/derecho/modules/23.09/gcc/13.2.0:/glade/work/nefrathe/spack-downstreams/derecho/modules/23.09/cray-mpich/8.1.27/oneapi/2023.2.1:/glade/u/apps/derecho/modules/23.09/cray-mpich/8.1.27/oneapi/2023.2.1"

pbsdsh -- mkdir -p "${TMPDIR}"
