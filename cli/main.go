package main

import (
	"log"

	"github.com/osrapps/osr-console/cli/cmd"
)

func main() {
	if err := cmd.Execute(); err != nil {
		log.Fatalf("Error: %v", err)
	}
}
