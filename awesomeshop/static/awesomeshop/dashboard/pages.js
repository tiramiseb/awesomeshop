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

angular.module('dbPages', ['angular-sortable-view', 'angularFileUpload', 'slugifier'])
.config(function($stateProvider) {
    $stateProvider
        .state('infos', {
            url: '/infos',
            templateUrl: 'pages',
            controller: 'PagesCtrl',
            params: {
                type: 'info'
            }
        })
        .state('docs', {
            url: '/docs',
            templateUrl: 'pages',
            controller: 'PagesCtrl',
            params: {
                type: 'doc'
            }
        })
        .state('newpage', {
            url: '/:type/new',
            templateUrl: 'page',
            controller: 'PageCtrl'
        })
        .state('page', {
            url: '/page/:page_id',
            templateUrl: 'page',
            controller: 'PageCtrl'
        })
})
.controller('PagesCtrl', function($scope, $http, $stateParams) {
    $scope.pagetype = $stateParams.type;
    $scope.sortoptions = {containment:'#pages-list'}
    $scope.sort = function(from_item, to_rank) {
        var from_id = from_item.id,
            to_item = $scope.pages[to_rank+1];
        if (to_item) {
            var to_id = to_item.id;
        } else {
            var to_id = 'last';
        };
        $http.get('/api/page/'+from_id+'/move/'+to_id);
    };
    $http.get('/api/page-'+$stateParams.type)
        .then(function(response) {
            $scope.pages = response.data;
        });
})
.controller('PageCtrl', function($scope, $http, $state, $stateParams, FileUploader, Slug, CONFIG) {
    var pid = $stateParams.page_id;
    $scope.langs = CONFIG.languages;
    $scope.$state = $state;
    if (pid) {
        $scope.uploader = new FileUploader({
            url: '/api/page/'+pid+'/photo',
            autoUpload: true,
            removeAfterUpload: true
        });
        $scope.uploader.onSuccessItem = function(item, response, status, header) {
            $scope.page.photos.push(response);
        };
    }
    $scope.submit = function() {
        $http.post('/api/page', $scope.page)
            .then(function(response) {
                if (pid) {
                    $scope.page = response.data;
                } else {
                    $state.go('page', {page_id:response.data.id})
                }
            });
    }
    $scope.delete = function() {
        if (pid) {
            $http.delete('/api/page/'+pid)
                .then(function(response) {
                    $state.go($scope.page.pagetype+'s');
                });
        } else {
            $state.go($scope.page.pagetype+'s')
        }
    };
    $scope.slug_from = function(text) {
        $scope.page.slug = Slug.slugify(text);
    };
    $scope.delete_photo = function(filename, index) {
        $http.get('/api/page/'+pid+'/photo/'+filename+'/delete')
            .then(function() {
                $scope.page.photos.splice(index, 1);
            })
    }
    if (pid) {
        $http.get('/api/page/'+pid)
            .then(function(response) {
                $scope.page = response.data;
            });
    } else {
        $scope.page = {pagetype: $stateParams.type}
    };
})
