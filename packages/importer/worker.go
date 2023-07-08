package importer

type (
	worker struct {
		pool       chan chan task
		r          chan task
		quitSig    chan struct{}
		stoppedSig chan struct{}
	}
)

// newWorker
func newWorker(pool chan chan task) *worker {
	w := worker{
		pool:       pool,
		r:          make(chan task, 1),
		quitSig:    make(chan struct{}),
		stoppedSig: make(chan struct{}),
	}

	go w.run()
	return &w
}

// run
func (w *worker) run() {
	defer func() {
		close(w.stoppedSig)
	}()

	for {
		w.pool <- w.r

		select {
		case r := <-w.r:
			r()
		case <-w.quitSig:
			return
		}
	}
}

// quit
func (w *worker) quit() {
	close(w.quitSig)
}

// stopped
func (w *worker) stopped() {
	<-w.stoppedSig
}
