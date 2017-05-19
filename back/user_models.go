package awesomeshop

import (
	"github.com/go-bongo/bongo"

	"gopkg.in/mgo.v2/bson"
)

type userInList struct {
	ID        bson.ObjectId `json:"id" bson:"_id"`
	Carts     int           `json:"carts"`
	Email     string        `json:"email" bson:"email"`
	IsAdmin   bool          `json:"is_admin" bson:"adm"`
	Addresses int           `json:"addresses"`
}

func (u *userInList) AfterFind(c *bongo.Collection) error {
	var carts = c.Connection.Collection("cart").Find(bson.M{"user": u.ID})
	defer carts.Free()
	var addresses = c.Connection.Collection("address").Find(bson.M{"user": u.ID})
	defer addresses.Free()
	u.Carts, _ = carts.Query.Count()
	u.Addresses, _ = addresses.Query.Count()
	return nil
}

/*
type user struct {
	//bongo.DocumentBase `bson:",inline"`
	CreatedAt   time.Time `json:"created_at" bson:"create"`
	Email       string    `json:"email" bson:"email"`
	Passsalt    string    `json:"passsalt" bson:"salt"`
	Passhash    string    `json:"passhash" bson:"hash"`
	IsAdmin     bool      `json:"is_admin" bson:"adm"`
	ConfirmCode string    `json:"confirm_code" bson:"confirm"`
	Locale      string    `json:"locale" bson:"locale"`
	// TODO If possible, query the last order
	LatestDeliveryAddress   string `json:"latest_delivery_address" bson:"del_addr"`
	LatestBillingAddress    string `json:"latest_billing_address" bson:"bil_addr"`
	LatestDeliveryAsBilling bool   `json:"latest_delivery_as_billing" bson:"del_as_bil"`
	LatestCarrier           string `json:"latest_carrier" bson:"carrier"`
	LatestPayment           string `json:"latest_payment" bson:"paymt"`
	LatestReusedPackage     bool   `json:"latest_reused_package" bson:"reuse_pkg"`

			createdAt  = db.DateTimeField(db_field='create',
		                                  default=datetime.datetime.now, required=True)
		    email = db.EmailField(unique=True)
		    passsalt = db.StringField(db_field='salt')
		    passhash = db.StringField(db_field='hash')
		    is_admin = db.BooleanField(db_field='adm', default=False)
		    locale = db.StringField()
		    confirm_code = db.StringField(db_field='confirm')
		    # The following are the user's "preferences" from his latest order
		    latest_delivery_address = db.StringField(db_field='del_addr')
		    latest_billing_address = db.StringField(db_field='bil_addr')
		    latest_delivery_as_billing = db.BooleanField(db_field='del_as_bil',
		                                                 default=True)
		    latest_carrier = db.StringField(db_field='carrier')
		    latest_payment = db.StringField(db_field='paymt')
		    latest_reused_package = db.BooleanField(db_field='reuse_pkg')


}
*/
