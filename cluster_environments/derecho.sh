#!/bin/bash

# Load the bash shell script
source /glade/u/apps/derecho/23.09/spack/opt/spack/lmod/8.7.24/gcc/7.5.0/c645/lmod/lmod/init/bash

# Set only the essential variables
export NCAR_DEFAULT_INFOPATH="/usr/local/share/info:/usr/share/info"
export NCAR_DEFAULT_MANPATH="/usr/local/share/man:/usr/share/man"
export NCAR_DEFAULT_PATH="/usr/local/bin:/usr/bin:/sbin:/bin"
export MODULEPATH="/glade/campaign/univ/ucit0011/ClimaModules-Derecho:/glade/u/apps/derecho/modules/environment"
module load ncarenv/23.09
# This is obtained from the derecho login node by running:
# echo "/glade/campaign/univ/ucit0011/ClimaModules-Derecho:$MODULEPATH"
pbsdsh -- mkdir -p "${TMPDIR}"
