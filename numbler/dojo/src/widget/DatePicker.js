dojo.provide("dojo.widget.DatePicker");
dojo.provide("dojo.widget.DatePicker.util");
dojo.require("dojo.widget.DomWidget");
dojo.require("dojo.date");

dojo.widget.DatePicker = function(){
	dojo.widget.Widget.call(this);
	this.widgetType = "DatePicker";
	this.isContainer = false;
	// the following aliases prevent breaking people using 0.2.x
	this.months = dojo.date.months;
	this.weekdays = dojo.date.days;
	this.toRfcDate = dojo.widget.DatePicker.util.toRfcDate;
	this.fromRfcDate = dojo.widget.DatePicker.util.fromRfcDate;
	this.initFirstSaturday = dojo.widget.DatePicker.util.initFirstSaturday;
}

dojo.inherits(dojo.widget.DatePicker, dojo.widget.Widget);
dojo.widget.tags.addParseTreeHandler("dojo:datepicker");

dojo.requireAfterIf("html", "dojo.widget.html.DatePicker");

dojo.widget.DatePicker.util = new function() {
	this.months = dojo.date.months;
	this.weekdays = dojo.date.days;
	
	this.toRfcDate = function(jsDate) {
		if(!jsDate) {
			jsDate = this.today;
		}
		var year = jsDate.getFullYear();
		var month = jsDate.getMonth() + 1;
		if (month < 10) {
			month = "0" + month.toString();
		}
		var date = jsDate.getDate();
		if (date < 10) {
			date = "0" + date.toString();
		}
		// because this is a date picker and not a time picker, we treat time 
		// as zero
		return year + "-" + month + "-" + date + "T00:00:00+00:00";
	}
	
	this.fromRfcDate = function(rfcDate) {
		var tempDate = rfcDate.split("-");
		if(tempDate.length < 3) {
			return new Date();
		}
		// fullYear, month, date
		return new Date(parseInt(tempDate[0]), (parseInt(tempDate[1], 10) - 1), parseInt(tempDate[2].substr(0,2), 10));
	}
	
	this.initFirstSaturday = function(month, year) {
		if(!month) {
			month = this.date.getMonth();
		}
		if(!year) {
			year = this.date.getFullYear();
		}
		var firstOfMonth = new Date(year, month, 1);
		return {year: year, month: month, date: 7 - firstOfMonth.getDay()};
	}
}
