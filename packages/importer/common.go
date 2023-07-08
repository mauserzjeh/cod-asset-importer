package importer

import (
	"fmt"
	"log"
	"path"
	"runtime"
)

// logMsg
func logMsg(label, format string, args ...any) {
	_, file, line, _ := runtime.Caller(2)
	fileBasePath := path.Base(file)
	msg := fmt.Sprintf(format, args...)
	log.Printf("[%v] %v:%v - %v", label, fileBasePath, line, msg)
}

// errorLog
func errorLog(err error) {
	logMsg("ERROR", fmt.Sprint(err))
}

// errorLogAndReturn
func errorLogAndReturn(err error) error {
	logMsg("ERROR", fmt.Sprint(err))
	return err
}

// infoLog
func infoLog(msg string, args ...any) {
	logMsg("INFO", msg, args...)
}

// debugLog
func debugLog(msg string, args ...any) {
	logMsg("DEBUG", msg, args...)
}
