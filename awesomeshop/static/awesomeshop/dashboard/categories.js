/* Copyright 2015 Sébastien Maccagnoni-Munch
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

angular.module('dbCategories', ['slugifier'])
.config(function($stateProvider) {
    $stateProvider
        .state('categories', {
            url: '/category',
            templateUrl: 'categories',
            controller: 'CategoriesCtrl'
        })
        .state('newcategory', {
            url: '/category/new',
            templateUrl: 'category',
            controller: 'CategoryCtrl'
        })
        .state('category', {
            url: '/category/:category_id',
            templateUrl: 'category',
            controller: 'CategoryCtrl'
        })
})
.controller('CategoriesCtrl', function($scope, $http) {
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            $scope.categories = response.data;
        });
    /*
     * TODO: categories sorting

    $scope.sortoptions = {containment:'#categories-list'}
    $scope.start_sort = function(item) {
        var i = 0,
            // If in_parent_level < 9999, that means the current category is
            // a child of the category we want to move (item)
            in_parent_level = 9999,
            thislevel = 0;
        while (i < $scope.categories.length) {
                // The previous level is needed to know if a "end of level" marker
                // must be added
            var previouslevel = thislevel,
                thislevel = $scope.categories[i].level;
            if (thislevel < previouslevel) {
                $scope.categories.splice(i, 0, {
                    marker: true,
                    level: previouslevel,
                    wrongtarget: in_parent_level != 9999
                });
            }
            if ($scope.categories[i] == item) {
                // If the current category is the item, mark it as the
                // "parent level"
                in_parent_level = item.level;
            } else if (thislevel > in_parent_level) {
                // If the current category is a child of the item, mark it
                // as an inadequate target
                $scope.categories[i].wrongtarget = true;
            } else if (thislevel <= in_parent_level) {
                // If the current category is at the same level than the item
                // or at a lower level, that means we're now outside of the
                // "inadequate targets" scope
                in_parent_level = 9999;
            }
            i += 1;
        }
        $scope.categories.push({
            marker: true,
            level: thislevel,
            wrongtarget: in_parent_level != 9999
        });
    };
    function remove_markers() {
        var i = 0;
        while(i < $scope.categories.length) {
            $scope.categories[i].wrongtarget = false;
            if ($scope.categories[i].marker) {
                // Remove the markers
                $scope.categories.splice(i, 1);
            } else {
                i += 1;
            }
        }
    }
    $scope.stop_sort = function(moved) {
        if (!moved) {
            remove_markers();
        };
    };
    $scope.sort = function(from_item, to_rank) {
        console.log($scope.categories);
        remove_markers();
        console.log($scope.categories);
    }
    */
})
.controller('CategoryCtrl', function($scope, $http, $stateParams, $state, Slug, CONFIG) {
    $scope.langs = CONFIG.languages;
    $http.get('/api/category', {params: {'flat':'true'}})
        .then(function(response) {
            $scope.categories = response.data;
            $scope.categories.unshift({
                'id': '',
                'full_name': '-----'
            })
        });
    $scope.submit = function() {
        if ($scope.category.id) {
            $http.put('/api/category/'+$scope.category.id+'/edit', $scope.category)
                .then(function(response) {
                    $scope.category = response.data;
                    $scope.form.$setPristine();
                });
        } else {
            $http.post('/api/category', $scope.category)
                .then(function(response) {
                    $scope.category = response.data;
                    $scope.form.$setPristine();
                    $state.go('category', {category_id:response.data.id}, {notify:false});
                });
        };
    }
    $scope.delete = function() {
        if ($scope.category.id) {
            $http.delete('/api/category/'+$scope.category.id+'/edit')
                .then(function(response) {
                    $state.go('categories');
                });
        } else {
            $state.go('categories');
        }
    };
    $scope.slug_from = function(text) {
        $scope.category.slug = Slug.slugify(text);
    };
    if ($stateParams.category_id) {
        $http.get('/api/category/'+$stateParams.category_id+'/edit')
            .then(function(response) {
                $scope.category = response.data;
                $scope.displayable_from_id($scope, 'categories', $scope.category.parent);
            });
    } else {
        $scope.category = {};
        $scope.displayablecategories = '-----';
    }
});
