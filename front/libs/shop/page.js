/* Copyright 2016 Sébastien Maccagnoni
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
angular.module('shopPage', [])
.config(function($stateProvider) {
    $stateProvider
        .state('doc', {
            url: '/doc/:slug',
            templateUrl: 'shop/page.html',
            controller: 'DocCtrl',
            params: {type:'doc'},
            title: 'DOCUMENTATION'
        })
        .state('info', {
            url: '/info/:slug',
            templateUrl: 'shop/page.html',
            controller: 'DocCtrl',
            params: {type:'info'},
            title: 'INFORMATION'
        })
})
.controller('DocCtrl', function($rootScope, $scope, $stateParams, $http, title, user) {
    $scope.user = user;
    $http.get('/api/page-'+$stateParams.type+'/'+$stateParams.slug)
        .then(function(response) {
            $scope.page = response.data;
            title.set($scope.page.title);
        });
});
