package awesomeshop

import (
	"fmt"

	"github.com/go-bongo/bongo"

	"gopkg.in/mgo.v2/bson"
)

type setting struct {
	bongo.DocumentBase `bson:",inline"`
	Name               string      `bson:"name"`
	Value              interface{} `bson:"value"`
}

func (a *Awesomeshop) getSetting(name string) interface{} {
	var (
		err         error
		settingData = &setting{}
	)
	err = a.DB.Collection("setting").FindOne(bson.M{"name": name}, settingData)
	if err != nil {
		a.Debug("[getSetting] Could not find setting ", name)
		return nil
	}
	return settingData.Value
}

func (a *Awesomeshop) setSetting(name string, value interface{}) error {
	var (
		err         error
		newerr      error
		settingData = &setting{}
	)
	// First, search if the setting already exists
	err = a.DB.Collection("setting").FindOne(bson.M{"name": name}, settingData)
	if err != nil {
		settingData.Name = name
	}
	// Then set the value and save the data (either update or create new)
	settingData.Value = value
	err = a.DB.Collection("setting").Save(settingData)
	if err != nil {
		newerr = fmt.Errorf("Could not set %s to value %v", name, value)
		a.Error(newerr, ": ", err)
		return newerr
	}
	return nil
}

func (a *Awesomeshop) getSettingInt(name string) int {
	var orig = a.getSetting(name)
	if orig == nil {
		return 0
	}
	return orig.(int)
}

func (a *Awesomeshop) getSettingString(name string) string {
	var orig = a.getSetting(name)
	if orig == nil {
		return ""
	}
	return orig.(string)
}
