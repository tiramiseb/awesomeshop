/* Copyright 2015-2016 Sébastien Maccagnoni
 *
 * This file is part of AwesomeShop.
 *
 * AwesomeShop is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Affero General Public License as published by the
 * Free Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * AwesomeShop is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
 * details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with AwesomeShop. If not, see <http://www.gnu.org/licenses/>.
 */

angular.module('awesomeshop', [
        // External modules
        'duScroll', 'ngAnimate', 'ngStorage', 'pascalprecht.translate',
        'tmh.dynamicLocale', 'ui.bootstrap', 'ui.router',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner',
        // Shop modules
        'shopPage',
        'shopUser',
        'shopShop'
])
.config(function($locationProvider, $urlRouterProvider, $urlMatcherFactoryProvider, $translateProvider, $translatePartialLoaderProvider, tmhDynamicLocaleProvider) {
    $locationProvider.html5Mode(true);
    $urlRouterProvider.otherwise('/');
    $urlMatcherFactoryProvider.strictMode(false);
    tmhDynamicLocaleProvider.localeLocationPattern('bower_components/angular-i18n/angular-locale_{{locale}}.js');
    $translatePartialLoaderProvider.addPart('common');
    $translatePartialLoaderProvider.addPart('shop');
    $translateProvider
        .useMessageFormatInterpolation()
        .useSanitizeValueStrategy('escape')
        .useLoader('$translatePartialLoader', {urlTemplate: 'libs/locale-{part}-{lang}.json'})
        .registerAvailableLanguageKeys(langs, langs_negociation)
        .fallbackLanguage(fallback_language)
        .determinePreferredLanguage();
})
.filter('trusthtml', function($sce) {
    return $sce.trustAsHtml;
})
.filter('htmlbr', function($sce) {
    return function(input) {
        if (input) {
            return $sce.trustAsHtml(input.replace(/\n/g, '<br>'));
        };
    };
})
.factory('countries', function($http) {
    var countries;
    $http.get('/api/country')
        .then(function(response) {
            countries = response.data;
        });
    return {
        get: function() {
            return countries;
        }
    };
})
.factory('newproducts', function($http) {
    var newproducts;
    $http.get('/api/newproducts')
        .then(function(response) {
            newproducts = response.data;
        });
    return {
        get: function() {
            return newproducts;
        },
        count: function() {
            if (newproducts) {
                return newproducts.length;
            } else {
                return 0;
            };
        }
    };
})
.factory('products', function($http, $q, $httpParamSerializer, $translate) {
    var catslugs = {},
        products = {};
    function get_product(productid, data, resolve, reject) {
        var lang = $translate.use(),
            prod;
        if (products[lang] && products[lang][productid]) {
            prod = products[lang][productid][data];
        };
        if (prod) {
            resolve(angular.copy(prod));
        } else {
            if (data) {
                params = {data: data};
            } else {
                params = {};
            }
            $http.get('/api/product/'+productid, {params: params})
                .then(function(response) {
                    var prod = response.data;
                    if (!products[lang]) {
                        products[lang] = {};
                    }
                    if (!products[lang][prod.id]) {
                        products[lang][prod.id] = {};
                    };
                    products[lang][prod.id][data] = prod;
                    resolve(angular.copy(prod));
                }, reject);
        };
    };
    return {
        getid: function(productid, data, scope) {
            return $q(function(resolve, reject) {
                get_product(productid, data, resolve, reject);
            })
        },
        getcatslug: function(cat, slug, data) {
            var catslug = cat+'/'+slug;
            return $q(function(resolve, reject) {
                var productid = catslugs[catslug];
                if (productid) {
                    // This product is already known
                    get_product(productid, data, resolve, reject);
                } else {
                    // Download from the catslug
                    if (data) {
                        params = {data: data};
                    } else {
                        params = {};
                    }
                    $http.get('/api/product/catslug/'+catslug, {params: params})
                        .then(function(response) {
                            var lang = $translate.use(),
                                prod = response.data;
                            if (!products[lang]) {
                                products[lang] = {};
                            }
                            if (!products[lang][prod.id]) {
                                products[lang][prod.id] = {};
                            };
                            products[lang][prod.id][data] = prod;
                            catslugs[catslug] = prod.id;
                            get_product(prod.id, data, resolve, reject);
                        }, reject);
                };
            })
        }
    };
})
.factory('categories', function($rootScope, $http) {
    var categories,
        current_product_category;
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            categories = response.data;
        });
    $rootScope.$on('$stateChangeStart', function() {
        current_product_category = undefined;
    });
    $rootScope.$on('$stateChangeSuccess', function(event, toState, toParams) {
        if (toState.name == 'product') {
            current_product_category = toParams.category;
        };
    });
    return {
        get: function() {
            return categories;
        },
        from_current_product() {
            return current_product_category;
        }
    };
})
.factory('docs', function($http) {
    var docs;
    $http.get('/api/page-doc')
        .then(function(response) {
            docs = response.data;
        });
    return {
        get: function() {
            return docs;
        }
    };
})
.factory('infos', function($http) {
    var infos;
    $http.get('/api/page-info')
        .then(function(response) {
            infos = response.data;
        });
    return {
        get: function() {
            return infos;
        }
    };
})
.factory('user', function($rootScope, $state, $http, $uibModal, $translate, tmhDynamicLocale) {
    var user = undefined;
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        user = data;
    });
    $rootScope.$on('event:auth-anonymous', function(e, data) {
        user = data;
    });
    return {
        forcelogin: function() {
            $http.get('/api/forcelogin');
        },
        get: function() {
            return user;
        },
        set: function(data) {
            user = data;
        },
        is_admin: function() {
            if (user) {
                return user.is_admin;
            } else {
                return false;
            }
        },
        logout: function() {
            $http.get('/api/logout')
                .then(function(response) {
                    if (!response.data.auth) {
                        $rootScope.$broadcast('event:auth-anonymous');
                    };
                    $state.go('index');
                });
        },
        resend_confirmation: function() {
            $http.get('/api/register/resend');
        },
        setlang: function(lang) {
            $http.put('/api/setlang', {'lang': lang});
            $translate.use(lang);
            tmhDynamicLocale.set(lang);
        }
    }
})
.factory('savedCarts', function($rootScope, $timeout, $http, cart, user) {
    var carts;
    function get_saved_carts() {
        $http.get('/api/cart')
            .then(function(response) {
                carts = response.data;
            });
    };
    if (user.get()) {
        get_saved_carts();
    };
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        // Timeout, just to be sure it is executed after the user data is loaded
        $timeout(function() {
            get_saved_carts();
        }, 10);
    });
    return {
        get: function() {
            return carts;
        },
        add: function(cart) {
            carts.push(cart);
        },
        count: function() {
            if (carts) {
                return carts.length;
            } else {
                return '';
            };
        },
        remove: function(index) {
            $http.delete('/api/cart/'+carts[index].id)
                .then(function() {
                    carts.splice(index, 1);
                })
        }
    };
})
.factory('cart', function($rootScope, $localStorage, $http, $state, products) {
    if ($localStorage.cart) {
        // Ask the server to adjust the cart (availability and price)
        $http.post('/api/cart/verify', $localStorage.cart)
            .then(function(response) {
                $localStorage.cart = response.data;
            });
    } else {
        $localStorage.cart = [];
    };
    return {
        add: function(productid, data, quantity) {
            // Add a product to the cart
            products.getid(productid, data)
                .then(function(prod) {
                    var full_data = {
                        product: prod,
                        data: data,
                        quantity: quantity
                    };
                    for (var i=0; i<$localStorage.cart.length; i++) {
                        var cartline = $localStorage.cart[i];
                        if (cartline.product.id == prod.id &&
                            cartline.data == data) {
                                cartline.quantity += quantity;
                                $rootScope.$broadcast('cart:added', full_data);
                                return;
                        }
                    };
                    // Product was not found, adding it
                    $localStorage.cart.push(full_data);
                    $rootScope.$broadcast('cart:added', full_data);
                })
        },
        remove: function(productid, data) {
            // Completely remove the product from the cart
            for (var i=0; i<$localStorage.cart.length; i++) {
                if ($localStorage.cart[i].product.id == productid &&
                    $localStorage.cart[i].data == data) {
                        $localStorage.cart.splice(i, 1);
                        break;
                };
            };
        },
        load: function(cart, do_not_verify) {
            // Load a stored cart in the live cart
            // do_not_verify = False, ask the server to confirm the quantity in cart
            if (do_not_verify) {
                // Used to verify the current live cart
                $localStorage.cart = cart;
            } else {
                $http.post('/api/cart/verify', cart)
                    .then(function(response) {
                        $localStorage.cart = response.data;
                        $rootScope.$broadcast('cart:loaded', response.data);
                    });
            };
        },
        quantity: function(product) {
            // Return the quantity in stock for a product
            if (product) { // product may be undefined, before it is loaded
                for (var i=0; i<$localStorage.cart.length; i++) {
                    if ($localStorage.cart[i].product.id == product.id) {
                        return $localStorage.cart[i].quantity;
                    };
                };
            };
            return 0;
        },
        total: function() {
            // Calculate the total amount of the cart
            var amount = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var cartline = $localStorage.cart[i];
                amount += cartline.quantity * parseFloat(cartline.product.net_price);
            }
            return amount;
        },
        weight: function() {
            // Calculate the total weight of the cart
            var weight = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var cartline = $localStorage.cart[i];
                weight += cartline.quantity * cartline.product.weight;
            }
            return weight;
        },
        count: function() {
            // Count the number of products in the cart
            var count = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var cartline = $localStorage.cart[i];
                // First, check and adjust the quantity
                if (!cartline.quantity) {
                    cartline.quantity = 1;
                } else if (cartline.quantity > cartline.product.stock && cartline.product.overstock_delay >= 0) {
                    // Reduce quantity to stock if overstock is not allowed
                    cartline.quantity = cartline.product.stock;
                };
                count += cartline.quantity;
            }
            return count;
        },
        reset: function() {
            // Empty the cart and go back to the index
            $localStorage.cart = [];
            $state.go('index');
        },
        empty: function() {
            // Empty the cart;
            $localStorage.cart = [];
        },
        list: function() {
            // Return the whole cart data
            return $localStorage.cart;
        },
        overstock: function() {
            // Is any product in the cart to be ordered on demand
            for (var i=0; i<$localStorage.cart.length; i++) {
                var cartline = $localStorage.cart[i];
                if (cartline.product.overstock_delay >= 0 && cartline.product.stock < cartline.quantity) {
                    // If the stock is not sufficient for a single "not
                    // overstock" product, the whole cart is marked as "not in
                    // stock"
                    return true;
                };
            };
            return false;
        },
        delay: function() {
            // Delay for the whole cart
            var delay = 0;
            for (var i=0; i<$localStorage.cart.length; i++) {
                var product = $localStorage.cart[i].product;
                if (product.stock < $localStorage.cart[i].quantity) {
                    if (product.overstock_delay >= 0 && delay !== false) {
                        delay = Math.max(product.overstock_delay, delay);
                    } else {
                        delay = false;
                    }
                } else if (delay !== false) {
                    delay = Math.max(product.delay, delay);
                };
            };
            return delay;
        }
    }
})
.factory('orders', function($rootScope, $http, $timeout, user) {
    var orders;
    function get_orders() {
        $http.get('/api/order')
            .then(function(response) {
                orders = response.data;
            });
    };
    if (user.get()) {
        get_orders();
    };
    $rootScope.$on('event:auth-loginConfirmed', function(e, data) {
        // Timeout, just to be sure it is executed after the user data is loaded
        $timeout(function() {
            get_orders();
        }, 10);
    });
    return {
        count: function() {
            if (orders) {
                return orders.length;
            } else {
                return '';
            };
        },
        get: function() {
            return orders;
        },
        add: function(order) {
            orders.push(order);
        }
    }

})
.factory('title', function($translate) {
    var title;
    $translate('HOME').then(function(trans) {
        title = trans;
    });
    return {
        set: function(newtitle) {
            title = newtitle;
        },
        get: function() {
            return title;
        }
    }
})
.run(function($timeout, $rootScope, $document, $translate, title, CONFIG) {
    $rootScope.$on('$stateChangeSuccess', function(event, toState) {
        if (toState.title) {
            // Without this timeout, the history is scrambled
            $timeout(function() {
                $translate(toState.title).then(function(newtitle) {
                    title.set(newtitle);
                })
            }, 0);
        };
        $document.scrollTop(0,300);
    });
    $rootScope.CONFIG = CONFIG;
    $rootScope.get_current_language = function() {
        return $translate.use();
    }
    $rootScope.languages = languages;
})
.directive('productsList', function() {
    return {
        restrict: 'E',
        scope: {
            products: '=products'
        },
        templateUrl: 'shop/productslist.html'
    };
})
.controller('TitleCtrl', function($scope, $translate, title, CONFIG) {
    $scope.title = title;
    $scope.shop_name = CONFIG.shop_name;
    $scope.shop_description = CONFIG.shop_description;
})
.controller('UserCtrl', function($scope, user, savedCarts, orders) {
    $scope.user = user;
    $scope.saved_carts = savedCarts;
    $scope.orders = orders;
})
.controller('NewProductsCtrl', function($scope, newproducts) {
    $scope.newproducts = newproducts;
})
.controller('CategoriesListCtrl', function($scope, categories, newproducts) {
    $scope.categories = categories;
    $scope.newproducts = newproducts;
})
.controller('DocsListCtrl', function($scope, docs) {
    $scope.docs = docs;
})
.controller('InfosListCtrl', function($scope, infos) {
    $scope.infos = infos;
})
.controller('SearchFormCtrl', function($scope, $state) {
    $scope.search = function() {
        $state.go('search', {'q': $scope.terms});
    }
})
