=====================
AwesomeShop Changelog
=====================

This file summarizes the most important modifications to AwesomeShop...

+------------+---------+------------------------------------------------------+
| Date       | Type    | Subject                                              |
+============+=========+======================================================+
| 2016-07-05 | Feature | Easier navigation between shop and dashboard         |
+------------+---------+------------------------------------------------------+
| 2016-07-01 | Bugfix  | Allow creaton of categories without parents          |
+------------+---------+------------------------------------------------------+
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
* Use Beaker to cache some results
* When creating an order, do not empty the cart before the browser is
  redirected to the order page (or display a message to tell the user (s)he
  must wait)
* Toolbar on a "page" page, to easily include specific stuff in pages contents
  (``.. doc-list::``, links to other pages, images...)
* Popup on the order status, in order to identify the steps when buying a
  product
* Display slug in dashboard products list

Bugs
====

/
