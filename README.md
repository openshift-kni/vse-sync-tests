# vse-sync-tests

Monorepo for synchronization testing of PTP (Precision Time Protocol) on OpenShift clusters.
This repository consolidates the test framework, data collection tools, and report generation
into a single codebase.

## Directory Layout

```
.
├── tests/              Test specifications and reference implementations
├── postprocess/        Python modules for analyzing sync test results (vse-sync-pp)
├── testdrive/          Test runner framework
├── cmd/                Entry point scripts (e2e.sh)
├── collection_tools/   Go-based data collection tools (formerly vse-sync-collection-tools)
├── reporting/          PDF test report generation (formerly vse-sync-test-report)
├── doc/                Contributing guides and documentation
└── hack/               Build and import scripts
```

## Components

### Test Specifications (`tests/`)

Synchronization test cases organized by ITU-T standard (G.8272, G.8273.2).
Each test case directory contains a `testspec.adoc` (specification) and `testimpl.py`
(reference implementation). See [README.adoc](README.adoc) for the full test specification
documentation.

### Collection Tools (`collection_tools/`)

Go application that collects synchronization data from a running OpenShift cluster.
Connects to PTP-enabled nodes to gather DPLL, GNSS, PHC, and PTP4L data.
See [collection_tools/README.md](collection_tools/README.md).

### Post-Processing (`postprocess/`)

Python library (`vse_sync_pp`) for parsing, demuxing, analyzing, and plotting
collected synchronization data. See [postprocess/README.adoc](postprocess/README.adoc).

### Test Runner (`testdrive/`)

Python framework for executing test cases against collected data and producing
JUnit XML results.

### Report Generation (`reporting/`)

Generates PDF test reports from JUnit XML results using Asciidoctor.
See [reporting/README.md](reporting/README.md).

## Quick Start

### Container (recommended)

Build and run the full test suite in a container:

```bash
podman build -t vse-sync-test -f Containerfile .

podman run \
  -v ~/kubeconfig:/usr/vse/kubeconfig:Z \
  -v ~/data:/usr/vse/data:Z \
  vse-sync-test
```

### Local

Run the end-to-end test pipeline directly:

```bash
./cmd/e2e.sh -d 2000s ~/kubeconfig
```

Omit the kubeconfig to skip data collection and re-analyze existing data:

```bash
./cmd/e2e.sh
```

See [README.adoc](README.adoc) for detailed usage instructions including MNO
cluster support and boundary clock testing.
