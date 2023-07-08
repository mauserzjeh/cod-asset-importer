package importer

import "sync"

type (
	task func() error

	workerPool struct {
		pool       chan chan task
		requests   chan task
		workers    []*worker
		quitSig    chan struct{}
		stoppedSig chan struct{}
		mux        sync.Mutex
	}
)

// newWorkerPool
func newWorkerPool(poolSize uint) *workerPool {
	wp := workerPool{
		pool:       make(chan chan task, poolSize),
		requests:   make(chan task),
		workers:    make([]*worker, poolSize),
		quitSig:    make(chan struct{}),
		stoppedSig: make(chan struct{}),
		mux:        sync.Mutex{},
	}

	for i := uint(0); i < poolSize; i++ {
		wp.workers[i] = newWorker(wp.pool)
	}

	go wp.start()
	return &wp
}

// start
func (wp *workerPool) start() {
	defer func() {
		close(wp.stoppedSig)
	}()

	for {
		select {
		case request := <-wp.requests:
			select {
			case w := <-wp.pool:
				w <- request
			case <-wp.quitSig:
				return
			}

		case <-wp.quitSig:
			return
		}
	}
}

// stop
func (wp *workerPool) stop() {
	close(wp.quitSig)

	<-wp.stoppedSig

	wp.mux.Lock()
	defer wp.mux.Unlock()

	for i := 0; i < len(wp.workers); i++ {
		wp.workers[i].quit()
	}

	for i := 0; i < len(wp.workers); i++ {
		wp.workers[i].stopped()
	}
}

// addTask
func (wp *workerPool) addTask(r task) {

}
