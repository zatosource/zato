// Load client for REST and SOAP channels. Holds a number of keep-alive connections,
// sends one fixed request over each of them in a loop for a fixed duration
// and reports the number of responses per status code as JSON.

package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// The result of a run, written to standard output.
type result struct {
	Requests int64            `json:"requests"`
	Errors   int64            `json:"errors"`
	Seconds  float64          `json:"seconds"`
	Statuses map[string]int64 `json:"statuses"`
}

// Reads one HTTP/1.1 response with a Content-Length body and returns its status code.
func readResponse(reader *bufio.Reader) (int, bool, error) {

	statusLine, err := reader.ReadString('\n')
	if err != nil {
		return 0, false, err
	}

	fields := strings.SplitN(statusLine, " ", 3)
	if len(fields) < 2 {
		return 0, false, fmt.Errorf("invalid status line %q", statusLine)
	}

	status, err := strconv.Atoi(fields[1])
	if err != nil {
		return 0, false, err
	}

	contentLength := 0
	isClosing := false

	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			return 0, false, err
		}

		line = strings.TrimRight(line, "\r\n")
		if line == "" {
			break
		}

		name, value, _ := strings.Cut(line, ":")
		name = strings.ToLower(strings.TrimSpace(name))
		value = strings.TrimSpace(value)

		if name == "content-length" {
			contentLength, err = strconv.Atoi(value)
			if err != nil {
				return 0, false, err
			}
		}

		if name == "connection" {
			if strings.EqualFold(value, "close") {
				isClosing = true
			}
		}
	}

	if _, err := io.CopyN(io.Discard, reader, int64(contentLength)); err != nil {
		return 0, false, err
	}

	return status, isClosing, nil
}

func main() {
	address := flag.String("address", "127.0.0.1:17010", "host:port of the server")
	connections := flag.Int("connections", 4, "number of keep-alive connections")
	duration := flag.Duration("duration", 2*time.Second, "how long to send requests for")
	requestPath := flag.String("request", "", "file with the raw HTTP request")
	flag.Parse()

	request, err := os.ReadFile(*requestPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	var requests, errors int64
	var statusLock sync.Mutex
	statuses := map[string]int64{}

	deadline := time.Now().Add(*duration)
	start := time.Now()

	var group sync.WaitGroup

	for range *connections {
		group.Add(1)

		go func() {
			defer group.Done()

			local := map[string]int64{}

			defer func() {
				statusLock.Lock()
				for key, value := range local {
					statuses[key] += value
				}
				statusLock.Unlock()
			}()

			for time.Now().Before(deadline) {

				conn, err := net.Dial("tcp", *address)
				if err != nil {
					atomic.AddInt64(&errors, 1)
					time.Sleep(10 * time.Millisecond)
					continue
				}

				reader := bufio.NewReaderSize(conn, 65536)

				for time.Now().Before(deadline) {

					if _, err := conn.Write(request); err != nil {
						atomic.AddInt64(&errors, 1)
						break
					}

					status, isClosing, err := readResponse(reader)
					if err != nil {
						atomic.AddInt64(&errors, 1)
						break
					}

					atomic.AddInt64(&requests, 1)
					local[strconv.Itoa(status)]++

					if isClosing {
						break
					}
				}

				conn.Close()
			}
		}()
	}

	group.Wait()

	out := result{
		Requests: requests,
		Errors:   errors,
		Seconds:  time.Since(start).Seconds(),
		Statuses: statuses,
	}

	encoded, _ := json.Marshal(out)
	fmt.Println(string(encoded))
}
