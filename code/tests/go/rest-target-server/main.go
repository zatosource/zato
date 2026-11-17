// Target endpoint of the outgoing REST measurements, and a compiled client that invokes it
// for reference figures of the endpoint itself.
//
// Server mode listens on one plain HTTP and one HTTPS address. The HTTPS certificate is issued
// at startup by a CA generated at startup, whose certificate is written to the certificate
// directory so that clients can verify against it.
//
// Client mode invokes one URL for a fixed duration with a fixed number of concurrent workers,
// and prints the call count, latency percentiles and process CPU time per call as JSON.

package main

import (
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/json"
	"encoding/pem"
	"flag"
	"fmt"
	"io"
	"log"
	"math/big"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"syscall"
	"time"
)

// The response body every successful read returns.
const itemBody = `{"id":12345,"name":"John Smith","email":"john.smith@example.com","status":"active",` +
	`"balance":1250.75,"tags":["premium","verified"],"updated":"2026-11-12T19:30:00Z"}`

// The content type of every JSON response.
const contentTypeJSON = "application/json"

// How long the issued certificates remain valid.
const certificateValidity = 24 * time.Hour

// ################################################################################################

type serverConfig struct {
	basicAuthorization  string
	staticAuthorization string
	oauthAuthorization  string
	oauthToken          string
}

// ################################################################################################

func writeItem(writer http.ResponseWriter) {
	writer.Header().Set("Content-Type", contentTypeJSON)
	_, _ = io.WriteString(writer, itemBody)
}

// ################################################################################################

func newHandler(config *serverConfig) http.Handler {
	mux := http.NewServeMux()

	// No security definition on the connection.
	mux.HandleFunc("/api/plain/item", func(writer http.ResponseWriter, request *http.Request) {
		_, _ = io.Copy(io.Discard, request.Body)
		writeItem(writer)
	})

	// HTTP Basic Auth - the exact header value is checked.
	mux.HandleFunc("/api/basic/item", func(writer http.ResponseWriter, request *http.Request) {
		_, _ = io.Copy(io.Discard, request.Body)
		if request.Header.Get("Authorization") != config.basicAuthorization {
			http.Error(writer, `{"error":"unauthorized"}`, http.StatusUnauthorized)
			return
		}
		writeItem(writer)
	})

	// Bearer tokens - either the static one or the one the token endpoint issues.
	mux.HandleFunc("/api/bearer/item", func(writer http.ResponseWriter, request *http.Request) {
		_, _ = io.Copy(io.Discard, request.Body)
		authorization := request.Header.Get("Authorization")
		if authorization != config.staticAuthorization && authorization != config.oauthAuthorization {
			http.Error(writer, `{"error":"unauthorized"}`, http.StatusUnauthorized)
			return
		}
		writeItem(writer)
	})

	// The server closes the connection after each response, so each call opens a new one.
	mux.HandleFunc("/api/close/item", func(writer http.ResponseWriter, request *http.Request) {
		_, _ = io.Copy(io.Discard, request.Body)
		if request.Header.Get("Authorization") != config.basicAuthorization {
			http.Error(writer, `{"error":"unauthorized"}`, http.StatusUnauthorized)
			return
		}
		writer.Header().Set("Connection", "close")
		writeItem(writer)
	})

	// The OAuth token endpoint, invoked on a token cache miss only.
	mux.HandleFunc("/oauth/token", func(writer http.ResponseWriter, request *http.Request) {
		_, _ = io.Copy(io.Discard, request.Body)
		writer.Header().Set("Content-Type", contentTypeJSON)
		body := fmt.Sprintf(`{"access_token":"%s","token_type":"Bearer","expires_in":3600}`, config.oauthToken)
		_, _ = io.WriteString(writer, body)
	})

	return mux
}

// ################################################################################################

func writePEM(path string, blockType string, der []byte) {
	file, err := os.Create(path)
	if err != nil {
		log.Fatalf("Could not create %s: %v", path, err)
	}
	defer file.Close()

	err = pem.Encode(file, &pem.Block{Type: blockType, Bytes: der})
	if err != nil {
		log.Fatalf("Could not write %s: %v", path, err)
	}
}

// ################################################################################################

