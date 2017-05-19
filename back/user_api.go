package awesomeshop

import (
	"net/http"

	"github.com/labstack/echo"
	"gopkg.in/mgo.v2/bson"
)

func (a *Awesomeshop) makeUserRoutes(api *echo.Group) {
	var userAPI = a.API.Group("/user", a.LoginRequired)
	userAPI.GET("", a.getAllUsers, a.AdminRequired)
}

func (a *Awesomeshop) getAllUsers(c echo.Context) error {
	var (
		results = a.DB.Collection("user").Find(bson.M{})
		person  = &userInList{}
		people  []userInList
	)
	defer results.Free()
	for results.Next(person) {
		people = append(people, *person)
	}
	return c.JSON(http.StatusOK, people)
}
