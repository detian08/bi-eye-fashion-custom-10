odoo.define('pos_referral.pos_referral', function (require) {
	var models = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
	var core = require('web.core');
	var utils = require('web.utils');

	models.load_fields('res.partner',['refered_by','tier','referral_points']);

	models.load_models([
	    {
	        model: 'bonus.tier',
	        fields: ['id','name','bonus_percent'],
	        loaded: function(self,bonus_tier){ 
	            self.bonus_tier = bonus_tier; 
	        },
	    },
	]);
})