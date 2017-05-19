package awesomeshop

import (
	"bytes"
	"encoding/base64"
	"net/http"
	"time"

	"github.com/ipfans/echo-session"
	"github.com/labstack/echo"
	"golang.org/x/crypto/scrypt"
	"gopkg.in/mgo.v2/bson"
)

const (
	scryptN     = 16384
	scryptR     = 8
	scryptP     = 1
	scryptDKLen = 64
	expiryDelay = 1800 // logout after 30 minutes of inactivity
)

type (
	userAuth struct {
		ID       bson.ObjectId `json:"-" bson:"_id"`
		Email    string        `json:"email" bson:"email"`
		PassSalt []byte        `json:"-" bson:"salt"`
		PassHash []byte        `json:"-" bson:"hash"`
		IsAdmin  bool          `json:"is_admin" bson:"adm"`
		Auth     bool          `json:"auth"`
	}

	authCredentials struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}
)

// userLoader is a middleware that loads user data from current session
//
// user data can then be read with c.Get("currentUser")
//
// when not authenticated, user data is an empty userAuth instance
func (a *Awesomeshop) userLoader(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		var (
			err      error
			authData = &userAuth{}
			sess     = session.Default(c)
			uid      = sess.Get("UID")
			expiry   = sess.Get("Expiry")
		)
		if uid == nil || expiry == nil {
			// Nothing stored in the session
			a.Debug("[userLoader] UID or expiry is not provided by authentication cookie")
			sess.Delete("UID")
			sess.Delete("Expiry")
			sess.Save()
			c.Set("currentUser", &userAuth{})
			return next(c)
		}
		if !bson.IsObjectIdHex(uid.(string)) {
			a.Debug("[userLoader] Client provides ", uid.(string), " as an UID but it is not an Mongo ID")
			sess.Delete("UID")
			sess.Delete("Expiry")
			sess.Save()
			c.Set("currentUser", &userAuth{})
			return next(c)
		}
		if time.Now().Unix() > expiry.(int64) {
			a.Debug("[userLoader] Authentication cookie has expired")
			sess.Delete("UID")
			sess.Delete("Expiry")
			sess.Save()
			c.Set("currentUser", &userAuth{})
			return next(c)
		}
		err = a.DB.Collection("user").FindOne(bson.M{"_id": bson.ObjectIdHex(uid.(string))}, authData)
		if err == nil {
			a.Debug("[userLoader] Authentication cookie OK for user: ", authData.Email)
			authData.Auth = true
			c.Set("currentUser", authData)
			sess.Set("Expiry", time.Now().Unix()+expiryDelay)
			sess.Save()
			return next(c)
		}
		c.Set("currentUser", &userAuth{})
		return next(c)
	}
}

// checkLogin checks validity of an email and the associated password
//
// authentication is bypassed if the user is already authenticated from cookie
//
// if authentication succeeds, the auth cookie is created and saved.
func (a *Awesomeshop) checkLogin(email, password string, c echo.Context) bool {
	var (
		authData     = &userAuth{}
		b64candidate []byte
		candidate    []byte
		currentUser  = c.Get("currentUser")
		err          error
		sess         = session.Default(c)
	)
	if currentUser != nil && currentUser.(*userAuth).Auth == true {
		a.Debug("[checkLogin] User already logged in (from cookie)")
		return true
	}

	err = a.DB.Collection("user").FindOne(bson.M{"email": email}, authData)
	if err != nil {
		a.Debug("[checkLogin] Could not find user ", email, ": ", err)
		return false
	}
	a.Debug("[checkLogin] Found user from email: ", authData.Email)

	candidate, err = scrypt.Key([]byte(password), authData.PassSalt, scryptN, scryptR, scryptP, scryptDKLen)
	if err != nil {
		a.Debug("[checkLogin] Could not hash candidate password: ", err)
		return false
	}
	b64candidate = make([]byte, base64.StdEncoding.EncodedLen(len(candidate)))
	base64.StdEncoding.Encode(b64candidate, candidate)
	if bytes.Compare(b64candidate, authData.PassHash) == 0 {
		a.Debug("[checkLogin] Authentication succeeded for user ", authData.Email)
		sess.Set("UID", authData.ID.Hex())
		sess.Set("Expiry", time.Now().Unix()+expiryDelay)
		sess.Save()
		authData.Auth = true
		c.Set("currentUser", authData)
		return true
	}
	return false
}

// loginRequired is an authentication middleware
//
// when using thins middleware, access is denied if the user is not logged in
func (a *Awesomeshop) loginRequired(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		var (
			auth     = c.Request().Header.Get(echo.HeaderAuthorization)
			bytecred []byte
			cred     string
			err      error
			i        int
			hasAuth  bool
			realm    string
		)

		if len(auth) > 6 && auth[:6] == "Basic" {
			bytecred, err = base64.StdEncoding.DecodeString(auth[6:])
			if err != nil {
				a.Debug("[loginRequired] Could not decode basic auth credentials")
				return err
			}
			cred = string(bytecred)
			for i = 0; i < len(cred); i++ {
				if cred[i] == ':' {
					if a.checkLogin(cred[:i], cred[i+1:], c) {
						return next(c)
					}
					hasAuth = true
				}
			}
		}
		if !hasAuth {
			if a.checkLogin("", "", c) {
				return next(c)
			}
		}
		realm = a.getSettingString("shop_name")
		if realm == "" {
			realm = "Restricted"
		}
		c.Response().Header().Set(echo.HeaderWWWAuthenticate, "Basic realm="+realm)
		return echo.ErrUnauthorized
	}
}

// adminChecker is an authorization middleware
//
// when using this middleware, access is forbidden if the current user is not admin
func (a *Awesomeshop) adminRequired(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		var (
			currentUserData = c.Get("currentUser")
		)
		if currentUserData == nil {
			a.Debug("[adminRequired] No user data: is userLoader enabled?")
			return echo.ErrForbidden
		}
		if currentUserData.(*userAuth).IsAdmin {
			a.Debug("[adminRequired] User is admin, allowing access")
			return next(c)
		}
		a.Debug("[adminRequired] User is not admin, forbidding access")
		return echo.ErrForbidden
	}
}

// makeAuthRoutes creates routes related to authentication
//
// it is somewhat related to user management, because it uses user objects/data
func (a *Awesomeshop) makeAuthRoutes(api *echo.Group) {
	api.POST("/login", a.login)
	api.POST("/login", a.logout, a.loginRequired)
}

func (a *Awesomeshop) login(c echo.Context) error {
	var (
		creds = &authCredentials{}
		err   error
	)
	creds = &authCredentials{}
	err = c.Bind(creds)
	if err != nil {
		a.Debug("[login] Could not bind credentials to authCredentials struct")
		return echo.NewHTTPError(http.StatusInternalServerError)
	}
	if a.checkLogin(creds.Email, creds.Password, c) {
		return c.JSON(200, c.Get("currentUser").(*userAuth))
	}
	return c.JSON(200, &userAuth{})
}

func (a *Awesomeshop) logout(c echo.Context) error {
	var sess = session.Default(c)
	sess.Delete("UID")
	sess.Delete("Expiry")
	sess.Save()
	return c.JSON(200, &userAuth{})
}
