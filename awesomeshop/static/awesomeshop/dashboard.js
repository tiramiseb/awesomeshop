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
angular.module('awesomeshop', [
        // External modules
        'ngAnimate', 'ui.router', 'validation.match',
        // Common awesomeshop modules
        'authentication', 'config', 'spinner', 
        // Dashboard modules
        'dashboardUsers'
])
.config(function($interpolateProvider, $stateProvider, $urlRouterProvider, $urlMatcherFactoryProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
    $urlRouterProvider.otherwise('');
    $urlMatcherFactoryProvider.strictMode(false);
    $stateProvider
        .state('index', {
            url: '',
            templateUrl: 'index',
            controller: 'IndexCtrl'
        })
})
.controller('IndexCtrl', function() {
})
