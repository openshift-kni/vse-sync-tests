// SPDX-License-Identifier: GPL-2.0-or-later

package collectors //nolint:dupl // new collector

import (
	"fmt"

	"github.com/openshift-kni/vse-sync-tests/collection_tools/pkg/callbacks"
	"github.com/openshift-kni/vse-sync-tests/collection_tools/pkg/clients"
	"github.com/openshift-kni/vse-sync-tests/collection_tools/pkg/collectors/contexts"
	"github.com/openshift-kni/vse-sync-tests/collection_tools/pkg/collectors/devices"
	"github.com/openshift-kni/vse-sync-tests/collection_tools/pkg/utils"
)

const (
	PMCCollectorName = "PMC"
	PMCInfo          = "pmc-info"
)

type PMCCollector struct {
	*baseCollector

	ctx clients.ExecContext
}

func pmcPoller(pmc *PMCCollector) func() (callbacks.OutputType, error) {
	return func() (callbacks.OutputType, error) {
		return devices.GetPMC(pmc.ctx) //nolint:wrapcheck //no point wrapping this
	}
}

// Poll collects information from the cluster then
// calls the callback.Call to allow that to persist it
func (pmc *PMCCollector) Poll(resultsChan chan PollResult, wg *utils.WaitGroupCount) {
	defer wg.Done()

	errorsToReturn := make([]error, 0)

	err := pmc.poll()
	if err != nil {
		errorsToReturn = append(errorsToReturn, err)
	}

	resultsChan <- PollResult{
		CollectorName: PMCCollectorName,
		Errors:        errorsToReturn,
	}
}

// Returns a new PMCCollector based on values in the CollectionConstructor
func NewPMCCollector(constructor *CollectionConstructor) (Collector, error) {
	ctx, err := contexts.GetPTPDaemonContext(constructor.Clientset, constructor.PTPNodeName)
	if err != nil {
		return &PMCCollector{}, fmt.Errorf("failed to create PMCCollector: %w", err)
	}

	collector := &PMCCollector{
		baseCollector: newBaseCollector(
			constructor.PollInterval,
			false,
			constructor.Callback,
			PMCCollectorName,
			PMCInfo,
		),
		ctx: ctx,
	}
	collector.poller = pmcPoller(collector)

	return collector, nil
}

func init() {
	RegisterCollector(PMCCollectorName, NewPMCCollector, optional)
}
