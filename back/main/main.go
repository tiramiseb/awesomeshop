package main

import (
	"github.com/tiramiseb/awesomeshop/back"
	"gopkg.in/alecthomas/kingpin.v2"
)

var (
	standalone = kingpin.Flag("standalone", "Serve the web root").Short('s').Bool()
	mongoConn  = kingpin.Flag("db-connection", "MongoDB connection string").Short('d').Default("localhost").String()
	mongoDB    = kingpin.Flag("database", "MongoDB database name").Short('b').Default("awesomeshop").String()
	listenOn   = kingpin.Flag("listen", "[IP]:port where to listen").Short('l').Default(":5000").String()
	debug      = kingpin.Flag("debug", "Enable the debug (verbose) output").Short('v').Bool()
)

func main() {
	var (
		apiroot string
		shop    *awesomeshop.Awesomeshop
	)
	kingpin.CommandLine.HelpFlag.Short('h')
	kingpin.Parse()
	if *standalone {
		apiroot = "/api"
	} else {
		apiroot = ""
	}

	shop = awesomeshop.New(*mongoConn, *mongoDB, apiroot, *debug)
	shop.Run(*listenOn)
}