func newTLSConfig(certDir string) *tls.Config {
	now := time.Now()

	// The CA ..
	caKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		log.Fatalf("Could not generate the CA key: %v", err)
	}

	caTemplate := &x509.Certificate{
		SerialNumber:          big.NewInt(1),
		Subject:               pkix.Name{CommonName: "REST Outgoing Measurement CA"},
		NotBefore:             now.Add(-time.Hour),
		NotAfter:              now.Add(certificateValidity),
		KeyUsage:              x509.KeyUsageCertSign | x509.KeyUsageCRLSign | x509.KeyUsageDigitalSignature,
		BasicConstraintsValid: true,
		IsCA:                  true,
	}

	caDER, err := x509.CreateCertificate(rand.Reader, caTemplate, caTemplate, &caKey.PublicKey, caKey)
	if err != nil {
		log.Fatalf("Could not create the CA certificate: %v", err)
	}

	caCertificate, err := x509.ParseCertificate(caDER)
	if err != nil {
		log.Fatalf("Could not parse the CA certificate: %v", err)
	}

	// .. the server certificate it issues ..
	leafKey, err := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if err != nil {
		log.Fatalf("Could not generate the server key: %v", err)
	}

	leafTemplate := &x509.Certificate{
		SerialNumber: big.NewInt(2),
		Subject:      pkix.Name{CommonName: "localhost"},
		NotBefore:    now.Add(-time.Hour),
		NotAfter:     now.Add(certificateValidity),
		KeyUsage:     x509.KeyUsageDigitalSignature,
		ExtKeyUsage:  []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		DNSNames:     []string{"localhost"},
		IPAddresses:  []net.IP{net.ParseIP("127.0.0.1")},
	}

	leafDER, err := x509.CreateCertificate(rand.Reader, leafTemplate, caCertificate, &leafKey.PublicKey, caKey)
	if err != nil {
		log.Fatalf("Could not create the server certificate: %v", err)
	}

	// .. and the CA certificate clients verify against.
	writePEM(filepath.Join(certDir, "ca.pem"), "CERTIFICATE", caDER)

	certificate := tls.Certificate{
		Certificate: [][]byte{leafDER, caDER},
		PrivateKey:  leafKey,
	}

	out := &tls.Config{Certificates: []tls.Certificate{certificate}}
	return out
}

// ################################################################################################

func runServer(httpAddr string, httpsAddr string, certDir string, config *serverConfig) {
	handler := newHandler(config)
	errorLog := log.New(io.Discard, "", 0)

	httpListener, err := net.Listen("tcp", httpAddr)
	if err != nil {
		log.Fatalf("Could not listen on %s: %v", httpAddr, err)
	}

	httpsListener, err := net.Listen("tcp", httpsAddr)
	if err != nil {
		log.Fatalf("Could not listen on %s: %v", httpsAddr, err)
	}

	tlsConfig := newTLSConfig(certDir)

	httpServer := &http.Server{Handler: handler, ErrorLog: errorLog}
	httpsServer := &http.Server{Handler: handler, ErrorLog: errorLog, TLSConfig: tlsConfig}

	go func() { _ = httpServer.Serve(httpListener) }()
	go func() { _ = httpsServer.ServeTLS(httpsListener, "", "") }()

	// The caller waits for this line before it sends the first request.
	httpPort := httpListener.Addr().(*net.TCPAddr).Port
	httpsPort := httpsListener.Addr().(*net.TCPAddr).Port
	fmt.Printf("ready %d %d\n", httpPort, httpsPort)

	select {}
}

// ################################################################################################

type clientResult struct {
	Calls        int     `json:"calls"`
	Errors       int     `json:"errors"`
	Seconds      float64 `json:"seconds"`
	CallsPerSec  float64 `json:"calls_per_sec"`
	CPUUsPerCall float64 `json:"cpu_us_per_call"`
	P50Us        float64 `json:"p50_us"`
	P99Us        float64 `json:"p99_us"`
}

// ################################################################################################

func getCPUSeconds() float64 {
	var usage syscall.Rusage
	_ = syscall.Getrusage(syscall.RUSAGE_SELF, &usage)

	user := float64(usage.Utime.Sec) + float64(usage.Utime.Usec)/1e6
	system := float64(usage.Stime.Sec) + float64(usage.Stime.Usec)/1e6

	out := user + system
	return out
}

// ################################################################################################

func percentile(sorted []time.Duration, fraction float64) float64 {
	if len(sorted) == 0 {
		return 0
	}
	index := int(float64(len(sorted)-1) * fraction)

	out := float64(sorted[index].Microseconds())
	return out
}

