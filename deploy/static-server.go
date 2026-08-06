package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

func main() {
	addr := flag.String("addr", "0.0.0.0:44117", "listen address")
	root := flag.String("root", ".", "static export directory")
	flag.Parse()

	info, err := os.Stat(*root)
	if err != nil {
		log.Fatalf("static root is unavailable: %v", err)
	}
	if !info.IsDir() {
		log.Fatalf("static root is not a directory: %s", *root)
	}

	files := http.FileServer(http.Dir(*root))
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		path := r.URL.Path
		if path == "/healthz" {
			w.Header().Set("Cache-Control", "no-store")
			w.Header().Set("Content-Type", "text/plain; charset=utf-8")
			w.WriteHeader(http.StatusOK)
			_, _ = w.Write([]byte("ok\n"))
			return
		}

		w.Header().Set("X-Content-Type-Options", "nosniff")
		ext := strings.ToLower(filepath.Ext(path))
		switch {
		case path == "/" || strings.HasSuffix(path, "/") || ext == ".html":
			w.Header().Set("Cache-Control", "no-cache")
		case strings.HasPrefix(path, "/_next/static/"):
			w.Header().Set("Cache-Control", "public, max-age=31536000, immutable")
		default:
			w.Header().Set("Cache-Control", "public, max-age=86400")
		}
		files.ServeHTTP(w, r)
	})

	server := &http.Server{
		Addr:              *addr,
		Handler:           handler,
		ReadHeaderTimeout: 10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	log.Printf("serving %s on http://%s", *root, *addr)
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatal(fmt.Errorf("static server stopped: %w", err))
	}
}
