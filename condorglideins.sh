#!/bin/bash

condor_status -p glidein.grid.iu.edu -any -const '(GlideinMyType =?= "glidefactory") && (GLIDEIN_GridType == "condor")' -af name
