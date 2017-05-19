package awesomeshop

import (
	"github.com/go-bongo/bongo"
	"github.com/ipfans/echo-session"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
	"github.com/labstack/gommon/log"
)

// Awesomeshop contains everything needed for a shop instance
type Awesomeshop struct {
	API           *echo.Group
	DB            *bongo.Connection
	Echo          *echo.Echo
	Debug         func(...interface{})
	Error         func(...interface{})
	AdminRequired echo.MiddlewareFunc
	LoginRequired echo.MiddlewareFunc
}

// New creates an instance of Awesomeshop
func New(mongoConn, mongoDB, apiroot string, debug bool) *Awesomeshop {
	var (
		a            = &Awesomeshop{}
		api          *echo.Group
		eko          *echo.Echo
		err          error
		sessionStore session.CookieStore
	)
	a.DB, err = bongo.Connect(&bongo.Config{
		ConnectionString: mongoConn,
		Database:         mongoDB,
	})
	if err != nil {
		log.Fatal("Could not connect to the database", err)
	}
	sessionStore = session.NewCookieStore([]byte("TEST_SECRET_KEY")) // TODO Use a parameter
	eko = echo.New()
	eko.Use(middleware.Logger())
	eko.Use(middleware.Recover())
	eko.Use(session.Sessions("AWESOMESHOP", sessionStore))
	eko.Use(a.userLoader)
	a.LoginRequired = a.loginRequired
	a.AdminRequired = a.adminRequired
	api = eko.Group(apiroot)
	a.API = api
	a.Echo = eko
	eko.Logger.SetPrefix("AwesomeShop")
	a.Debug = eko.Logger.Debug
	a.Error = eko.Logger.Error
	if debug {
		eko.Logger.SetLevel(log.DEBUG)
	} else {
		eko.Logger.SetLevel(log.WARN)
	}
	a.makeRoutes()
	return a
}

func (a *Awesomeshop) makeRoutes() {
	a.makeAuthRoutes(a.API)
	a.makeUserRoutes(a.API)
	// Todo
	//		Done
	// GET /search
	// GET /config
	// 		POST /login
	// GET /userdata
	// PUT /userdata
	// DELETE /userdata
	// GET /logout
	// PUT /setlang
	// POST /register
	// GET /register/resend
	// GET /forcelogin
	// 		GET /user
	// POST /user
	// GET /user/<user_id>
	// POST /user/<user_id>
	// DELETE /user/<user_id>
	// GET /confirm/<code>
	// page
	// GET /page
	// POST /page
	// GET /page-<page_type>
	// POST /page-<page_type>
	// GET /page/<page_id>
	// PUT /page/<page_id>
	// DELETE /page/<page_id>
	// GET /page-<page_type>/<page_slug>
	// POST /page/<page_id>/photo
	// DELETE /page/<page_id>/photo/<filename>
	// payment
	// GET /payment
	// GET /payplug/return/<order_number>
	// GET /payplug/cancel/<order_number>
	// POST /payplug/ipn/<order_number>
	// shipping
	// GET /country
	// POST /country
	// GET /country/<country_id>
	// PUT /country/<country_id>
	// DELETE /country/<country_id>
	// GET /countriesgroup
	// POST /countriesgroup
	// GET /countriesgroup/<group_id>
	// PUT /countriesgroup/<group_id>
	// DELETE /countriesgroup/<group_id>
	// GET /carrier
	// POST /carrier
	// GET /carrier/<carrier_id>
	// PUT /carrier/<carrier_id>
	// DELETE /carrier/<carrier_id>
	// GET /carrier/<country>/<int:weight>
	// GET /category
	// POST /category
	// GET /category/<category_id>/edit
	// PUT /category/<category_id>/edit
	// DELETE /category/<category_id>/edit
	// GET /category/<category_id>
	// dbcart
	// POST /cart/verify
	// GET /cart
	// POST /cart
	// GET /cart/<cart_id>
	// DELETE /cart/<cart_id>
	// order
	// GET /order/all
	// GET /order
	// POST /order
	// GET /order/<number>
	// PUT /order/<number>
	// GET /order/<number>/pay
	// GET /order/<number>/cancel
	// GET /order/<number>/invoice
	// product
	// GET /product
	// GET /product-<product_type>
	// POST /product-<product_type>
	// GET /newproducts
	// GET /product-<product_type>/<product_id>/edit
	// PUT /product-<product_type>/<product_id>/edit
	// DELETE /product-<product_type>/<product_id>/edit
	// GET /product/catslug/<category_id>/<product_slug>
	// GET /product/<product_id>
	// POST /product/<product_id>/photo
	// DELETE /product/<product_id>/photo/<filename>
	// GET /product/<product_id>/photo/<int:from_rank>/move/<int:to_rank>
	// tax
	// GET /taxrate
	// POST /taxrate
	// GET /taxrate/<tax_id>
	// PUT /taxrate/<tax_id>
	// DELETE /taxrate/<tax_id>
	// TODO GET /api should list all API routes
	//fmt.Println(a.Echo.Routes())
}

// Run starts the shop server
func (a *Awesomeshop) Run(listenOn string) {
	a.Echo.Logger.Fatal(a.Echo.Start(listenOn))
}
