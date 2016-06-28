=====================
AwesomeShop Changelog
=====================

This file summarizes the most important modifications to AwesomeShop...

+------------+---------+------------------------------------------------------+
| Date       | Type    | Subject                                              |
+============+=========+======================================================+
| 2016-06-24 | Feature | Allow the customer to cancel an order                |
+------------+---------+------------------------------------------------------+
| 2016-06-21 | Feature | Shipping fee estimation for anonymous users          |
|            |         +------------------------------------------------------+
|            |         | Display a popup when products are added to the cart  |
|            |         +------------------------------------------------------+
|            |         | KitProduct: sell multiple products at once           |
|            |         +------------------------------------------------------+
|            |         | Deal with product variable data (eg for kitproducts) |
|            +---------+------------------------------------------------------+
|            | Misc    | CHANGELOG file creation                              |
+------------+---------+------------------------------------------------------+
| 2016-06-20 | Feature | Merge cart and checkout pages                        |
|            +---------+------------------------------------------------------+
|            | Bugfix  | Use correct shipping price when weight = threshold   |
+------------+---------+------------------------------------------------------+

TODO
====

The following are ideas of features that may be implemented in AwesomeShop.

* Customize shipping delays for each product
* Remove jinja macros
* Change how translations work in order to get rid of Flask for the frontend
* "Edit" button on public pages when the user is an admin
* Send an email when an order is created
* Use Beaker to cache some results

Bugs
====

* In the dashboard, user page title is the admin email because of lastpass. find a way to make it NOT change the contents