// ################################################################################################

func runClient(url string, authorization string, caPath string, duration time.Duration, warmup time.Duration, concurrency int) {
	transport := &http.Transport{
		MaxIdleConns:        concurrency,
		MaxIdleConnsPerHost: concurrency,
		DisableCompression:  true,
	}

	if caPath != "" {
		caPEM, err := os.ReadFile(caPath)
		if err != nil {
			log.Fatalf("Could not read %s: %v", caPath, err)
		}
		pool := x509.NewCertPool()
		pool.AppendCertsFromPEM(caPEM)
		transport.TLSClientConfig = &tls.Config{RootCAs: pool}
	}

	client := &http.Client{Transport: transport}

	invoke := func() bool {
		request, _ := http.NewRequest(http.MethodGet, url, nil)
		if authorization != "" {
			request.Header.Set("Authorization", authorization)
		}
		response, err := client.Do(request)
		if err != nil {
			return false
		}
		_, _ = io.Copy(io.Discard, response.Body)
		_ = response.Body.Close()
		return response.StatusCode == http.StatusOK
	}

	// Warm-up, so that the connections are established before the measurement starts.
	warmupEnd := time.Now().Add(warmup)
	for time.Now().Before(warmupEnd) {
		invoke()
	}

	var lock sync.Mutex
	var group sync.WaitGroup
	latencies := make([]time.Duration, 0, 1<<20)
	errors := 0

	cpuStart := getCPUSeconds()
	start := time.Now()
	end := start.Add(duration)

	for worker := 0; worker < concurrency; worker++ {
		group.Add(1)
		go func() {
			defer group.Done()
			local := make([]time.Duration, 0, 1<<16)
			localErrors := 0
			for {
				callStart := time.Now()
				isOK := invoke()
				callEnd := time.Now()
				local = append(local, callEnd.Sub(callStart))
				if !isOK {
					localErrors++
				}
				if callEnd.After(end) {
					break
				}
			}
			lock.Lock()
			latencies = append(latencies, local...)
			errors += localErrors
			lock.Unlock()
		}()
	}

	group.Wait()
	elapsed := time.Since(start).Seconds()
	cpuUsed := getCPUSeconds() - cpuStart

	sort.Slice(latencies, func(left, right int) bool { return latencies[left] < latencies[right] })

	result := clientResult{
		Calls:        len(latencies),
		Errors:       errors,
		Seconds:      elapsed,
		CallsPerSec:  float64(len(latencies)) / elapsed,
		CPUUsPerCall: cpuUsed * 1e6 / float64(len(latencies)),
		P50Us:        percentile(latencies, 0.50),
		P99Us:        percentile(latencies, 0.99),
	}

	encoded, _ := json.Marshal(result)
	fmt.Println(string(encoded))
}

// ################################################################################################

func main() {
	mode := flag.String("mode", "server", "server or client")

	httpAddr := flag.String("http-addr", "127.0.0.1:0", "plain HTTP listen address")
	httpsAddr := flag.String("https-addr", "127.0.0.1:0", "HTTPS listen address")
	certDir := flag.String("cert-dir", ".", "where the CA certificate is written")
	basicAuthorization := flag.String("basic-authorization", "", "the expected Basic Auth header value")
	staticAuthorization := flag.String("static-authorization", "", "the expected static bearer header value")
	oauthToken := flag.String("oauth-token", "", "the token the token endpoint issues")

	url := flag.String("url", "", "the URL to invoke")
	authorization := flag.String("authorization", "", "the Authorization header to send")
	caPath := flag.String("ca", "", "the CA certificate to verify against")
	duration := flag.Duration("duration", time.Second, "measurement duration")
	warmup := flag.Duration("warmup", 200*time.Millisecond, "warm-up duration")
	concurrency := flag.Int("concurrency", 1, "concurrent workers")

	flag.Parse()

	switch strings.ToLower(*mode) {
	case "server":
		config := &serverConfig{
			basicAuthorization:  *basicAuthorization,
			staticAuthorization: *staticAuthorization,
			oauthAuthorization:  "Bearer " + *oauthToken,
			oauthToken:          *oauthToken,
		}
		runServer(*httpAddr, *httpsAddr, *certDir, config)
	case "client":
		runClient(*url, *authorization, *caPath, *duration, *warmup, *concurrency)
	default:
		log.Fatalf("Unknown mode: %s", *mode)
	}
}
